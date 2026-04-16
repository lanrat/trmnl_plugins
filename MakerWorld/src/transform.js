// MakerWorld Trending transform — slims the polled API payload down to the
// subset of fields the template uses, keeping the merge payload under
// TRMNL's 100kb limit. The full response from
// /api/v1/search-service/select/design/nav?navKey=Trending carries deeply
// nested creator profiles, licensing, file manifests, and i18n blobs that
// the template never reads.

var MAX_ITEMS = 20;

function slim(item) {
  var creator = item.designCreator || {};
  return {
    cover: item.cover || "",
    coverPortrait: item.coverPortrait || "",
    title: item.title || "",
    titleTranslated: item.titleTranslated || "",
    downloadCount: item.downloadCount || 0,
    likeCount: item.likeCount || 0,
    printCount: item.printCount || 0,
    designCreator: { name: creator.name || "" }
  };
}

function transform(input) {
  var hits = (input && input.hits) || [];
  return {
    hits: hits.slice(0, MAX_ITEMS).map(slim)
  };
}
