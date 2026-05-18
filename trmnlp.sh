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

# Parse optional -y/--yes flag (auto-confirm push/pull overwrite prompts)
AUTO_YES=0
if [[ $# -ge 1 && ( "$1" == "-y" || "$1" == "--yes" ) ]]; then
    AUTO_YES=1
    shift
fi

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 [-y|--yes] <plugin-dir> <command> [args...]" >&2
    echo "       $0 pull   # update trmnlp Docker image" >&2
    exit 1
fi

# args
PLUGIN_PATH_INPUT="$1"
shift

# set TRMNL_API_KEY in trmnl.env
# https://trmnl.com/account
if [[ ! -f "$SCRIPT_DIR/trmnl.env" ]]; then
    echo "trmnl.env not found. Please visit https://trmnl.com/account to get your API key."
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
    local plugin_name
    plugin_name="$(basename "$plugin_path")"
    plugin_name="${plugin_name// /_}"
    echo "Running on plugin: $plugin_path"

    local container_name="trmnlp-${plugin_name}"
    local cmd="${1-}"

    # `serve` is the only long-running command. Background docker so bash can
    # handle Ctrl-C via trap (bash defers trap delivery while waiting on a
    # foreground child). Backgrounded with `-t` would fail, so use `-i` only.
    # All other commands run foreground with `-it` so interactive prompts work.
    # Match any unique prefix of "serve" — trmnlp's Thor CLI accepts abbreviations.
    if [[ "serve" == "$cmd"* && -n "$cmd" ]]; then
        docker run -i --init --sig-proxy=false --rm --name "$container_name" \
            --publish 4567:4567 \
            --env-file "$SCRIPT_DIR/trmnl.env" \
            --user "$(id -u):$(id -g)" \
            --env HOME=/tmp \
            --volume "$plugin_path:/plugin" \
            trmnl/trmnlp:latest "$@" &
        local docker_pid=$!
        trap 'docker kill "'"$container_name"'" >/dev/null 2>&1 || true' INT
        local rc=0
        wait "$docker_pid" || rc=$?
        trap - INT
        return $rc
    fi

    # With -y/--yes, auto-confirm push/pull overwrite prompts by piping "y".
    if [[ "$AUTO_YES" == "1" && -n "$cmd" && ( "push" == "$cmd"* || "pull" == "$cmd"* ) ]]; then
        set +o pipefail
        yes | docker run -i --init --rm --name "$container_name" \
            --env-file "$SCRIPT_DIR/trmnl.env" \
            --user "$(id -u):$(id -g)" \
            --env HOME=/tmp \
            --volume "$plugin_path:/plugin" \
            trmnl/trmnlp:latest "$@"
        local rc=$?
        set -o pipefail
        return $rc
    fi

    docker run -it --init --rm --name "$container_name" \
        --env-file "$SCRIPT_DIR/trmnl.env" \
        --user "$(id -u):$(id -g)" \
        --env HOME=/tmp \
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
