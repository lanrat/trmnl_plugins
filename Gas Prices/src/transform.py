import json
import urllib.parse
import urllib.request

GASBUDDY_GRAPHQL = "https://www.gasbuddy.com/graphql"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# GasBuddy is fronted by Cloudflare and 403s on Python's default
# "Python-urllib/x.y" UA. An empty string works from a normal Python process
# but TRMNL's serverless runtime appears to substitute its own default, so we
# send a browser UA explicitly. Nominatim also 403s on empty per its usage
# policy, so geocode() sends an identifying UA.
GASBUDDY_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
NOMINATIM_USER_AGENT = "trmnl-gas-prices-plugin"

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "apollo-require-preflight": "true",
    "Origin": "https://www.gasbuddy.com",
    "Referer": "https://www.gasbuddy.com/home",
    "gbcsrf": "x",
    "User-Agent": GASBUDDY_USER_AGENT,
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
        headers={"User-Agent": NOMINATIM_USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            results = json.loads(resp.read())
    except Exception:
        return None, None, None
    if not results:
        return None, None, None
    return float(results[0]["lat"]), float(results[0]["lon"]), results[0].get("display_name", "")


def normalize_price(val):
    """GasBuddy normally returns dollars (e.g. 3.499). Guard against cents."""
    try:
        p = float(val)
    except (TypeError, ValueError):
        return 0.0
    if p > 20:  # no US fuel price exceeds $20/gal; assume cents
        p = p / 100.0
    return p


def format_price(val):
    return "{:.2f}".format(normalize_price(val))


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
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        return {"error": "GasBuddy request failed: " + str(e)[:80]}

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
            raw_price = credit.get("price") or cash.get("price") or 0
            price_val = normalize_price(raw_price)
            posted = credit.get("postedTime") or cash.get("postedTime")
            if price_val > 0:
                all_prices[fp] = {
                    "price": price_val,
                    "display": format_price(raw_price),
                    "posted": posted,
                    "name": p.get("longName", fp),
                }
            if fp == fuel_type and price_val > 0:
                price_info = {
                    "price": price_val,
                    "display": format_price(raw_price),
                    "posted": posted,
                }

        if not price_info:
            continue

        stations.append({
            "name": s.get("name", "Unknown"),
            "address": s.get("address", {}).get("line1", ""),
            "price": price_info["price"],
            "display": price_info["display"],
            "posted": price_info["posted"],
            "all_prices": all_prices,
        })

    # Sort by price ascending, take top N
    stations.sort(key=lambda x: x["price"])
    stations = stations[:num_stations]

    # Parse trends
    trend_data = []
    for t in trends:
        avg = t.get("today", 0)
        low = t.get("todayLow", 0)
        trend_data.append({
            "area": t.get("areaName", ""),
            "average": normalize_price(avg),
            "average_display": format_price(avg) if avg else "",
            "lowest": normalize_price(low),
            "lowest_display": format_price(low) if low else "",
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
