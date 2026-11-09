#!/usr/bin/env python3
"""Check tracked documentation and saved evidence without starting ROS or hardware."""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import struct
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LABS = ('week02', 'week03', 'mission1', 'mission2', 'week06', 'week07', 'week08', 'week09')
SNAPSHOT = 'mission2/workspaces/'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tracked_files():
    output = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT)
    return {p for p in output.decode().split('\0') if p}


def managed(name):
    return not name.startswith(SNAPSHOT) or name == SNAPSHOT + 'README.md'


def check_link(source, target, tracked):
    target = target.strip('<>')
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return
    path = (source.parent / unquote(parsed.path)).resolve()
    require(path.is_relative_to(ROOT), f'{source}: link escapes repository: {target}')
    require(path.exists(), f'{source}: missing link: {target}')
    rel = path.relative_to(ROOT).as_posix()
    present = rel in tracked if path.is_file() else any(n.startswith(rel + '/') for n in tracked)
    require(present, f'{source}: link points to untracked content: {target}')


def inspect_file(name, tracked, counts):
    p = ROOT / name
    if p.is_symlink():
        return
    suffix = p.suffix.lower()
    if suffix == '.md' and managed(name):
        text = p.read_text()
        links = re.findall(r'\]\(([^)]+)\)', text)
        links += re.findall(r'(?:src|href)=["\']([^"\']+)["\']', text)
        for target in links:
            check_link(p, target, tracked)
        counts['markdown_files'] += 1
        counts['link_references'] += len(links)
    if not managed(name):
        return
    if suffix == '.py':
        ast.parse(p.read_text(), filename=name)
        counts['python_files'] += 1
    elif suffix == '.sh':
        subprocess.run(['bash', '-n', str(p)], check=True, capture_output=True)
        counts['shell_files'] += 1
    elif suffix == '.json':
        json.loads(p.read_text())
        counts['json_files'] += 1
    elif suffix in ('.xml', '.urdf', '.svg'):
        ET.parse(p)
        counts['xml_files'] += 1
    elif suffix in ('.png', '.jpg', '.jpeg', '.pdf'):
        data = p.read_bytes()
        if suffix == '.png':
            require(data[:8] == b'\x89PNG\r\n\x1a\n', f'{name}: invalid PNG signature')
            width, height = struct.unpack('>II', data[16:24])
            require(width > 0 and height > 0, f'{name}: invalid image dimensions')
        elif suffix in ('.jpg', '.jpeg'):
            require(data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9'), f'{name}: invalid JPEG markers')
        else:
            require(data.startswith(b'%PDF-'), f'{name}: invalid PDF signature')
        counts['image_pdf_files'] += 1
    elif suffix == '.zip':
        with zipfile.ZipFile(p) as archive:
            require(archive.testzip() is None, f'{name}: ZIP CRC failure')
        counts['zip_files'] += 1


def check_snapshot(counts):
    base = ROOT / SNAPSHOT
    for line in (base / 'SHA256SUMS').read_text().splitlines():
        digest, filename = line.split(maxsplit=1)
        p = base / filename.lstrip('*')
        require(hashlib.sha256(p.read_bytes()).hexdigest() == digest, f'Snapshot changed: {p}')
        counts['snapshot_hashes'] += 1


def check_bag(counts):
    base = ROOT / 'week08/results/aruco_bag'
    db = base / 'aruco_bag_0.db3'
    with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True) as conn:
        require(conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok', 'rosbag SQLite integrity failure')
        observed = dict(conn.execute('SELECT topics.name, COUNT(messages.id) FROM topics LEFT JOIN messages ON topics.id=messages.topic_id GROUP BY topics.id'))
    text = (base / 'metadata.yaml').read_text()
    expected = {name: int(n) for name, n in re.findall(r'name: (\S+).*?message_count: (\d+)', text, re.S)}
    total = int(re.search(r'^  message_count: (\d+)', text, re.M).group(1))
    require(observed == expected and sum(observed.values()) == total, 'rosbag metadata/count mismatch')
    counts['bag_messages'] = total


def check_map(counts):
    base = ROOT / 'week09/results'
    meta = (base / 'map.yaml').read_text()
    image = re.search(r'^image: (.+)$', meta, re.M).group(1).strip()
    resolution = float(re.search(r'^resolution: (.+)$', meta, re.M).group(1))
    data = (base / image).read_bytes()
    header = re.match(rb'P5\s+(?:#[^\n]*\n\s*)*(\d+)\s+(\d+)\s+(\d+)[\r]?\n', data)
    require(header is not None, 'Expected binary PGM P5 with a valid header')
    width, height, maximum = map(int, header.groups())
    require(maximum == 255 and len(data[header.end():]) == width * height, 'PGM pixel count mismatch')
    evidence = json.loads((base / 'verification.json').read_text())
    require([width, height] == evidence['map_size_cells'], 'Map dimensions differ from verification record')
    require(resolution == evidence['resolution_m_per_cell'], 'Map resolution differs from verification record')
    counts['map_cells'] = width * height


def main():
    tracked = tracked_files()
    counts = Counter()
    failures = []
    for lab in LABS:
        try:
            require(f'{lab}/README.md' in tracked, f'{lab}: README missing')
            for folder in ('screenshots', 'results'):
                require(any(n.startswith(f'{lab}/{folder}/') for n in tracked), f'{lab}: {folder} missing')
            require(any(n.startswith(lab + '/') and n.endswith(('.py', '.cpp', '.sh', '.urdf')) for n in tracked), f'{lab}: code missing')
        except ValueError as error:
            failures.append(str(error))
    for name in sorted(tracked):
        try:
            inspect_file(name, tracked, counts)
        except (ValueError, OSError, SyntaxError, ET.ParseError, subprocess.CalledProcessError, zipfile.BadZipFile, struct.error) as error:
            failures.append(f'{name}: {error}')
    for check in (check_snapshot, check_bag, check_map):
        try:
            check(counts)
        except (ValueError, OSError, sqlite3.Error, AttributeError, KeyError) as error:
            failures.append(f'{check.__name__}: {error}')
    print(json.dumps({'labs': len(LABS), 'checks': dict(counts), 'failures': failures}, ensure_ascii=False, indent=2))
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
