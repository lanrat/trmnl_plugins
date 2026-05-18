#!/usr/bin/env python3
"""Test harness for Gas Prices serverless function.

Usage:
    python3 test.py <search> [fuel_type] [num_stations]

Examples:
    python3 test.py 90210
    python3 test.py 80202 regular_gas 5
    python3 test.py "Denver CO" diesel 10
"""

import sys
import json

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    search = sys.argv[1]
    fuel_type = sys.argv[2] if len(sys.argv) > 2 else "regular_gas"
    num_stations = sys.argv[3] if len(sys.argv) > 3 else "8"

    input_data = {
        "trmnl": {
            "plugin_settings": {
                "custom_fields_values": {
                    "search": search,
                    "fuel_type": fuel_type,
                    "num_stations": num_stations,
                }
            }
        }
    }

    # Load and execute the transform function
    with open("src/transform.py") as f:
        exec(f.read(), globals())

    result = run(input_data)  # noqa: F821

    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    gas = result["gas"]
    print(f"Search: {gas['search']}  |  Fuel: {gas['fuel_label']}  |  Stations: {gas['station_count']}")
    print()

    if gas["trends"]:
        print("Trends:")
        for t in gas["trends"]:
            arrow = {1: "UP", -1: "DOWN"}.get(t["direction"], "FLAT")
            low = f"  low=${t['lowest_display']}" if t["lowest"] else ""
            print(f"  {t['area']:20s} avg=${t['average_display']}{low}  {arrow}")
        print()

    print("Stations (sorted by price):")
    for i, s in enumerate(gas["stations"]):
        marker = " << CHEAPEST" if i == 0 else ""
        print(f"  ${s['display']:<8} {s['name']:20s} {s['address']}{marker}")

    print()
    print("Raw JSON:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
