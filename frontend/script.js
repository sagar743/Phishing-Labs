// Frontend is served by the same Flask server as the API, so relative
// paths work regardless of host/port - no CORS or file:// issues.
const API_BASE_URL = "";

// ---------- Home page: submit URL for analysis ----------
const scanForm = document.getElementById('scan-form');
if (scanForm) {
  scanForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const urlInput = document.getElementById('url-input');
    const errorEl = document.getElementById('scan-error');
    const submitBtn = scanForm.querySelector('button');
    errorEl.textContent = '';

    const url = urlInput.value.trim();
    if (!url) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyzing...';

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || 'Something went wrong');
      }

      const result = await response.json();
      localStorage.setItem('lastScanResult', JSON.stringify(result));
      window.location.href = 'result.html';

    } catch (err) {
      errorEl.textContent = err.message || 'Could not reach the server. Is the Flask API running?';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Analyze URL';
    }
  });
}

// ---------- Result page: display last scan result ----------
const predictionEl = document.getElementById('prediction-text');
if (predictionEl) {
  const raw = localStorage.getItem('lastScanResult');

  if (!raw) {
    document.querySelector('main').innerHTML =
      '<h1>No scan result found</h1><p><a href="index.html">Go back and scan a URL</a></p>';
  } else {
    const result = JSON.parse(raw);

    document.getElementById('result-url').textContent = result.url;

    predictionEl.textContent = result.prediction;
    predictionEl.classList.add(result.prediction === 'PHISHING' ? 'phishing' : 'legitimate');

    document.getElementById('risk-score').textContent = `${result.risk_score}/100`;
    document.getElementById('confidence').textContent = `${result.confidence}%`;

    const f = result.features;
    document.getElementById('f-url-length').textContent = f.url_length;
    document.getElementById('f-https').textContent = f.has_https ? 'Yes' : 'No';
    document.getElementById('f-ip').textContent = f.has_ip ? 'Yes' : 'No';
    document.getElementById('f-dots').textContent = f.num_dots;
    document.getElementById('f-hyphens').textContent = f.num_hyphens;
    document.getElementById('f-special').textContent = f.num_special_chars;
    document.getElementById('f-subdomains').textContent = f.num_subdomains;

    const reasonsList = document.getElementById('reasons-list');
    reasonsList.innerHTML = '';
    result.reasons.forEach(reason => {
      const li = document.createElement('li');
      li.textContent = reason;
      reasonsList.appendChild(li);
    });
  }
}

// ---------- History page: load and display scans ----------
const historyBody = document.getElementById('history-body');
if (historyBody) {
  fetch(`${API_BASE_URL}/api/history`)
    .then(res => res.json())
    .then(scans => {
      if (!scans.length) {
        historyBody.innerHTML = '<tr><td colspan="5">No scans yet.</td></tr>';
        return;
      }
      historyBody.innerHTML = scans.map(scan => `
        <tr>
          <td>${scan.url}</td>
          <td>${scan.prediction}</td>
          <td>${scan.risk_score}/100</td>
          <td>${scan.confidence}%</td>
          <td>${scan.timestamp}</td>
        </tr>
      `).join('');
    })
    .catch(() => {
      historyBody.innerHTML = '<tr><td colspan="5">Could not load history. Is the server running?</td></tr>';
    });
}
