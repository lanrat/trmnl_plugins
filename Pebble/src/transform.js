// Pebble Appstore transform — slims the polled repebble appstore JSON down
// to the small subset of fields the template needs, keeping the merge
// payload under TRMNL's 100kb limit.
//
// Multi-URL polling exposes the two responses as input.IDX_0 (watchfaces)
// and input.IDX_1 (watchapps-and-companions). Custom field values are at
// input.trmnl.plugin_settings.custom_fields_values.

function slim(item) {
  var listImg = item.list_image || {};
  var screenshots = item.screenshot_images || [];
  var firstShot = screenshots[0] || {};
  var latest = item.latest_release || {};
  return {
    id: item.id,
    title: item.title || "",
    author: item.author || "",
    type: item.type || "",
    hearts: item.hearts || 0,
    list_image_144: listImg["144x144"] || "",
    screenshot_144x168: firstShot["144x168"] || "",
    published_date: latest.published_date || ""
  };
}

function transform(input) {
  var settings = (input.trmnl && input.trmnl.plugin_settings && input.trmnl.plugin_settings.custom_fields_values) || {};
  var feed = settings.feed || "most-loved";
  var sortMode = settings.sort_mode || "updated";
  var contentType = settings.content_type || "both";

  var faces = (input.IDX_0 && input.IDX_0.data) || [];
  var apps = (input.IDX_1 && input.IDX_1.data) || [];

  // Soft balance for "both": cap each type at PER_TYPE_CAP so a much larger
  // collection (e.g. 30 faces vs 10 apps) doesn't drown out the rarer type
  // when the grid randomly samples cards.
  var PER_TYPE_CAP = 20;
  var items = [];
  if (contentType === "watchfaces") {
    items = faces;
  } else if (contentType === "apps") {
    items = apps;
  } else {
    items = faces.slice(0, PER_TYPE_CAP).concat(apps.slice(0, PER_TYPE_CAP));
  }

  items = items.map(slim);

  if (feed === "all" && sortMode === "released") {
    items.sort(function (a, b) {
      return (b.published_date || "").localeCompare(a.published_date || "");
    });
  }

  var feedLabel;
  if (feed === "most-loved") {
    feedLabel = "Top Picks";
  } else if (sortMode === "released") {
    feedLabel = "Recently Released";
  } else {
    feedLabel = "Recently Updated";
  }

  var typeLabel;
  if (contentType === "watchfaces") {
    typeLabel = "Faces";
  } else if (contentType === "apps") {
    typeLabel = "Apps";
  } else {
    typeLabel = "Faces + Apps";
  }

  return {
    pebble: {
      items: items,
      feed_label: feedLabel,
      type_label: typeLabel,
      instance_title: feedLabel + " \u00b7 " + typeLabel,
      count: items.length
    }
  };
}
