# ♃ The Hudson Legacy Archive

<div class="hudson-hero">
  <div class="hudson-symbol">♃</div>
  <p>JUPITER 8 · FAMILY HERITAGE · ARCHIVE 001</p>
  <h2>THE HUDSON LEGACY</h2>
  <p>Roots of the past. Voices of the present. Records for the future.</p>
  <a href="#explore-the-archive">Explore the archive ↓</a>
</div>

<style>
.hudson-hero{background:radial-gradient(circle at 50% 15%,#c83725,#891e19 65%,#54120f);border:5px double #eabd40;border-radius:14px;padding:3rem 1rem;color:#fff1cd;text-align:center;margin:1rem 0 2rem}
.hudson-hero h2{font-family:Georgia,serif;font-size:clamp(2rem,5vw,3.5rem);color:#ffd145!important}
.hudson-hero p{color:#fff1cd}.hudson-symbol{font-size:5rem;color:#ffd145}
.hudson-hero a{display:inline-block;margin-top:1rem;padding:.8rem 1.3rem;border-radius:6px;background:#ffce35;color:#4a180d!important;font-weight:800;text-decoration:none!important}
.hudson-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}
.hudson-cards section{border:1px solid #d2b47b;border-top:5px solid #a52c22;border-radius:8px;background:#fff4da;padding:1rem;color:#3e2919}
.hudson-cards h3{color:#8b211b!important;font-family:Georgia,serif;margin-top:0}
.hudson-cards p{color:#3e2919}
.hudson-note{border-left:5px solid #a52c22;background:#fff4da;padding:1rem;color:#3e2919}
.hudson-hero a:focus-visible{outline:3px solid #154db9;outline-offset:3px}
</style>

> Before machines created profiles, generations made lives. Every family name deserves a careful record, not an invented conclusion.

## Explore the archive

<div class="hudson-cards">
<section><h3>🌳 Family Tree</h3><p>Documented relationships and ancestral branches, pending review and permission.</p></section>
<section><h3>📜 Ancestral Biographies</h3><p>Attributed personal histories, distinguishing evidence from family memories.</p></section>
<section><h3>🕰 Generational Timeline</h3><p>Verified dates alongside relevant historical events.</p></section>
<section><h3>🗺 Migration & Origins</h3><p>Places and journeys only where source records support them.</p></section>
<section><h3>📷 Memory Gallery</h3><p>Photographs and heirlooms with clear credits and publication rights.</p></section>
<section><h3>🔐 Provenance Ledger</h3><p>Document citations, uncertainties, corrections and source status.</p></section>
</div>

## Joseph's family tree on Ancestry

The original tree is hosted by Ancestry. This page **does not embed or republish an invitation URL** because invitations may include private access tokens.

<div class="hudson-note"><strong>Access control:</strong> Request a suitable view-only sharing link from the tree owner. No Ancestry link will be published until the owner approves a public-safe method of sharing.</div>

At present, this is a **designed archive shell**, not a verified genealogical reconstruction. No individual family relationships, identities, dates or private media have been imported.


## GEDCOM historical collection: October 2026

<div class="hudson-note"><strong>Archive intake completed.</strong> A GEDCOM 5.5.1 export titled <em>Joseph Quinton Hudson Family Tree</em> was assessed for historical coverage. This public summary is intentionally aggregate-only: it does not distribute the raw GEDCOM, living-person records, contact information, invitation tokens, or individual family relationships.</div>

| GEDCOM intake metric | Observed in the submitted export |
| --- | ---: |
| Individual records | 691 |
| Family-group records | 287 |
| Individual records containing a death event | 458 |
| Individual records with a parseable death year | 446 |
| Death-year records dated 1925 or earlier | 396 |
| Export metadata | GEDCOM 5.5.1, Ancestry family-tree export, October 16, 2026 |

### Historical scope and confidence

The tree includes records reporting historical dates reaching back into the sixteenth century. **Ancestry tree data is not automatically authenticated evidence.** Dates, identities, titles and claimed ancestral connections can be mistaken, transcribed incorrectly or duplicated. Counts represent GEDCOM records, not necessarily distinct people; the export includes repeated-looking historical entries.

**Current public exhibition status:** Data received and structurally assessed. Identity-level genealogy and relationship diagrams are withheld pending duplicate resolution, source-by-source verification, and review of publication permissions.

### Research workflow

1. Normalize names and dates while preserving original evidence.
2. Identify duplicates and inconsistent parental/partner relationships.
3. Verify each proposed link using cited independent historical sources.
4. Screen for living and possibly living people, sensitive facts and copyrighted images.
5. Publish only reviewed historical profiles with clear source citations, corrections and consent where needed.

**Research invariant:** `TREE_ASSERTION != HISTORICAL_PROOF` · `DEATH_EVENT != VERIFIED_DEATH` · `RECORD_COUNT != UNIQUE_PEOPLE`.


## Interactive Historical Ancestor Explorer

This explorer renders **45 historical profile entries** transcribed and cautiously normalized from the submitted GEDCOM. The original data contains repeated-looking entries, and its proposed relationships have **not** been corroborated by independent records. Generation labels are GEDCOM relationship hops from Joseph Quinton Hudson, not proof of lineage.

<div class="hudson-interactive" id="hudson-ancestor-explorer">
 <div class="hx-head"><span aria-hidden="true">♃ 🌳</span><strong>THE LIVING ARCHIVE OF HISTORY</strong><p>Explore reported ancestral branches. Each illustrated portrait is a decorative placeholder, not an authentic photograph.</p></div>
 <div class="hx-tools"><label>Find a historical profile <input id="hx-query" type="search" placeholder="Search a name" autocomplete="off"></label><label>Generation <select id="hx-generation"><option value="all">All generations</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option></select></label><button type="button" id="hx-reset">Reset view</button></div>
 <p id="hx-count" role="status" aria-live="polite"></p>
 <div class="hx-layout"><div id="hx-cards" class="hx-cards"></div><section class="hx-detail" id="hx-detail" aria-label="Selected profile"><h3>Select an ancestor</h3><p>Choose a card to explore the recorded generations and associated parent links.</p></section></div>
 <p class="hx-foot">TREE ASSERTION ≠ VERIFIED HISTORY · REPORTED DEATH ≠ INDEPENDENTLY CONFIRMED DEATH · NO ACTUAL PORTRAIT IMAGES WERE INCLUDED IN THE GEDCOM EXPORT.</p>
</div>
<style>
.hudson-interactive{margin:1.5rem 0;border:2px solid #b58438;border-radius:12px;background:#fdf5df;color:#4b281a;padding:clamp(12px,3vw,24px)}.hx-head{text-align:center;background:#891f19;color:#ffdd76;padding:20px 12px;border-radius:8px}.hx-head strong{display:block;font:700 clamp(1.2rem,3vw,1.9rem) Georgia,serif}.hx-head span{font-size:2rem}.hx-head p{color:#fff0c6;margin-bottom:0}.hx-tools{display:flex;flex-wrap:wrap;align-items:end;gap:12px;margin:18px 0}.hx-tools label{flex:1 1 180px;font-weight:700}.hx-tools input,.hx-tools select{display:block;width:100%;box-sizing:border-box;padding:10px;margin-top:4px;border:1px solid #9d6c3b;border-radius:6px;background:white;color:#25160d}.hx-tools button,.hx-parent{padding:10px;border:1px solid #84211a;background:#ffcf40;color:#432014;border-radius:6px;cursor:pointer;font-weight:700}.hx-layout{display:grid;grid-template-columns:minmax(0,2fr) minmax(230px,1fr);gap:16px}.hx-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(154px,1fr));gap:10px;max-height:650px;overflow:auto;align-content:start}.hx-person{background:#fffaf0;color:#432014;border:1px solid #c6a677;border-radius:9px;padding:12px;text-align:center;cursor:pointer;min-height:168px;overflow-wrap:anywhere}.hx-person[aria-pressed=true]{outline:3px solid #9b2017}.hx-portrait{display:flex;align-items:center;justify-content:center;width:68px;height:68px;margin:0 auto 8px;border-radius:50%;border:3px double #ae863f;background:linear-gradient(150deg,#e8c877,#a82a20);font-size:38px;line-height:1}.hx-person strong{display:block;color:#651914;font-family:Georgia,serif;font-size:.95rem}.hx-person small{display:block;margin-top:5px;color:#5d4934}.hx-detail{background:#fff9e8;border:2px double #c79c4f;border-radius:9px;padding:16px;align-self:start;position:sticky;top:12px}.hx-detail h3{font-family:Georgia,serif;color:#78231a!important;margin-top:.25rem}.hx-detail .hx-parent{display:block;width:100%;text-align:left;margin:7px 0}.hx-foot{font-size:.75rem;letter-spacing:.02em;color:#613c2b;margin-top:14px}.hx-detail p{color:#432014}@media(max-width:700px){.hx-layout{grid-template-columns:1fr}.hx-cards{max-height:480px}.hx-detail{position:static}}
</style>
<script>
(function(){
 const root=document.getElementById('hudson-ancestor-explorer');if(!root||root.dataset.ready)return;root.dataset.ready='true';
 const people=[["Willie L. Hudson",1864,1923,3,[1,2]],["Wm Hudson",1840,1904,4,[8,10]],["Elizabeth Hudson",1844,1917,4,[7,9]],["Mandy Jenkins",1841,1903,4,[6,11]],["Randal Jenkins",1842,1868,4,[5]],["Mariah Yopp",1821,1897,5,[14,15]],["John W Yopp",1818,1868,5,[16,17]],["James Wellborn",1800,1850,5,[18,19]],["Silas Larkin Hutson",1809,1880,5,[20,23]],["Sarah Sallie Sanders",1802,1852,5,[]],["Lucie Hutson",1813,1883,5,[21,22]],["Mary Frances Hampton - Yopp",1825,1897,5,[24,25]],["Elijah Lee",1793,1873,5,[26,27]],["Mary Polly Johnson",1810,1860,5,[28,29]],["Clementine Groves O'Neal",1801,1845,6,[31,39]],["Benjamin Wade Hampton",1800,1844,6,[34,30]],["Robert Samuel Yopp",1795,1869,6,[33,32]],["Elizabeth Hously",1800,1876,6,[36,35]],["Nancy Catherine Cleveland",1788,1814,6,[37]],["Chapley Ross Wellborn",1780,1824,6,[]],["William Hudson",1762,1850,6,[38]],["Britton Odum",1794,1862,6,[41]],["Susannah Walters",1787,1809,6,[40]],["Maryann Miller",1785,1850,6,[]],["Benjamin Wade Hampton",1800,1850,6,[42]],["Clementine Groves Oneal",1801,1847,6,[43,44]],["Stephen Lee",1770,1834,6,[]],["Mary Cox",1775,1803,6,[]],["Thomas Gideon Johnson",1787,1859,6,[]],["Nancy Austin",1792,1861,6,[]],["Mary Jane Darsey",1770,1840,7,[]],["William O'Neal",1777,1826,7,[]],["Abigail Hansley",1765,1813,7,[]],["John Yopp",1723,1803,7,[]],["Andrew Hampton Jr",1767,1840,7,[]],["Winnifred Ann Yopp",1755,1847,7,[]],["John William Hansley Jr.",1762,1822,7,[]],["Katherine Sloan",1744,1841,7,[]],["Charles Owen Hudson",1729,1763,7,[]],["Elinor Culpepper",1775,1849,7,[]],["William Walters Jr",1750,1807,7,[]],["Sarah Kitching",1776,1835,7,[]],["Mary Jane Darsey",1770,1840,7,[]],["William O'Neal",1777,1826,7,[]],["Elinor Culpepper",1775,1849,7,[]]];
 const cards=root.querySelector('#hx-cards'), detail=root.querySelector('#hx-detail'),search=root.querySelector('#hx-query'),generation=root.querySelector('#hx-generation'),count=root.querySelector('#hx-count');
 let selected=-1;
 const portrait='<span class="hx-portrait" aria-hidden="true">♟</span>';
 function node(tag,cls,content){const e=document.createElement(tag);if(cls)e.className=cls;if(content!==undefined)e.textContent=String(content);return e}
 function choose(i){selected=i;const p=people[i];detail.replaceChildren();detail.append(node('h3','',p[0]),node('p','','Recorded in submitted family tree: '+p[1]+'–'+p[2]),node('p','','Generation '+p[3]+' from Joseph (as asserted by source tree).'));
 detail.append(node('h4','','Listed parent records'));
 if(!p[4].length) detail.append(node('p','','No parent entries included in this historical preview.'));
 for(const id of [...new Set(p[4])]){if(!people[id])continue;const b=node('button','hx-parent','↳ '+people[id][0]+' ('+people[id][1]+')');b.type='button';b.addEventListener('click',()=>{search.value='';generation.value='all';render();choose(id)});detail.append(b)}
 detail.append(node('p','','Illustrated avatar only. Relationships and vital dates are unverified GEDCOM assertions.'));cards.querySelectorAll('[data-id]').forEach(e=>e.setAttribute('aria-pressed',String(Number(e.dataset.id)===i)));
 }
 function render(){cards.replaceChildren();let c=0;people.forEach((p,i)=>{if(!p[0].toLowerCase().includes(search.value.trim().toLowerCase()) || (generation.value!=='all'&&String(p[3])!==generation.value))return;c++;const b=node('button','hx-person');b.type='button';b.dataset.id=i;b.setAttribute('aria-pressed',String(i===selected));const art=node('span','hx-portrait','♟');art.setAttribute('aria-hidden','true');b.append(art,node('strong','',p[0]),node('small','',p[1]+'–'+p[2]),node('small','','Generation '+p[3]));b.addEventListener('click',()=>choose(i));cards.append(b)});count.textContent=c+' of '+people.length+' historical profile records displayed';}
 search.addEventListener('input',render);generation.addEventListener('change',render);root.querySelector('#hx-reset').addEventListener('click',()=>{search.value='';generation.value='all';selected=-1;detail.replaceChildren(node('h3','','Select an ancestor'),node('p','','Choose a card to explore listed parent relationships.'));render()});render();
})();
</script>

## Evidence and privacy policy

| Status | Interpretation |
| --- | --- |
| Documented | Supported by specifically cited records |
| Family testimony | Oral history, attributed but not independently established |
| Research lead | Unconfirmed hypothesis requiring additional records |
| Artistic interpretation | Creative framing, not historical fact |
| Private | Withheld from the public site |

Living persons' personal information must be withheld unless permission and an appropriate publication basis are confirmed. GEDCOM exports should be reviewed and redacted before publication. Imported trees are not inherently verified.

## Provenance principle

`PATTERN != PROOF` · `PROFILE != PERSON` · `MEMORY != EVIDENCE` · `HUMAN_AGENCY > MACHINE_AUTHORITY`

*♃ Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 · Heritage exhibit*
