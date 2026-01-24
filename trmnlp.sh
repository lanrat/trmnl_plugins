#!/usr/bin/env bash
set -eu
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then set -o xtrace; fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Handle pull command
if [[ $# -ge 1 && "$1" == "pull" ]]; then
    echo "Pulling latest trmnl/trmnlp:latest Docker image..."
    docker pull trmnl/trmnlp:latest
    exit 0
fi

if [[ $# -lt 2 ]]; then
    echo "Error: plugin dir and action are required args" >&2
    exit 1
fi

# args
PLUGIN_PATH_INPUT="$1"
shift

# set TRMNL_API_KEY in trmnl.env
# https://usetrmnl.com/account
if [[ ! -f "$SCRIPT_DIR/trmnl.env" ]]; then
    echo "trmnl.env not found. Please visit https://usetrmnl.com/account to get your API key."
    read -r -p "Enter your TRMNL API key: " api_key
    if [[ -z "$api_key" ]]; then
        echo "Error: API key cannot be empty" >&2
        exit 1
    fi
    echo "TRMNL_API_KEY=$api_key" > "$SCRIPT_DIR/trmnl.env"
    echo "Created trmnl.env with your API key"
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
