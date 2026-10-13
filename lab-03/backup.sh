#!/usr/bin/env bash
set -euo pipefail
usage() { cat <<'EOF'
Usage: backup.sh --source DIR --dest DIR [--keep N] [--dry-run] [--help]
Create timestamped .tar.gz backups, retaining the newest N backups of this source.
EOF
}
source_dir='' dest_dir='' keep=5 dry_run=false
while (($#)); do
 case "$1" in
  --source|--dest|--keep)
   if (($# < 2)); then echo "Missing value for $1" >&2; exit 2; fi
   case "$1" in --source) source_dir=$2;; --dest) dest_dir=$2;; --keep) keep=$2;; esac; shift 2;;
  --dry-run) dry_run=true; shift;;
  --help|-h) usage; exit 0;;
  *) echo "Unknown argument: $1" >&2; usage >&2; exit 2;;
 esac
done
[[ -n $source_dir && -n $dest_dir ]] || { echo 'Both --source and --dest are required' >&2; exit 2; }
[[ $keep =~ ^[1-9][0-9]*$ ]] || { echo '--keep must be a positive integer' >&2; exit 2; }
[[ -d $source_dir && -r $source_dir && -x $source_dir ]] || { echo 'Source directory not accessible' >&2; exit 3; }
source_dir=$(cd -- "$source_dir" && pwd -P)
mkdir_parent=$(dirname -- "$dest_dir")
[[ -d $mkdir_parent ]] || { echo 'Destination parent does not exist' >&2; exit 3; }
dest_dir=$(cd -- "$mkdir_parent" && pwd -P)/$(basename -- "$dest_dir")
case "$dest_dir/" in "$source_dir/"*) echo 'Destination must be outside source' >&2; exit 3;; esac
name=$(basename -- "$source_dir")
if command -v sha256sum >/dev/null; then hash=$(printf '%s' "$source_dir" | sha256sum | cut -c1-10); else hash=$(printf '%s' "$source_dir" | shasum -a 256 | cut -c1-10); fi
prefix="${name//[^a-zA-Z0-9_-]/_}-${hash}-"
timestamp=$(date -u +%Y-%m-%d-%H%M%S)-$(date +%N)
archive="${prefix}${timestamp}.tar.gz"
mapfile -d '' existing < <(if [[ -d $dest_dir ]]; then find "$dest_dir" -maxdepth 1 -type f -name "${prefix}*.tar.gz" -print0 | sort -zr; fi)
to_remove=()
if ((${#existing[@]} >= keep)); then
 for ((i=keep-1;i<${#existing[@]};i++)); do to_remove+=("${existing[i]}"); done
fi
if $dry_run; then
 echo "DRY RUN: would create $dest_dir/$archive"
 for f in "${to_remove[@]}"; do echo "DRY RUN: would remove $f"; done
 echo "DRY RUN: no files modified"
 exit 0
fi
mkdir -p -- "$dest_dir"
log="$dest_dir/backup.log"
record() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$log"; }
archive_path="$dest_dir/$archive"
tmp=$(mktemp "$dest_dir/.backup-XXXXXXXX.tar.gz")
trap 'rm -f -- "$tmp"' EXIT
if ! tar -czf "$tmp" -C "$(dirname -- "$source_dir")" -- "$name"; then record "ERROR archive failed: $source_dir" >&2; exit 4; fi
mv -- "$tmp" "$archive_path"
trap - EXIT
bytes=$(wc -c < "$archive_path" | tr -d ' ')
record "CREATED $archive_path bytes=$bytes"
for f in "${to_remove[@]}"; do rm -f -- "$f"; record "REMOVED $f"; done
record "DONE source=$source_dir kept=$keep archived_bytes=$bytes"
