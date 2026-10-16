#!/usr/bin/env bash
# Print TRMNL plugin directories, one per line.
# A plugin is a top-level directory containing src/settings.yml.
#
#   trmnl-plugins.sh all                  every plugin
#   trmnl-plugins.sh changed BEFORE AFTER plugins with src/ changes in BEFORE..AFTER
#                                         (all plugins if BEFORE is unknown)
#   trmnl-plugins.sh NAME                 a single plugin, validated
set -euo pipefail
if [[ "${TRACE-0}" == "1" ]]; then set -o xtrace; fi
cd "$(git rev-parse --show-toplevel)"

all_plugins() {
    for dir in */; do
        if [[ -f "$dir/src/settings.yml" ]]; then
            echo "${dir%/}"
        fi
    done
}

case "${1-}" in
    all)
        all_plugins
        ;;
    changed)
        before="${2:?missing BEFORE commit}"
        after="${3:?missing AFTER commit}"
        # New branches and force-pushes have no usable base commit.
        if [[ "$before" =~ ^0+$ ]] || ! git cat-file -e "$before^{commit}" 2>/dev/null; then
            echo "Base commit '$before' unavailable, selecting all plugins" >&2
            all_plugins
            exit 0
        fi
        git diff --name-only -z "$before" "$after" -- '*/src/*' \
            | tr '\0' '\n' | cut -d/ -f1 | sort -u \
            | while IFS= read -r dir; do
                # skip plugins deleted in this range
                if [[ -f "$dir/src/settings.yml" ]]; then
                    echo "$dir"
                fi
            done
        ;;
    "")
        echo "Usage: $0 all | changed BEFORE AFTER | <plugin-dir>" >&2
        exit 2
        ;;
    *)
        dir="${1%/}"
        if [[ ! -f "$dir/src/settings.yml" ]]; then
            echo "Error: '$dir' is not a plugin (no src/settings.yml)" >&2
            exit 1
        fi
        echo "$dir"
        ;;
esac
