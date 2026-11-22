function getGrade(score) {
  if (score >= 90) return { letter: 'S', cls: 's-color' };
  if (score >= 75) return { letter: 'A', cls: 'a-color' };
  if (score >= 60) return { letter: 'B', cls: 'b-color' };
  if (score >= 45) return { letter: 'C', cls: 'c-color' };
  return { letter: 'D', cls: 'd-color' };
}

function formatStatName(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}

function formatNumber(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return value ?? 'N/A';
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

function buildMatchCard(match) {
  const overall = match.overall ?? match.total_score ?? 0;
  const grade = getGrade(overall);
  const breakdown = match.breakdown ?? {};
  const stats = match.stats ?? {};
  const displayStats = Object.entries(stats).filter(
    ([key]) => !['win', 'role', 'champion', 'duration_minutes'].includes(key)
  );

  const rows = displayStats.map(([key, raw]) => {
    const result = breakdown[key];
    const statGrade = result ? getGrade(result.score) : null;
    return `
      <tr>
        <td class="stat-name">${formatStatName(key)}</td>
        <td>${formatNumber(raw)}</td>
        <td>
          ${result ? `
            <div class="score-bar-wrap">
              <div class="score-bar">
                <div class="score-bar-fill ${statGrade.cls}" style="width:${result.score}%; background:currentColor;"></div>
              </div>
              <span class="score-val ${statGrade.cls}">${formatNumber(result.score)}</span>
            </div>
          ` : '<span class="unscored">Not scored</span>'}
        </td>
        <td style="color:var(--text-dim)">${result ? `${formatNumber(result.weight)}%` : '—'}</td>
      </tr>`;
  }).join('');

  //header: show champion, kda, duration, overall score, and win/loss if server sent info 
  const hasResult = typeof match.win === 'boolean';
  const badge = hasResult ? 
  `<span class="win-badge ${match.win ? 'win' : 'loss'}">${match.win ? 'WIN' : 'LOSS'}</span>`
    : '';

  const title = match.champion ?? match.match_id ?? 'Unknown Champion';
  const kda = match.kills !== undefined && match.deaths !== undefined && match.assists !== undefined
    ? `${match.kills}/${match.deaths}/${match.assists}`
    : 'N/A';
  const duration = match.duration_mins !== undefined ? `${formatNumber(match.duration_mins)}m` : 'N/A';

  return `
    <div class="match-card">
      <div class="card-header" onclick="toggleCard(this)">
        ${badge}
        <span class="card-champion">${title}</span>
        <span class="card-kda">
          <span>${kda}</span>
          &nbsp;·&nbsp;${duration}${match.role ? ` · ${formatStatName(match.role)}` : ''}
        </span>
        <span class="overall-score ${grade.cls}">${formatNumber(overall)}</span>
        <span class="card-chevron">▼</span>
      </div>
      <div class="card-body">
        <table class="breakdown-table">
          <thead>
            <tr>
              <th>Constraint</th>
              <th>Value</th>
              <th>Score</th>
              <th>Weight</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

function toggleCard(header) {
  const body    = header.nextElementSibling;
  const chevron = header.querySelector('.card-chevron');
  body.classList.toggle('open');
  chevron.classList.toggle('open');
}

async function runAnalysis() {
  const raw   = document.getElementById('summoner-input').value.trim();
  const games = document.getElementById('games-select').value;
  const btn   = document.getElementById('search-button');
  const out   = document.getElementById('results');

  if (!raw.includes('#')) {
    out.innerHTML = `<p class="state-msg error">Enter your Riot ID in Name#TAG format.</p>`;
    out.classList.remove('hidden');
    return;
  }

  const [name, tag] = raw.split('#');
  btn.disabled = true;
  out.classList.remove('hidden');
  out.innerHTML = `<p class="state-msg">Fetching ${games} ranked games for ${raw}…</p>`;

  try {
    const res  = await fetch(`/api/analyze/${encodeURIComponent(name)}/${encodeURIComponent(tag)}?games=${games}`);
    const data = await res.json();

    if (!res.ok) {
      out.innerHTML = `<p class="state-msg error">${data.detail || 'Something went wrong.'}</p>`;
      return;
    }

    if (!data.matches.length) {
      out.innerHTML = `<p class="state-msg">No ranked games found for ${raw}.</p>`;
      return;
    }

    const avg = (data.matches.reduce((s, m) => s + (m.overall ?? m.total_score ?? 0), 0) / data.matches.length).toFixed(2);
    const g   = getGrade(parseFloat(avg));

    out.innerHTML = `
      <div class="summoner-header">
        ${data.summoner}
        <span>— avg score <span class="${g.cls}">${avg} (${g.letter})</span> over ${data.matches.length} games</span>
      </div>
      ${data.matches.map(buildMatchCard).join('')}`;

  } catch (err) {
    console.error("runAnalysis failed:", err);
    out.innerHTML = `<p class="state-msg error">${err.name}: ${err.message}</p>`;
  } finally {
    btn.disabled = false;
  }
}

document.getElementById('summoner-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') runAnalysis(); 
});