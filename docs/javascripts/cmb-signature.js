/* CMB archival signature and local reading-length hints.
 * Human-readable provenance only. No tracking or remote requests.
 */
(function () {
  "use strict";
  var base = "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/";

  function link(label, url) {
    var a = document.createElement("a");
    a.textContent = label;
    a.href = url;
    return a;
  }

  function initialize() {
    var article = document.querySelector(".rst-content");
    if (!article) return;

    var path = window.location.pathname;
    if (/\/(?:fables|2084|spiders-internet)\//.test(path)) {
      var title = article.querySelector("h1");
      if (title && !article.querySelector(".cmb-reading-length")) {
        var contentWords = (article.innerText || article.textContent || "").trim().split(/\s+/).filter(Boolean).length;
        var minutes = Math.max(1, Math.ceil(contentWords / 225));
        var note = document.createElement("p");
        note.className = "cmb-reading-length";
        note.textContent = "Estimated reading time: " + minutes + " min at 225 words per minute.";
        note.style.cssText = "color:#ffde83;font-size:.84rem;font-weight:700;";
        title.insertAdjacentElement("afterend", note);
      }
    }

    if (article.querySelector(".cmb-signature-footer")) return;
    var footer = document.createElement("footer");
    footer.className = "cmb-signature-footer";
    footer.setAttribute("aria-label", "Creator, attribution and provenance");
    var heading = document.createElement("div");
    heading.className = "cmb-signature-title";
    heading.textContent = "♃ CMB™ // THE HUMAN REMAINDER";
    var author = document.createElement("p");
    author.textContent = "Jupiter Hudson / WisdomLoveThePoet / Jupiter 8. Authored literary, educational, technical, and research material has distinct evidence and licensing boundaries.";
    var axiom = document.createElement("p");
    axiom.textContent = "PATTERN ≠ PROOF | PROFILE ≠ PERSON | HUMAN_AGENCY > MACHINE_AUTHORITY";
    var nav = document.createElement("nav");
    nav.setAttribute("aria-label", "Archive provenance and legal links");
    [
      ["Creator provenance", base + "CREATOR_PROVENANCE/"],
      ["Revision history", "https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/commits/main/"],
      ["Repository license", "https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/blob/main/LICENSE"],
      ["Source repository", "https://github.com/jupiter8nohate/computational-metacognitive-bilingualism"]
    ].forEach(function (entry) {
      nav.appendChild(link(entry[0], entry[1]));
    });
    footer.appendChild(heading);
    footer.appendChild(author);
    footer.appendChild(axiom);
    footer.appendChild(nav);
    article.appendChild(footer);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
}());
