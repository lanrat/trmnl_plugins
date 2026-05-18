import json
import urllib.parse
import urllib.request

GASBUDDY_GRAPHQL = "https://www.gasbuddy.com/graphql"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "apollo-require-preflight": "true",
    "Origin": "https://www.gasbuddy.com",
    "Referer": "https://www.gasbuddy.com/home",
    "gbcsrf": "x",
    "User-Agent": "",
}

LOCATION_QUERY_PRICES = (
    "query LocationBySearchTerm("
    "$fuel: Int, $lat: Float, $lng: Float, $maxAge: Int, $search: String"
    ") { locationBySearchTerm(lat: $lat, lng: $lng, search: $search) { "
    "stations(fuel: $fuel lat: $lat lng: $lng maxAge: $maxAge) { "
    "results { address { line1 } name "
    "prices { cash { postedTime price } "
    "credit { postedTime price } fuelProduct longName } "
    "priceUnit currency id } } "
    "trends { areaName country today todayLow trend } } }"
)

FUEL_TYPE_MAP = {
    "regular_gas": 1,
    "midgrade_gas": 2,
    "premium_gas": 3,
    "diesel": 5,
}


def geocode(search):
    """Geocode a search term to lat/lng using Nominatim."""
    # Try as US postal code first if it looks like a zip
    params = {"format": "json", "limit": 1}
    if search.strip().isdigit() and len(search.strip()) == 5:
        params["postalcode"] = search.strip()
        params["country"] = "US"
    else:
        params["q"] = search

    req = urllib.request.Request(
        NOMINATIM_URL + "?" + urllib.parse.urlencode(params),
        headers={"User-Agent": "trmnl-gas-prices-plugin"},
    )
    with urllib.request.urlopen(req, timeout=4) as resp:
        results = json.loads(resp.read())
    if not results:
        return None, None, None
    return float(results[0]["lat"]), float(results[0]["lon"]), results[0].get("display_name", "")


def run(input):
    settings = input["trmnl"]["plugin_settings"]["custom_fields_values"]
    search = settings.get("search", "")
    fuel_type = settings.get("fuel_type", "regular_gas")
    num_stations = int(settings.get("num_stations", "8"))

    if not search:
        return {"error": "Please set a ZIP code or city in plugin settings."}

    # Geocode the search term to coordinates
    lat, lng, display_name = geocode(search)
    if lat is None:
        return {"error": "Could not find location: " + search}

    fuel_int = FUEL_TYPE_MAP.get(fuel_type, 1)

    query = {
        "operationName": "LocationBySearchTerm",
        "query": LOCATION_QUERY_PRICES,
        "variables": {
            "maxAge": 0,
            "fuel": fuel_int,
            "lat": lat,
            "lng": lng,
            "search": search,
        },
    }

    req = urllib.request.Request(
        GASBUDDY_GRAPHQL,
        data=json.dumps(query).encode("utf-8"),
        headers=DEFAULT_HEADERS,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=4) as resp:
        data = json.loads(resp.read())

    if "errors" in data:
        return {"error": data["errors"][0].get("message", "API error")}

    location = data.get("data", {}).get("locationBySearchTerm", {})
    raw_stations = location.get("stations", {}).get("results", [])
    trends = location.get("trends", [])

    # Parse stations
    stations = []
    for s in raw_stations:
        # Find the matching fuel type price
        price_info = None
        all_prices = {}
        for p in s.get("prices", []):
            fp = p.get("fuelProduct", "")
            credit = p.get("credit") or {}
            cash = p.get("cash") or {}
            price_val = credit.get("price") or cash.get("price") or 0
            posted = credit.get("postedTime") or cash.get("postedTime")
            if price_val and price_val > 0:
                all_prices[fp] = {
                    "price": price_val,
                    "posted": posted,
                    "name": p.get("longName", fp),
                }
            if fp == fuel_type and price_val and price_val > 0:
                price_info = {
                    "price": price_val,
                    "posted": posted,
                }

        if not price_info:
            continue

        stations.append({
            "name": s.get("name", "Unknown"),
            "address": s.get("address", {}).get("line1", ""),
            "price": price_info["price"],
            "posted": price_info["posted"],
            "all_prices": all_prices,
        })

    # Sort by price ascending, take top N
    stations.sort(key=lambda x: x["price"])
    stations = stations[:num_stations]

    # Parse trends
    trend_data = []
    for t in trends:
        trend_data.append({
            "area": t.get("areaName", ""),
            "average": t.get("today", 0),
            "lowest": t.get("todayLow", 0),
            "direction": t.get("trend", 0),
        })

    fuel_labels = {
        "regular_gas": "Regular",
        "midgrade_gas": "Midgrade",
        "premium_gas": "Premium",
        "diesel": "Diesel",
    }

    return {
        "gas": {
            "stations": stations,
            "trends": trend_data,
            "fuel_label": fuel_labels.get(fuel_type, "Regular"),
            "search": search,
            "station_count": len(stations),
        }
    }
