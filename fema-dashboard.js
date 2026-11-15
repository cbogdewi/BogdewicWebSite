const status = document.getElementById('status');

function addBars(targetId, rows, labelKey, limit = 10) {
  const target = document.getElementById(targetId);
  target.replaceChildren();
  const shown = rows.slice(0, limit);
  const max = Math.max(1, ...shown.map(row => Number(row.count) || 0));
  for (const row of shown) {
    const line = document.createElement('div');
    line.className = 'bar-row';
    const label = document.createElement('span');
    label.textContent = row[labelKey];
    const track = document.createElement('span');
    track.className = 'track';
    const fill = document.createElement('span');
    fill.className = 'fill';
    fill.style.width = `${Math.max(1, (Number(row.count) / max) * 100)}%`;
    track.append(fill);
    const count = document.createElement('strong');
    count.textContent = Number(row.count).toLocaleString();
    line.append(label, track, count);
    target.append(line);
  }
  if (!shown.length) target.textContent = 'No summary data available.';
}

function textCell(value) {
  const cell = document.createElement('td');
  cell.textContent = value || '—';
  return cell;
}

async function loadReport() {
  try {
    const response = await fetch('data/fema-disasters.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Report not found (HTTP ${response.status}). The first scheduled/manual pipeline run may not have completed yet.`);
    const data = await response.json();
    document.getElementById('total').textContent = Number(data.recordCount).toLocaleString();
    document.getElementById('states-total').textContent = data.states.length.toLocaleString();
    document.getElementById('generated').textContent = new Date(data.generatedAt).toLocaleDateString(undefined, { timeZone: 'UTC', year: 'numeric', month: 'short', day: 'numeric' });
    addBars('types', data.incidentTypes, 'name');
    addBars('states', data.states, 'name', 15);
    const body = document.getElementById('latest');
    body.replaceChildren();
    for (const row of data.latest) {
      const tr = document.createElement('tr');
      tr.append(
        textCell(new Date(row.declarationDate).toLocaleDateString()),
        textCell(row.disasterNumber),
        textCell(row.state),
        textCell(row.incidentType),
        textCell([row.declarationTitle, row.designatedArea].filter(Boolean).join(' — ')),
      );
      body.append(tr);
    }
    status.textContent = `Loaded ${Number(data.recordCount).toLocaleString()} valid unique records; ${Number(data.rejectedCount).toLocaleString()} records failed validation. Generated ${new Date(data.generatedAt).toUTCString()}.`;
  } catch (error) {
    status.classList.add('error');
    status.textContent = error.message;
  }
}

loadReport();
