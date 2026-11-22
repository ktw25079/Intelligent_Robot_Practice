"""Check the published final bundle against sources and recorded evidence; no ROS."""
import ast
import json
import math
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class RecordedRunTests(unittest.TestCase):
    def test_bundle_contains_same_mission_and_geometry(self):
        bundle = ast.parse((ROOT / 'submission/pick_demo_202302200.py').read_text())
        for filename, names in [('pick_demo_202302200.py', ['Mission']), ('mission_geometry.py', ['Grid', 'tip', 'wrap', 'transform_pose'])]:
            source = ast.parse((ROOT / 'scripts' / filename).read_text())
            for name in names:
                original = next(n for n in source.body if getattr(n, 'name', None) == name)
                bundled = next(n for n in bundle.body if getattr(n, 'name', None) == name)
                self.assertEqual(ast.dump(original), ast.dump(bundled), name)

    def test_embedded_configuration_matches_final_record(self):
        tree = ast.parse((ROOT / 'submission/pick_demo_202302200.py').read_text())
        value = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'RECORDED_CONFIG_JSON' for t in n.targets))
        self.assertEqual(json.loads(value), json.loads((ROOT / 'mission_config/continuous_20261120.json').read_text()))

    def test_log_sequence_and_reported_distances(self):
        events = [json.loads(line) for line in (ROOT / 'results/continuous_run_11.log').read_text().splitlines()]
        stages = list(dict.fromkeys(e['phase'] for e in events if e['phase'] != 'preflight'))
        self.assertEqual(stages, ['1_approach', '2_lower', '3_grasp', '4_lift', '5_transfer', '6_place_retreat'])
        self.assertTrue(events[-1]['completed'])
        self.assertEqual(sum(e['event'] == 'mission_start' for e in events), 1)
        self.assertFalse(any(e['event'] == 'mission_stopped' for e in events))
        result = json.loads((ROOT / 'results/continuous_run_11_result.json').read_text())
        config = json.loads((ROOT / 'mission_config/continuous_20261120.json').read_text())
        arrival = next(e['pose'] for e in events if e['event'] == 'navigation_complete' and e['phase'] == '5_transfer')
        self.assertAlmostEqual(math.dist(arrival[:2], config['B'][:2]), result['B_error_m'])
        retreat = next(e['distance'] for e in events if e['event'] == 'retreat_complete')
        self.assertAlmostEqual(retreat, result['retreat_m'])

if __name__ == '__main__':
    unittest.main()
