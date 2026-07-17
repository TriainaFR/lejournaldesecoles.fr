/* Le Journal des Écoles — moteur de recherche client (site statique).
   Index : /assets/search-index.json. Utilisé par l'overlay (suggestions
   instantanées) et par la page /recherche/ (résultats complets). */
(function () {
  'use strict';

  var INDEX_URL = '/assets/search-index.json';
  var cache = null;

  function normalize(s) {
    return (s || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[\u2019'`]/g, ' ');
  }

  function load() {
    if (cache) return Promise.resolve(cache);
    return fetch(INDEX_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        data.forEach(function (e) {
          e._title = normalize(e.title);
          e._kw = normalize(e.keywords);
          e._ex = normalize(e.excerpt);
          e._cat = normalize(e.cat);
        });
        cache = data;
        return data;
      });
  }

  function score(entry, terms) {
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i], s = 0;
      if (entry._title.indexOf(t) !== -1) s += 4;
      if (entry._kw.indexOf(t) !== -1) s += 2;
      if (entry._cat.indexOf(t) !== -1) s += 2;
      if (entry._ex.indexOf(t) !== -1) s += 1;
      if (s === 0) return 0;           // chaque terme doit matcher quelque part
      total += s;
    }
    if (entry.type === 'Article') total += 2;   // les articles d'abord
    return total;
  }

  function query(q) {
    var terms = normalize(q).split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return Promise.resolve([]);
    return load().then(function (data) {
      return data
        .map(function (e) { return { entry: e, s: score(e, terms) }; })
        .filter(function (r) { return r.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .map(function (r) { return r.entry; });
    });
  }

  /* — suggestions instantanées dans l'overlay de recherche — */
  function bindOverlay(inputEl, listEl) {
    if (!inputEl || !listEl) return;
    var timer = null;
    inputEl.addEventListener('input', function () {
      clearTimeout(timer);
      var q = inputEl.value;
      timer = setTimeout(function () {
        if (normalize(q).trim().length < 2) { listEl.innerHTML = ''; return; }
        query(q).then(function (results) {
          listEl.innerHTML = results.slice(0, 5).map(function (e) {
            return '<li><a href="' + e.url + '">' +
              '<span class="sr-cat">' + e.cat + '</span>' +
              '<span class="sr-title">' + e.title + '</span></a></li>';
          }).join('');
        });
      }, 120);
    });
  }

  window.JDESearch = { load: load, query: query, normalize: normalize, bindOverlay: bindOverlay };
})();
