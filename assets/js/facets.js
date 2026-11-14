/* GeoFAIR Resource Hub — faceted search over the embedded Schema.org ItemList.
   No dependencies. Reads <script id="resource-index" type="application/ld+json">,
   derives facets from the DefinedTerm objects, filters client-side, and keeps the
   selection in the URL query string so views can be shared. */
(function () {
  'use strict';

  var indexEl = document.getElementById('resource-index');
  var resultsEl = document.getElementById('results');
  var countEl = document.getElementById('result-count');
  var activeEl = document.getElementById('active-filters');
  var qEl = document.getElementById('q');
  var panel = document.getElementById('facets');
  if (!indexEl || !resultsEl || !panel) return;

  var data;
  try { data = JSON.parse(indexEl.textContent); } catch (e) { resultsEl.textContent = 'The catalogue index could not be read.'; return; }
  var raw = (data.itemListElement || []).map(function (li) { return li.item || li; });

  /* ---- Normalise each LearningResource into a flat record ---------------- */
  function arr(x) { return x == null ? [] : (Array.isArray(x) ? x : [x]); }
  function termsIn(set, about) {
    return arr(about).filter(function (t) { return t && typeof t === 'object' && String(t.inDefinedTermSet || '').indexOf('/vocab/' + set + '/') !== -1; });
  }
  function code(t) { return t && typeof t === 'object' ? t.termCode : t; }
  function label(t) { return t && typeof t === 'object' ? (t.name || t.termCode) : t; }

  var items = raw.map(function (it) {
    var stages = termsIn('lifecycle-stage', it.about);
    var areas = termsIn('research-area', it.about);
    var type = it.learningResourceType;
    var level = it.educationalLevel;
    var status = code(it.creativeWorkStatus) || 'published';
    var cost = it.conditionsOfAccess;
    var authors = arr(it.author).map(function (a) { return a && a.name ? a.name : ''; });
    var text = [it.name, it.description, arr(it.keywords).join(' '), arr(it.teaches).join(' '), authors.join(' '),
                stages.map(label).join(' '), areas.map(label).join(' '), label(type), label(level)].join(' ').toLowerCase();
    return {
      id: it['@id'], name: it.name, description: it.description || '', url: it.url,
      type: code(type), typeLabel: label(type), level: code(level), levelLabel: label(level),
      stage: stages.map(code), stageLabels: stages.map(label),
      area: areas.map(code), areaLabels: areas.map(label),
      audience: arr(it.audience).map(function (a) { return a && a.audienceType ? a.audienceType : a; }),
      cost: code(cost) || (it.isAccessibleForFree === false ? 'yes' : 'no'), costLabel: label(cost),
      free: it.isAccessibleForFree === true, status: status, text: text
    };
  });

  /* ---- Facet definitions come from the rendered panel -------------------- */
  var facets = Array.prototype.map.call(panel.querySelectorAll('.facet'), function (fs) {
    return { key: fs.dataset.facet, el: fs, inputs: Array.prototype.slice.call(fs.querySelectorAll('input[type=checkbox]')) };
  });
  // The audience facet stores ids in the panel but labels in the JSON-LD; map label -> id by the panel's label text.
  var audienceLabelToId = {};
  facets.forEach(function (f) {
    if (f.key !== 'audience') return;
    f.inputs.forEach(function (i) { var l = panel.querySelector('label[for="' + i.id + '"]'); if (l) audienceLabelToId[l.textContent.trim()] = i.value; });
  });
  items.forEach(function (it) { it.audience = it.audience.map(function (a) { return audienceLabelToId[a] || a; }); });

  function valueOf(it, key) {
    switch (key) {
      case 'stage': return it.stage;
      case 'area': return it.area;
      case 'type': return it.type ? [it.type] : [];
      case 'level': return it.level ? [it.level] : [];
      case 'audience': return it.audience;
      case 'cost': return it.cost ? [it.cost] : [];
      case 'free': return it.free ? ['1'] : [];
      case 'obsolete': return it.status === 'obsolete' ? ['1'] : [];
      default: return [];
    }
  }

  /* ---- State <-> URL ----------------------------------------------------- */
  function readState() {
    var p = new URLSearchParams(location.search);
    var s = { q: (p.get('q') || '').trim() };
    facets.forEach(function (f) { s[f.key] = (p.get(f.key) || '').split(',').filter(Boolean); });
    return s;
  }
  function writeState(s) {
    var p = new URLSearchParams();
    if (s.q) p.set('q', s.q);
    facets.forEach(function (f) { if (s[f.key].length) p.set(f.key, s[f.key].join(',')); });
    var qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }

  /* ---- Filtering --------------------------------------------------------- */
  function matchesFacet(it, key, selected) {
    if (key === 'obsolete') return selected.length ? true : it.status !== 'obsolete';
    if (!selected.length) return true;
    var vals = valueOf(it, key);
    return selected.some(function (v) { return vals.indexOf(v) !== -1; });
  }
  function matchesQuery(it, q) {
    if (!q) return true;
    return q.toLowerCase().split(/\s+/).every(function (tok) { return it.text.indexOf(tok) !== -1; });
  }
  function filterItems(s, skipKey) {
    return items.filter(function (it) {
      if (!matchesQuery(it, s.q)) return false;
      return facets.every(function (f) { return f.key === skipKey ? true : matchesFacet(it, f.key, s[f.key]); });
    });
  }

  /* ---- Rendering --------------------------------------------------------- */
  function esc(x) { return String(x == null ? '' : x).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function chip(txt, cls) { return '<span class="chip ' + (cls || '') + '">' + esc(txt) + '</span>'; }
  function card(it) {
    var desc = it.description.length > 200 ? it.description.slice(0, 197).replace(/\s+\S*$/, '') + '…' : it.description;
    return '<article class="card">' +
      '<p class="card__eyebrow">' + (it.typeLabel ? chip(it.typeLabel, 'chip--type') + ' ' : '') + (it.levelLabel ? chip(it.levelLabel) + ' ' : '') +
        (it.costLabel ? chip(it.costLabel, it.free ? 'chip--free' : '') + ' ' : '') + (it.status === 'obsolete' ? chip('Obsolete', 'chip--warning') : '') + '</p>' +
      '<h3 class="card__title"><a href="' + esc(it.id) + '">' + esc(it.name) + '</a></h3>' +
      '<p class="card__description">' + esc(desc) + '</p>' +
      '<p class="card__chips">' + it.stageLabels.map(function (l) { return chip(l, 'chip--stage'); }).join(' ') + ' ' +
        it.areaLabels.map(function (l) { return chip(l, 'chip--area'); }).join(' ') + '</p>' +
      (it.url ? '<p class="card__links"><a href="' + esc(it.url) + '" target="_blank" rel="noopener">Open resource ↗<span class="sr-only"> (opens in a new tab)</span></a></p>' : '') +
      '</article>';
  }

  function render(s) {
    var shown = filterItems(s, null);
    resultsEl.innerHTML = shown.length ? shown.map(card).join('') : '<p class="notice">No resources match. Try removing a filter.</p>';
    countEl.textContent = shown.length + ' of ' + items.length + ' resources';

    // Counts per facet value: computed with that facet's own selection ignored.
    facets.forEach(function (f) {
      var base = filterItems(s, f.key);
      f.inputs.forEach(function (input) {
        var n = base.filter(function (it) { return valueOf(it, f.key).indexOf(input.value) !== -1; }).length;
        var c = f.el.querySelector('[data-count-for="' + input.value + '"]');
        if (c) c.textContent = n;
        input.parentNode.classList.toggle('is-empty', n === 0 && !input.checked);
        input.checked = s[f.key].indexOf(input.value) !== -1;
      });
    });

    var active = [];
    facets.forEach(function (f) {
      s[f.key].forEach(function (v) {
        var input = f.inputs.filter(function (i) { return i.value === v; })[0];
        var l = input ? panel.querySelector('label[for="' + input.id + '"]') : null;
        if (l) active.push(l.textContent.trim());
      });
    });
    activeEl.textContent = active.length ? 'Filters: ' + active.join(' · ') : '';
  }

  /* ---- Wire up ----------------------------------------------------------- */
  var state = readState();
  if (qEl) qEl.value = state.q;

  panel.addEventListener('change', function (e) {
    var input = e.target;
    if (!input || input.type !== 'checkbox') return;
    var key = input.name, sel = state[key] || [];
    if (input.checked) { if (sel.indexOf(input.value) === -1) sel.push(input.value); }
    else { sel = sel.filter(function (v) { return v !== input.value; }); }
    state[key] = sel;
    writeState(state); render(state);
  });

  var t;
  if (qEl) qEl.addEventListener('input', function () {
    clearTimeout(t);
    t = setTimeout(function () { state.q = qEl.value.trim(); writeState(state); render(state); }, 150);
  });

  var reset = document.getElementById('facets-reset');
  if (reset) reset.addEventListener('click', function () {
    state = { q: '' }; facets.forEach(function (f) { state[f.key] = []; });
    if (qEl) qEl.value = '';
    writeState(state); render(state);
  });

  window.addEventListener('popstate', function () { state = readState(); if (qEl) qEl.value = state.q; render(state); });

  render(state);
})();
