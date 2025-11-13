#!/usr/bin/env bash
set -euo pipefail

show_help() {
    cat <<EOF
Usage: $0 <IP_ADDRESS>

Positional:
  IP_ADDRESS        IP of the SmartBot

Examples:
  $0 192.168.33.10
EOF
}

if [[ $# -lt 1 ]]; then
    echo "Error: missing IP address"
    echo
    show_help
    exit 1
fi

IP="$1"
REMOTE_SCRIPT="/home/smartbot/agent_repos/smartbot3_ws/docker/stop.bash prod"

# Run remote stop
ssh -tt "smartbot@${IP}" "
    echo 'Stopping SmartBot containers...'
    bash ${REMOTE_SCRIPT}
"
