/* D.N.A. Bible progressive reading enhancement: private, ephemeral state only. */
(() => {
  "use strict";
  const routes = Object.freeze([
    ["DEATH_NOTE_2084", "I: Everybody Dies Twice"],
    ["DEATH_NOTE_2084_FALSE_LIGHT", "II: The False Light Protocol"],
    ["DEATH_NOTE_2084_HOUSE_OF_A_MILLION_DOORS", "III: The House of a Million Doors"],
    ["DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_CELLS", "IV: The Ledger of Invisible Cells"],
    ["DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE", "V: The Child Who Refused the Update"],
    ["DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_YEARS", "VI: The Ledger of Invisible Years"],
    ["DEATH_NOTE_2084_POST_GROUND_BASELINE", "VII: The Post-Ground Baseline"],
    ["DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE", "VIII: The Witness in the Lighthouse"],
    ["DEATH_NOTE_2084_STATION_SEVEN", "IX: Station Seven"]
  ]);
  const slug = window.location.pathname.replace(/\/+$/, "").split("/").pop();
  const index = routes.findIndex(([route]) => route === slug);
  if (index >= 0) {
    const content = document.querySelector(".rst-content");
    if (content && !content.querySelector(".cmb-chapter-nav")) {
      const nav = document.createElement("nav");
      nav.className = "cmb-chapter-nav";
      nav.setAttribute("aria-label", "DEATH NOTE 2084 chapter navigation");
      const heading = document.createElement("strong");
      heading.textContent = "𓂀 DEATH NOTE 2084 // TRANSMISSION " + (index + 1) + " OF 9";
      const row = document.createElement("div");
      row.className = "cmb-chapter-nav__links";
      const base = new URL("../", window.location.href);
      const add = (label, route) => {
        const link = document.createElement("a");
        link.href = new URL(route, base).href;
        link.textContent = label;
        row.append(link);
      };
      add("All nine transmissions", "2084/");
      if (index > 0) add("Previous: " + routes[index - 1][1], routes[index - 1][0] + "/");
      if (index + 1 < routes.length) add("Next: " + routes[index + 1][1], routes[index + 1][0] + "/");
      nav.append(heading, row);
      content.append(nav);
    }
  }
  const reader = document.getElementById("cmb-nine-transmissions");
  if (!reader) return;
  const boxes = Array.from(reader.querySelectorAll("input[type=checkbox][data-chapter]"));
  const status = reader.querySelector("#cmb-reader-progress");
  if (!status || boxes.length !== 9) return;
  const update = () => {
    const total = boxes.filter(box => box.checked).length;
    status.textContent = total + " of 9 transmissions marked read in this open page.";
  };
  boxes.forEach(box => box.addEventListener("change", update));
  update();
})();