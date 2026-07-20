import twemoji from 'twemoji'

// Telegram's own web client renders emoji with Twemoji (Twitter's open
// source emoji set) instead of relying on the OS font — that's why emoji
// look identical on iOS, Android, and desktop inside Telegram. We do the
// same thing here: escape the text first, then swap any unicode emoji for
// small inline SVG images so producers never see the (often ugly) stock
// Android/Google emoji glyphs.
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

export function renderEmojiText(text) {
  if (!text) return ''
  const escaped = escapeHtml(text)
  return twemoji.parse(escaped, {
    folder: 'svg',
    ext: '.svg',
    className: 'emoji-icon',
  })
}
