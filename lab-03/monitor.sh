#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo 'Usage: monitor.sh [--config FILE] [--help]'
}

config="$(cd "$(dirname "$0")" && pwd)/config/system.env"

while (($#)); do
    case "$1" in
        --config)
            (($# >= 2)) || {
                echo 'Missing --config path' >&2
                exit 2
            }
            config=$2
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
done

[[ -f $config ]] || {
    echo "Missing config: $config" >&2
    exit 2
}

# shellcheck source=/dev/null
source "$config"

: "${CPU_MAX:=85}" "${MEM_MAX:=85}" "${DISK_MAX:=90}"
: "${DISK_PATH:=/}" "${SERVICES:=}" "${MONITOR_LOG:=system-monitor.log}"

for value in "$CPU_MAX" "$MEM_MAX" "$DISK_MAX"; do
    if ! [[ $value =~ ^[0-9]+$ ]] || ((value > 100)); then
        echo 'Thresholds must be 0..100' >&2
        exit 2
    fi
done

[[ -d "$DISK_PATH" ]] || {
    echo 'Invalid disk path' >&2
    exit 2
}

[[ -r /proc/stat && -r /proc/meminfo ]] || {
    echo 'Linux /proc required' >&2
    exit 3
}

read -r _ u n s idle io irq sirq steal _ < /proc/stat
prev_idle=$((idle + io))
prev_total=$((u + n + s + idle + io + irq + sirq + steal))

sleep 1

read -r _ u n s idle io irq sirq steal _ < /proc/stat
idle_diff=$((idle + io - prev_idle))
total_diff=$((u + n + s + idle + io + irq + sirq + steal - prev_total))
cpu=$((total_diff > 0 ? (100 * (total_diff - idle_diff) / total_diff) : 0))

mem_total=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
mem_avail=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
mem=$((100 * (mem_total - mem_avail) / mem_total))

disk=$(df -P "$DISK_PATH" | awk 'NR==2 {gsub(/%/, "", $5); print $5}')

issues=()

if ((cpu > CPU_MAX)); then
    issues+=("CPU=$cpu% > $CPU_MAX%")
fi

if ((mem > MEM_MAX)); then
    issues+=("MEM=$mem% > $MEM_MAX%")
fi

if ((disk > DISK_MAX)); then
    issues+=("DISK=$disk% > $DISK_MAX%")
fi

for svc in $SERVICES; do
    if ! systemctl is-active --quiet "$svc"; then
        issues+=("SERVICE $svc inactive")
    fi
done

stamp=$(date -u +%FT%TZ)

if ((${#issues[@]})); then
    printf '%s ALERT cpu=%s%% memory=%s%% disk=%s%% %s\n' \
        "$stamp" "$cpu" "$mem" "$disk" "${issues[*]}" | tee -a "$MONITOR_LOG"
    exit 1
fi

printf '%s OK cpu=%s%% memory=%s%% disk=%s%% services=healthy\n' \
    "$stamp" "$cpu" "$mem" "$disk" | tee -a "$MONITOR_LOG"
