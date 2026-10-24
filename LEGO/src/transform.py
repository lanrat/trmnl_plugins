import urllib.request
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
  with urllib.request.urlopen(url, timeout=10) as response:
    content = response.read()

  with gzip.open(io.BytesIO(content), "rt", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [row for row in reader if row.get("img_url")]

  # only show large sets; minifigs never reach this part count
  if dataset == "sets":
    rows = [row for row in rows if not row.get("num_parts") or int(row["num_parts"]) > 1000]

  if not rows:
    raise ValueError(f"no rows with images in dataset {dataset}")

  chosen = random.choice(rows)

  return {
    "lego": chosen
  }