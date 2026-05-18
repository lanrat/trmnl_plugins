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

    # Docker is backgrounded so bash can handle Ctrl-C, which precludes `-t`
    # (a backgrounded TTY-attached process fails with "input device is not a TTY").
    local docker_tty="-i"
    local auto_yes=0
    if [[ "$AUTO_YES" == "1" && ( "${1-}" == "push" || "${1-}" == "pull" ) ]]; then
        auto_yes=1
    fi

    # Ensure Ctrl-C tears down the container. Bash defers trap delivery while
    # waiting on a foreground child, so we run docker in the background and
    # `wait` on it (which is interruptible). The trap docker-kills the
    # container so the wait returns.
    local docker_pid
    if [[ "$auto_yes" == "1" ]]; then
        set +o pipefail
        yes | docker run $docker_tty --init --sig-proxy=false --rm --name "$container_name" \
            --publish 4567:4567 \
            --env-file "$SCRIPT_DIR/trmnl.env" \
            --user "$(id -u):$(id -g)" \
            --env HOME=/tmp \
            --volume "$plugin_path:/plugin" \
            trmnl/trmnlp:latest "$@" &
        docker_pid=$!
        set -o pipefail
    else
        docker run $docker_tty --init --sig-proxy=false --rm --name "$container_name" \
            --publish 4567:4567 \
            --env-file "$SCRIPT_DIR/trmnl.env" \
            --user "$(id -u):$(id -g)" \
            --env HOME=/tmp \
            --volume "$plugin_path:/plugin" \
            trmnl/trmnlp:latest "$@" &
        docker_pid=$!
    fi

    trap 'docker kill "'"$container_name"'" >/dev/null 2>&1 || true' INT
    local rc=0
    wait "$docker_pid" || rc=$?
    trap - INT
    return $rc
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
