#!/usr/bin/env python3
"""Analyze Apache/Nginx combined access logs; malformed entries are counted."""
import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

LOG_RE = re.compile(r'^(?P<ip>\S+) \S+ \S+ \[(?P<date>[^]]+)\] "(?P<request>(?:[^"\\]|\\.)*)" (?P<status>\d{3}) (?P<bytes>\S+) "(?:[^"\\]|\\.)*" "(?:[^"\\]|\\.)*"$')


def parse_line(line):
    match = LOG_RE.match(line.strip())
    if not match:
        return None
    data = match.groupdict()
    try:
        date = datetime.strptime(data['date'], '%d/%b/%Y:%H:%M:%S %z')
        code = int(data['status'])
    except ValueError:
        return None
    if not 100 <= code <= 599:
        return None
    return {'ip': data['ip'], 'status': code, 'hour': date.strftime('%Y-%m-%d %H:00 %z')}


def analyze(lines, top):
    ips, classes, hours = Counter(), Counter(), Counter()
    bad = total = 0
    for line in lines:
        total += 1
        item = parse_line(line)
        if item is None:
            bad += 1
            continue
        ips[item['ip']] += 1
        classes[f"{item['status']//100}xx"] += 1
        hours[item['hour']] += 1
    return {'total_lines': total, 'valid_lines': total-bad, 'malformed_lines': bad,
            'top_ips': [{'ip': ip, 'requests': n} for ip, n in ips.most_common(top)],
            'status_classes': dict(sorted(classes.items())),
            'hourly_requests': dict(sorted(hours.items()))}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Analyze web server combined access logs')
    ap.add_argument('--input', required=True, help='Combined log file')
    ap.add_argument('--output', required=True, help='Report destination')
    ap.add_argument('--format', choices=['text', 'json'], default='text')
    ap.add_argument('--top', type=int, default=5)
    args = ap.parse_args(argv)
    if args.top < 1:
        ap.error('--top must be positive')
    try:
        with open(args.input, encoding='utf-8', errors='replace') as handle:
            report = analyze(handle, args.top)
        if args.format == 'json':
            content = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        else:
            content = (f"Total: {report['total_lines']} | Valid: {report['valid_lines']} | Malformed: {report['malformed_lines']}\n"
                       + 'Top IPs:\n' + ''.join(f"  {x['ip']}: {x['requests']}\n" for x in report['top_ips'])
                       + 'Status classes:\n' + ''.join(f'  {k}: {v}\n' for k,v in report['status_classes'].items())
                       + 'Hourly requests:\n' + ''.join(f'  {k}: {v}\n' for k,v in report['hourly_requests'].items()))
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        print(f'Wrote {path} (malformed: {report["malformed_lines"]})')
        return 0
    except OSError as exc:
        print(f'File error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
