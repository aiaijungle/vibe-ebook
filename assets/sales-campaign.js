(() => {
  const incoming = new URLSearchParams(window.location.search);
  const campaignKeys = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  const tags = [];

  for (const key of campaignKeys) {
    const value = incoming.get(key);
    if (value && /^[a-z0-9][a-z0-9_.-]{0,79}$/i.test(value)) {
      tags.push([key, value]);
    }
  }

  if (tags.length === 0) {
    return;
  }

  for (const link of document.querySelectorAll("a[data-aib-campaign-link]")) {
    const destination = new URL(link.href);

    for (const [key, value] of tags) {
      if (!destination.searchParams.has(key)) {
        destination.searchParams.set(key, value);
      }
    }

    link.href = destination.href;
  }
})();
