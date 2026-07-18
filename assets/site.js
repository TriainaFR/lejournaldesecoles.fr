/* Le Journal des Écoles - comportements communs légers.
   Date d'édition en direct : le HTML embarque une date statique (lisible par
   les crawlers) que ce script remplace par la date du jour du visiteur. */
(function () {
  'use strict';
  var el = document.getElementById('edition-date');
  if (!el) return;
  try {
    var s = new Intl.DateTimeFormat('fr-FR', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    }).format(new Date());
    el.textContent = s.charAt(0).toUpperCase() + s.slice(1);
    el.setAttribute('data-live', '1');
  } catch (e) { /* la date statique reste affichée */ }
})();
