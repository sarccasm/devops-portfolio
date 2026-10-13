#!/usr/bin/env bash
set -euo pipefail
repo=$(git rev-parse --show-toplevel)
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$repo/.git/hooks"
for hook in pre-commit pre-push; do
 cp "$script_dir/hooks/$hook" "$repo/.git/hooks/$hook"
 chmod +x "$repo/.git/hooks/$hook"
done
echo 'Installed hooks. Install shellcheck and ruff for linting.'
