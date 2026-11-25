"""Summarize saved navigation and manipulation logs without ROS or robot access."""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_log(relative):
    path = ROOT / relative
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()], {
        'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def one(rows, **fields):
    matches = [r for r in rows if all(r.get(k) == v for k, v in fields.items())]
    if len(matches) != 1:
        raise ValueError(f'Expected one event for {fields}, found {len(matches)}')
    return matches[0]


def navigation():
    runs = []
    for filename in ('no_obstacle_01', 'with_obstacle_04'):
        rows, source = read_log(f'mission3/results/logs/{filename}.jsonl')
        goals = []
        for goal in ('A', 'B'):
            sent = one(rows, event='goal_sent', goal=goal)
            result = one(rows, event='goal_result', goal=goal)
            seconds = (datetime.fromisoformat(result['utc']) - datetime.fromisoformat(sent['utc'])).total_seconds()
            if seconds < 0:
                raise ValueError('Negative goal duration')
            goals.append({'goal': goal, 'sent_utc': sent['utc'], 'result_utc': result['utc'],
                          'elapsed_s': seconds, 'result': result['result']})
        runs.append({'source': source, 'goals': goals})
    return {'timing_basis': 'goal_sent to goal_result; includes action handling',
            'scope': 'One saved run per condition; not repeated-trial statistics or a controlled performance comparison.',
            'runs': runs}


def manipulation():
    rows, source = read_log('appendix/mobile_pick_place/results/continuous_run_11.log')
    start = one(rows, event='mission_start')['time']
    previous = start
    stages = []
    boundaries = [
        ('1_approach', {'event': 'arm_complete', 'name': 'approach'}),
        ('2_lower', {'event': 'floor_reference'}),
        ('3_grasp', {'event': 'gripper_complete'}),
        ('4_lift', {'event': 'lift_verified'}),
        ('5_transfer', {'event': 'navigation_complete'}),
        ('6_place_retreat', {'event': 'six_stage_complete'}),
    ]
    for phase, fields in boundaries:
        end = one(rows, phase=phase, **fields)
        elapsed = end['time'] - previous
        if elapsed < 0:
            raise ValueError('Non-monotonic milestone time')
        stages.append({'phase': phase, 'end_event': fields,
                       'start_offset_s': round(previous-start, 6),
                       'end_offset_s': round(end['time']-start, 6),
                       'elapsed_s': round(elapsed, 6)})
        previous = end['time']
    return {'source': source,
            'timing_basis': 'mission_start then consecutive stage-completion milestones; includes transitions and waits',
            'scope': 'One saved run; timestamps are log wall-clock times, not synchronized video times.',
            'stages': stages, 'total_s': round(previous-start, 6),
            'near_goal_relocalization_count': sum(r['event']=='near_goal_relocalization' for r in rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare stored summaries without writing files')
    args = parser.parse_args()
    outputs = {'mission3/results/navigation_timing.json': navigation(),
               'appendix/mobile_pick_place/results/run11_timing.json': manipulation()}
    for relative, data in outputs.items():
        path = ROOT / relative
        if args.check:
            if json.loads(path.read_text()) != data:
                raise SystemExit(f'MISMATCH: {relative}')
            print(f'PASS: {relative}')
        else:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
            print(relative)


if __name__ == '__main__':
    main()
