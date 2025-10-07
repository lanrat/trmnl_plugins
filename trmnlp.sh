#!/usr/bin/env bash
set -eu
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then set -o xtrace; fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# args
PLUGIN_PATH_INPUT="$1"
shift

if [[ $# -lt 1 ]]; then
    echo "Error: action argument required" >&2
    exit 1
fi

# set TRMNL_API_KEY in trmnl.env
# https://usetrmnl.com/account
if [[ ! -f "$SCRIPT_DIR/trmnl.env" ]]; then
    echo "Error: trmnl.env not found in $SCRIPT_DIR" >&2
    exit 1
fi

# Function to run docker command on a single plugin
run_plugin() {
    local plugin_path="$1"
    shift
    echo "Running on plugin: $plugin_path"
    docker run -it  --rm --name "trmnlp" \
        --publish 4567:4567 \
        --env-file "$SCRIPT_DIR/trmnl.env" \
        --user "$(id -u):$(id -g)" \
        --volume "$plugin_path:/plugin" \
        trmnl/trmnlp:latest "$@"
}

# Check if PLUGIN_PATH is '.'
if [[ "$PLUGIN_PATH_INPUT" == "." ]]; then
    # Iterate over all directories in the current directory
    for dir in "$SCRIPT_DIR"/*/; do
        # Skip if not a directory or if it doesn't contain src/settings.yml
        if [[ -d "$dir" && -f "$dir/src/settings.yml" ]]; then
            run_plugin "$(realpath "$dir")" "$@"
        fi
    done
else
    # Single plugin mode
    PLUGIN_PATH="$(realpath "$PLUGIN_PATH_INPUT")"
    # Create plugin directory if it doesn't exist
    mkdir -p "$PLUGIN_PATH"
    run_plugin "$PLUGIN_PATH" "$@"
fi
