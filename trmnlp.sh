#!/usr/bin/env bash
set -eu
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then set -o xtrace; fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# args
PLUGIN_PATH="$(realpath "$1")"
shift

if [[ $# -lt 1 ]]; then
    echo "Error: plugin folder/path argument required" >&2
    exit 1
fi

# set TRMNL_API_KEY in trmnl.env
# https://usetrmnl.com/account
if [[ ! -f "$SCRIPT_DIR/trmnl.env" ]]; then
    echo "Error: trmnl.env not found in $SCRIPT_DIR" >&2
    exit 1
fi

# Create plugin directory if it doesn't exist
mkdir -p "$PLUGIN_PATH"

exec docker run -it  --rm --name "trmnlp" \
    --publish 4567:4567 \
    --env-file "$SCRIPT_DIR/trmnl.env" \
    --user "$(id -u):$(id -g)" \
    --volume "$PLUGIN_PATH:/plugin" \
    trmnl/trmnlp:latest "$@"
