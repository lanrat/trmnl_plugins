import requests
import gzip
import io
import csv
import random

# https://rebrickable.com/downloads/
datasets = {
  "sets":  "https://cdn.rebrickable.com/media/downloads/sets.csv.gz",
  "minifigs": "https://cdn.rebrickable.com/media/downloads/minifigs.csv.gz"
}

def run(input):
  dataset = input['trmnl']['plugin_settings']['custom_fields_values']['dataset']
  url = datasets.get(dataset)
  print("dataset:", dataset, url)
  response = requests.get(url, timeout=3)
  response.raise_for_status()

  with gzip.open(io.BytesIO(response.content), "rt", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    sets = [row for row in reader if row.get("img_url") and (not row.get("num_parts") or int(row["num_parts"]) > 1000)]

    chosen = random.choice(sets)

    return {
      "lego": chosen
    }