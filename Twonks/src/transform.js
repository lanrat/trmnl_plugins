// Serverless transform for the Twonks Comics plugin.
//
// Source history: the plugin used to poll a Nitter RSS mirror of @twonkscomics
// on X. Nitter shut down (the feed now 410s) and twonkscomics.com is no longer
// registered, so the feed is taken from Bluesky instead — Steve Nelson posts
// each comic to @twonks.bsky.social, and the public AppView API needs no auth:
//
//   https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed
//     ?actor=twonks.bsky.social&limit=20&filter=posts_with_media
//
// Output contract is unchanged from the RSS version: { comic, channel_title }.

function transform(input) {
  const feed = (input && Array.isArray(input.feed)) ? input.feed : [];

  // Bluesky attaches images either directly (app.bsky.embed.images#view) or
  // nested under a quote post (app.bsky.embed.recordWithMedia#view).
  const imagesOf = (embed) => {
    if (!embed) return [];
    if (Array.isArray(embed.images)) return embed.images;
    if (embed.media && Array.isArray(embed.media.images)) return embed.media.images;
    return [];
  };

  // at://did:.../app.bsky.feed.post/<rkey> -> a browsable bsky.app permalink
  const webLink = (post) => {
    const handle = (post.author && (post.author.handle || post.author.did)) || 'twonks.bsky.social';
    const rkey = String(post.uri || '').split('/').pop();
    return rkey ? `https://bsky.app/profile/${handle}/post/${rkey}` : '';
  };

  let chosen = null;
  let imageUrl = null;
  for (const entry of feed) {
    // Skip reposts (someone else's art) and replies (usually chatter, not a strip).
    if (!entry || entry.reason) continue;
    const post = entry.post;
    if (!post || !post.record || post.record.reply) continue;

    const img = imagesOf(post.embed)[0];
    if (!img || !img.fullsize) continue;

    chosen = post;
    imageUrl = img.fullsize;
    break;
  }

  // Read the name off the chosen post, not feed[0] — a repost at the top of the
  // feed would otherwise put someone else's display name in the title bar.
  const channelTitle = (chosen && chosen.author && chosen.author.displayName) || 'Twonks';

  if (!chosen) {
    return { comic: { title: '', link: '', pub_date: '', image_url: null }, channel_title: channelTitle };
  }

  // Post text is the caption/title; keep the first line so long captions don't
  // overflow the title bar.
  const title = String(chosen.record.text || '').split('\n')[0].trim();

  return {
    comic: {
      title: title,
      link: webLink(chosen),
      pub_date: chosen.record.createdAt || chosen.indexedAt || '',
      image_url: imageUrl
    },
    channel_title: channelTitle
  };
}
