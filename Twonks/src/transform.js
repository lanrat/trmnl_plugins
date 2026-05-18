function transform(input) {
  const channel = (input && input.rss && input.rss.channel) || (input && input.channel) || {};
  const rawItems = channel.item;
  const items = Array.isArray(rawItems) ? rawItems : (rawItems ? [rawItems] : []);

  const txt = (v) => {
    if (v == null) return '';
    if (typeof v === 'string') return v;
    if (typeof v === 'object') return v._text || v['#text'] || v.__cdata || v._cdata || '';
    return String(v);
  };

  // Nitter marks video posts with a literal "<br>Video<br>" in the description;
  // the <img> in those is just a video thumbnail, not the comic.
  const isVideo = (desc) => /<br\s*\/?>\s*Video\s*<br\s*\/?>/i.test(desc);

  let chosen = null;
  let imageUrl = null;
  for (const item of items) {
    const desc = txt(item.description);
    if (isVideo(desc)) continue;
    const m = desc.match(/<img[^>]+src=["']([^"']+)["']/i);
    if (!m) continue;
    chosen = item;
    imageUrl = m[1];
    break;
  }

  if (!chosen) {
    return { comic: { title: '', link: '', pub_date: '', image_url: null }, channel_title: txt(channel.title) };
  }

  return {
    comic: {
      title: txt(chosen.title),
      link: txt(chosen.link),
      pub_date: txt(chosen.pubDate),
      image_url: imageUrl
    },
    channel_title: txt(channel.title)
  };
}
