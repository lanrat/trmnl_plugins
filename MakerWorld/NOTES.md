# MakerWorld Plugin Notes

## Search Term Support (investigated 2026-03-29)

Currently the plugin uses the trending endpoint. Adding an optional search term was investigated but deferred.

### The Problem

TRMNL's `polling_url` in settings.yml is static — it can interpolate custom field values (e.g., `{{search_term}}`), but can't conditionally switch between two different URLs. We need the trending endpoint when no search term is provided, and the search endpoint when one is.

### API Endpoints

**Trending** (current):
```
https://makerworld.com/api/v1/search-service/select/design/nav?navKey=Trending&offset=0&limit=20
```

**Search**:
```
https://makerworld.com/api/v1/search-service/select/design2?orderBy=score&designType=0&limit=20&offset=0&keyword=SEARCH_TERM
```

### Findings

- The search endpoint with an **empty keyword** returns results that are ~70% overlapping with trending but not identical (different total count: 1952 vs 1523, different ordering).
- `orderBy=Trending` and `navKey=Trending` on the search endpoint have no effect — it ignores those parameters.
- The `/design/nav` and `/design2` endpoints use fundamentally different ranking algorithms.
- Both endpoints return the same JSON structure (`hits` array with identical item fields).

### Options for Future Implementation

1. **Accept "close enough"**: Use the search endpoint for everything. ~70% overlap with trending when keyword is empty. Simplest approach — single polling URL with `{{search_term}}` interpolation.

2. **Serverless function**: Switch strategy to `serverless` and write a function that checks the custom field value and calls the appropriate API. Preserves exact trending results but adds complexity.

3. **Two plugins**: Keep trending as-is and create a separate "MakerWorld Search" plugin. Simplest but means maintaining two plugins.

### Custom Field Definition (ready to use)

When implementing, add this to `settings.yml` custom_fields:
```yaml
- keyname: search_term
  field_type: string
  name: Search Term
  description: Optional search term. Leave blank for trending.
  optional: true
  placeholder: 'e.g. cat, vase, tool holder'
```

Access in Liquid: `{{ trmnl.plugin_settings.custom_fields_values.search_term }}`
