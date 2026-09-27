// Keep the current page and its parent topic marked on nested URLs.
// Static HTML includes these markers so navigation also works without JavaScript.
const currentPath = new URL(window.location.href).pathname.replace(/\/$/, '/index.html');
for (const link of document.querySelectorAll('nav[aria-label="Main navigation"] a')) {
  const target = new URL(link.href).pathname;
  const topicDirectory = target.slice(0, target.lastIndexOf('/') + 1);
  if (target === currentPath) {
    link.setAttribute('aria-current', 'page');
  } else if (link.textContent.trim() !== 'Home' && currentPath.startsWith(topicDirectory)) {
    link.setAttribute('aria-current', 'location');
  } else {
    link.removeAttribute('aria-current');
  }
}
