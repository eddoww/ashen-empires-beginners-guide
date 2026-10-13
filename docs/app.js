// The menu on a narrow screen, the quest search, the picture viewer, and the checklist that remembers its ticks.
(function () {
  var names = { index: 'Start', valinor: 'Valinor', mainland: 'Mainland', krog: 'Krog', silvest: 'Silvest',
    whisperdale: 'Whisperdale', gear: 'Gear', after: 'After 25', level40: 'Level 40+', howto: 'How do I', trades: 'Trades', tradesgear: 'Gear trades', tradesrest: 'Potions and food', followers: 'Followers', basics: 'Basics', about: 'Sources' };

  document.getElementById('menu').onclick = function () { document.body.classList.toggle('open'); };
  document.getElementById('nav').onclick = function (e) { if (e.target.tagName === 'A') document.body.classList.remove('open'); };

  // Search: quests first, then headings; every word typed has to be in the name.
  var find = document.getElementById('find'), found = document.getElementById('found'), on = -1;
  function search() {
    var words = find.value.toLowerCase().split(/\s+/).filter(Boolean);
    found.innerHTML = ''; on = -1;
    if (!words.length) return;
    var hits = QUESTS.filter(function (q) {
      var name = q.n.toLowerCase();
      return words.every(function (w) { return name.indexOf(w) >= 0; });
    }).sort(function (a, b) { return (a.h || 0) - (b.h || 0); }).slice(0, 14);
    hits.forEach(function (q) {
      var li = document.createElement('li'), a = document.createElement('a'), small = document.createElement('small');
      a.href = q.p + '.html#' + q.a;
      a.textContent = q.n;
      small.textContent = names[q.p] + (q.l ? ', level ' + q.l : '');
      a.appendChild(small); li.appendChild(a); found.appendChild(li);
    });
  }
  find.oninput = search;
  find.onkeydown = function (e) {
    var links = found.querySelectorAll('a');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (links[on]) links[on].classList.remove('on');
      on = (on + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
      if (links[on]) links[on].classList.add('on');
    } else if (e.key === 'Enter' && links.length) {
      location.href = (links[on] || links[0]).href; find.value = ''; found.innerHTML = '';
    } else if (e.key === 'Escape') { find.value = ''; found.innerHTML = ''; }
  };
  document.addEventListener('click', function (e) { if (!e.target.closest('.find')) found.innerHTML = ''; });
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== find) { e.preventDefault(); find.focus(); }
  });

  // A quest reached by its link: open its pictures' row if it has one.
  function arrive() {
    var row = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (row && row.tagName === 'TR') row.scrollIntoView({ block: 'center' });
  }
  window.addEventListener('hashchange', arrive); arrive();

  // The picture viewer: the pictures of one group, with the arrow keys.
  var box = document.getElementById('box'), big = box.querySelector('img'), line = box.querySelector('p'), group = [], at = 0;
  function show(i) {
    at = (i + group.length) % group.length;
    var pic = group[at];
    big.src = pic.href;
    line.textContent = (pic.title || '') + ' ';
    var a = document.createElement('a');
    a.href = pic.dataset.page; a.textContent = pic.dataset.credit; a.target = '_blank'; a.rel = 'noopener';
    line.appendChild(document.createTextNode('(from ')); line.appendChild(a); line.appendChild(document.createTextNode(')'));
    box.hidden = false;
  }
  document.addEventListener('click', function (e) {
    var pic = e.target.closest('.pic');
    if (!pic) return;
    e.preventDefault();
    group = Array.prototype.slice.call(pic.parentNode.querySelectorAll('.pic'));
    show(group.indexOf(pic));
  });
  document.getElementById('shut').onclick = function () { box.hidden = true; };
  document.getElementById('prev').onclick = function () { show(at - 1); };
  document.getElementById('next').onclick = function () { show(at + 1); };
  box.onclick = function (e) { if (e.target === box) box.hidden = true; };
  document.addEventListener('keydown', function (e) {
    if (box.hidden) return;
    if (e.key === 'Escape') box.hidden = true;
    if (e.key === 'ArrowLeft') show(at - 1);
    if (e.key === 'ArrowRight') show(at + 1);
  });

  // The checklist keeps its ticks in this browser.
  Array.prototype.forEach.call(document.querySelectorAll('li.tick input'), function (input, i) {
    var key = 'tick:' + location.pathname + ':' + i;
    try { input.checked = localStorage.getItem(key) === '1'; } catch (e) {}
    input.onchange = function () { try { localStorage.setItem(key, input.checked ? '1' : '0'); } catch (e) {} };
  });
})();
