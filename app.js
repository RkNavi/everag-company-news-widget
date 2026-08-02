(() => {
  "use strict";

  const status = document.getElementById("status");
  const list = document.getElementById("news-list");

  function formatDate(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    }).format(date);
  }

  function safeUrl(value) {
    try {
      const url = new URL(value);
      return ["http:", "https:"].includes(url.protocol) ? url.href : "";
    } catch {
      return "";
    }
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function renderItem(item) {
    const card = el("article", "news-card");
    const imageWrap = el("div", "news-image-wrap");
    const imageUrl = safeUrl(item.image || "");

    if (imageUrl) {
      const image = el("img", "news-image");
      image.src = imageUrl;
      image.alt = "";
      image.loading = "lazy";
      image.referrerPolicy = "no-referrer-when-downgrade";
      image.addEventListener("error", () => {
        imageWrap.replaceChildren(el("div", "news-image-placeholder", "EVER.AG"));
      });
      imageWrap.appendChild(image);
    } else {
      imageWrap.appendChild(el("div", "news-image-placeholder", "EVER.AG"));
    }

    const content = el("div", "news-content");
    const title = el("h2", "news-title");
    const titleLink = el("a", "news-title-link", item.title || "Company news");

    const href = safeUrl(item.link || "");

    if (href) {
      titleLink.href = href;
      titleLink.target = "_blank";
      titleLink.rel = "noopener noreferrer";
    }

title.appendChild(titleLink);
content.appendChild(title);
    
    if (item.summary) content.appendChild(el("p", "news-summary", item.summary));

    if (href) {
      const link = el("a", "read-more", "Read full article →");
      link.href = href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      content.appendChild(link);
    }

    card.append(imageWrap, content);
    return card;
  }

  async function loadFeed() {
    try {
      const response = await fetch(`feed.json?cache=${Date.now()}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const items = Array.isArray(data.items) ? data.items : [];

      if (!items.length) {
        status.textContent = "No company news items are currently available.";
        return;
      }

      const fragment = document.createDocumentFragment();
      items.forEach(item => fragment.appendChild(renderItem(item)));

      if (data.fetchedAt) {
        const updated = el("p", "updated", `Feed checked ${formatDate(data.fetchedAt)}`);
        fragment.appendChild(updated);
      }

      list.replaceChildren(fragment);
      status.hidden = true;
    } catch (error) {
      console.error(error);
      status.classList.add("error");
      status.textContent = "The company news feed could not be loaded. Open the Ever.Ag Company News page using the link above.";
    }
  }

  loadFeed();
})();
