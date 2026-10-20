#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
base=$(mktemp -d)
trap 'rm -rf -- "$base"' EXIT
mkdir -p "$base/source with spaces" "$base/backups"
printf 'hello' > "$base/source with spaces/test.txt"
for _ in 1 2 3 4 5 6; do
 "$here/backup.sh" --source "$base/source with spaces" --dest "$base/backups" --keep 3 >/dev/null
 sleep 0.02
done
count=$(find "$base/backups" -type f -name '*.tar.gz' | wc -l)
[[ $count -eq 3 ]] || { echo "Expected 3 backups, got $count" >&2; exit 1; }
before=$(find "$base/backups" -type f | wc -l)
"$here/backup.sh" --source "$base/source with spaces" --dest "$base/backups" --dry-run --keep 1 >/dev/null
after=$(find "$base/backups" -type f | wc -l)
[[ $before -eq $after ]] || { echo 'dry-run modified filesystem' >&2; exit 1; }
echo 'backup tests passed'
