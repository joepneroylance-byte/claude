const API = '';  // same origin

// ── State ──────────────────────────────────────────────────────────────────
const state = { a: null, b: null };
let radarChart = null, goalsChart = null, defenseChart = null;

// ── League colours for charts ──────────────────────────────────────────────
const COLORS = {
  a: { border: '#38bdf8', bg: 'rgba(56,189,248,0.2)' },
  b: { border: '#f97316', bg: 'rgba(249,115,22,0.2)' },
};

// ── Boot ───────────────────────────────────────────────────────────────────
async function boot() {
  const leagues = await apiFetch('/api/leagues');
  ['a', 'b'].forEach(side => {
    const sel = document.getElementById(`league-${side}`);
    leagues.forEach(l => {
      const opt = document.createElement('option');
      opt.value = l.id;
      opt.textContent = l.name;
      sel.appendChild(opt);
    });
  });
  setupSearch('a');
  setupSearch('b');
}

// ── Search ─────────────────────────────────────────────────────────────────
function setupSearch(side) {
  const input = document.getElementById(`input-${side}`);
  const list = document.getElementById(`suggestions-${side}`);
  let debounce;

  input.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = input.value.trim();
    if (q.length < 2) { list.innerHTML = ''; list.classList.add('hidden'); return; }
    debounce = setTimeout(() => fetchSuggestions(side, q), 300);
  });

  document.addEventListener('click', e => {
    if (!e.target.closest(`#search-${side}`)) {
      list.innerHTML = '';
      list.classList.add('hidden');
    }
  });
}

async function fetchSuggestions(side, q) {
  const league = document.getElementById(`league-${side}`).value;
  const params = new URLSearchParams({ q });
  if (league) params.set('league_id', league);
  const results = await apiFetch(`/api/players/search?${params}`);
  renderSuggestions(side, results);
}

function renderSuggestions(side, players) {
  const list = document.getElementById(`suggestions-${side}`);
  list.innerHTML = '';
  if (!players.length) {
    list.classList.add('hidden');
    return;
  }
  players.slice(0, 8).forEach(p => {
    const li = document.createElement('li');
    li.innerHTML = `
      <img src="${p.photo || ''}" alt="" onerror="this.style.visibility='hidden'" />
      <div>
        <div>${p.name}</div>
        <div class="suggest-meta">${p.team || ''} · ${p.league || ''}</div>
      </div>`;
    li.addEventListener('click', () => selectPlayer(side, p));
    list.appendChild(li);
  });
  list.classList.remove('hidden');
}

async function selectPlayer(side, player) {
  const list = document.getElementById(`suggestions-${side}`);
  const input = document.getElementById(`input-${side}`);
  list.innerHTML = '';
  list.classList.add('hidden');
  input.value = player.name;

  const card = document.getElementById(`card-${side}`);
  card.innerHTML = '<div class="spinner"></div>';

  const leagueId = player.league_id || document.getElementById(`league-${side}`).value;
  const data = await apiFetch(`/api/players/${player.id}/stats?league_id=${leagueId}`);

  state[side] = data;
  renderCard(side, data);
  if (state.a && state.b) renderComparison();
}

// ── Player card ────────────────────────────────────────────────────────────
function renderCard(side, d) {
  const s = d.stats;
  const card = document.getElementById(`card-${side}`);
  card.innerHTML = `
    <div class="card-inner">
      <div class="card-photo">
        <img src="${d.photo || ''}" alt="${d.name}" onerror="this.src=''" />
      </div>
      <div class="card-info">
        <div class="card-name">${d.name}</div>
        <div class="card-meta">
          <span>${d.nationality || ''}</span>
          <span>Age ${d.age || '–'}</span>
          <span>${d.position || '–'}</span>
          ${d.height ? `<span>${d.height}</span>` : ''}
        </div>
        <div class="team-row">
          <img src="${d.team_logo || ''}" alt="" onerror="this.style.visibility='hidden'" />
          <span>${d.team || ''} · ${d.league || ''} ${d.season || ''}</span>
        </div>
        <div class="mini-stats">
          <div class="mini-stat"><div class="val">${s.appearances}</div><div class="lbl">Apps</div></div>
          <div class="mini-stat"><div class="val">${s.goals}</div><div class="lbl">Goals</div></div>
          <div class="mini-stat"><div class="val">${s.assists}</div><div class="lbl">Assists</div></div>
          <div class="mini-stat"><div class="val">${s.avg_rating ?? '–'}</div><div class="lbl">Rating</div></div>
          <div class="mini-stat"><div class="val">${s.minutes}</div><div class="lbl">Mins</div></div>
        </div>
      </div>
    </div>`;
}

// ── Comparison ─────────────────────────────────────────────────────────────
function renderComparison() {
  document.getElementById('comparison').hidden = false;
  document.getElementById('th-a').textContent = state.a.name;
  document.getElementById('th-b').textContent = state.b.name;
  renderRadar();
  renderGoalsChart();
  renderDefenseChart();
  renderStatTable();
}

function renderRadar() {
  const a = state.a.stats, b = state.b.stats;
  const labels = ['Goals', 'Assists', 'Key Passes', 'Dribbles %', 'Tackles', 'Interceptions'];
  const valA = [a.goals, a.assists, a.passes_key, a.dribble_success_pct ?? 0, a.tackles, a.interceptions];
  const valB = [b.goals, b.assists, b.passes_key, b.dribble_success_pct ?? 0, b.tackles, b.interceptions];

  if (radarChart) radarChart.destroy();
  radarChart = new Chart(document.getElementById('radar-chart'), {
    type: 'radar',
    data: {
      labels,
      datasets: [
        { label: state.a.name, data: valA, borderColor: COLORS.a.border, backgroundColor: COLORS.a.bg, pointBackgroundColor: COLORS.a.border },
        { label: state.b.name, data: valB, borderColor: COLORS.b.border, backgroundColor: COLORS.b.bg, pointBackgroundColor: COLORS.b.border },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: '#8b949e', font: { size: 11 } } } },
      scales: {
        r: {
          ticks: { color: '#8b949e', backdropColor: 'transparent', font: { size: 10 } },
          grid: { color: '#30363d' },
          pointLabels: { color: '#e6edf3', font: { size: 11 } },
          angleLines: { color: '#30363d' },
        },
      },
    },
  });
}

function renderGoalsChart() {
  const a = state.a.stats, b = state.b.stats;
  const labels = ['Goals', 'Assists', 'Shots', 'On Target', 'Pen Scored'];
  const valA = [a.goals, a.assists, a.shots_total, a.shots_on_target, a.penalties_scored];
  const valB = [b.goals, b.assists, b.shots_total, b.shots_on_target, b.penalties_scored];

  if (goalsChart) goalsChart.destroy();
  goalsChart = new Chart(document.getElementById('goals-chart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: state.a.name, data: valA, backgroundColor: COLORS.a.bg, borderColor: COLORS.a.border, borderWidth: 1.5, borderRadius: 4 },
        { label: state.b.name, data: valB, backgroundColor: COLORS.b.bg, borderColor: COLORS.b.border, borderWidth: 1.5, borderRadius: 4 },
      ],
    },
    options: barOptions(),
  });
}

function renderDefenseChart() {
  const a = state.a.stats, b = state.b.stats;
  const labels = ['Tackles', 'Interceptions', 'Blocks', 'Duels Won', 'Fouls Committed'];
  const valA = [a.tackles, a.interceptions, a.blocks, a.duels_won, a.fouls_committed];
  const valB = [b.tackles, b.interceptions, b.blocks, b.duels_won, b.fouls_committed];

  if (defenseChart) defenseChart.destroy();
  defenseChart = new Chart(document.getElementById('defense-chart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: state.a.name, data: valA, backgroundColor: COLORS.a.bg, borderColor: COLORS.a.border, borderWidth: 1.5, borderRadius: 4 },
        { label: state.b.name, data: valB, backgroundColor: COLORS.b.bg, borderColor: COLORS.b.border, borderWidth: 1.5, borderRadius: 4 },
      ],
    },
    options: barOptions(),
  });
}

function barOptions() {
  return {
    responsive: true,
    plugins: { legend: { labels: { color: '#8b949e', font: { size: 11 } } } },
    scales: {
      x: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#30363d' } },
      y: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#30363d' } },
    },
  };
}

// ── Stat table ─────────────────────────────────────────────────────────────
const STAT_GROUPS = [
  {
    label: 'General',
    rows: [
      ['Appearances', 'appearances', false],
      ['Lineups (starts)', 'lineups', false],
      ['Minutes played', 'minutes', false],
      ['Avg. rating', 'avg_rating', true],
    ],
  },
  {
    label: 'Attacking',
    rows: [
      ['Goals', 'goals', true],
      ['Assists', 'assists', true],
      ['Shots (total)', 'shots_total', true],
      ['Shots on target', 'shots_on_target', true],
      ['Shot accuracy %', 'shot_accuracy_pct', true],
      ['Mins per goal', 'mins_per_goal', false],
      ['Penalties scored', 'penalties_scored', true],
      ['Penalties missed', 'penalties_missed', false],
    ],
  },
  {
    label: 'Passing',
    rows: [
      ['Passes (total)', 'passes_total', true],
      ['Key passes', 'passes_key', true],
      ['Pass accuracy %', 'pass_accuracy_pct', true],
    ],
  },
  {
    label: 'Dribbling & Duels',
    rows: [
      ['Dribble attempts', 'dribbles_attempts', true],
      ['Dribbles completed', 'dribbles_success', true],
      ['Dribble success %', 'dribble_success_pct', true],
      ['Duels (total)', 'duels_total', false],
      ['Duels won', 'duels_won', true],
      ['Duel win %', 'duel_win_pct', true],
    ],
  },
  {
    label: 'Defensive',
    rows: [
      ['Tackles', 'tackles', true],
      ['Interceptions', 'interceptions', true],
      ['Blocks', 'blocks', true],
      ['Fouls drawn', 'fouls_drawn', true],
      ['Fouls committed', 'fouls_committed', false],
    ],
  },
  {
    label: 'Discipline',
    rows: [
      ['Yellow cards', 'yellow_cards', false],
      ['Red cards', 'red_cards', false],
    ],
  },
];

function renderStatTable() {
  const tbody = document.getElementById('stat-body');
  tbody.innerHTML = '';
  const sa = state.a.stats, sb = state.b.stats;

  STAT_GROUPS.forEach(group => {
    const hdr = document.createElement('tr');
    hdr.className = 'stat-group-header';
    hdr.innerHTML = `<td colspan="3">${group.label}</td>`;
    tbody.appendChild(hdr);

    group.rows.forEach(([label, key, higherIsBetter]) => {
      const va = sa[key] ?? null;
      const vb = sb[key] ?? null;
      const tr = document.createElement('tr');

      let tdA = `<td>${fmt(va)}</td>`;
      let tdB = `<td>${fmt(vb)}</td>`;

      if (va !== null && vb !== null && va !== vb && higherIsBetter) {
        if (va > vb) tdA = `<td class="winner">${fmt(va)}</td>`;
        else tdB = `<td class="winner">${fmt(vb)}</td>`;
      }

      tr.innerHTML = `<td>${label}</td>${tdA}${tdB}`;
      tbody.appendChild(tr);
    });
  });
}

function fmt(v) {
  if (v === null || v === undefined) return '–';
  return v;
}

// ── Util ───────────────────────────────────────────────────────────────────
async function apiFetch(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

boot();
