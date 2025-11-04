console.log("✅ hospital_dash.js loaded");

// Function to update vitals dynamically
function refreshVitals() {
  console.log("Fetching vitals...");
  fetch('/api/get-vitals/')
    .then(res => res.json())
    .then(data => {
      data.forEach(v => {
        const block = document.querySelector(`.dash-block[data-username="${v.username}"]`);
        if (!block) {
          console.warn(`⚠️ No block found for ${v.username}`);
          return;
        }

        const ecgEl = block.querySelector('.v-ekg .value');
        const spo2El = block.querySelector('.v-spo2 .value');
        const nibpEl = block.querySelector('.v-nibp .value');
        const rrEl = block.querySelector('.v-rr .value');
        const tempEl = block.querySelector('.v-temp .value');
        const statusEl = block.querySelector('.status');

        // Update vitals or show '--' if inactive
        if (v.status === 'Inactive') {
          ecgEl.textContent = '--';
          spo2El.textContent = '--';
          nibpEl.textContent = '--';
          rrEl.textContent = '--';
          tempEl.textContent = '--';
        } else {
          ecgEl.textContent = v.ecg ?? '--';
          spo2El.textContent = v.spo2 ? `${v.spo2}%` : '--';
          nibpEl.textContent = v.nibp ?? '--';
          rrEl.textContent = v.rr ?? '--';
          tempEl.textContent = v.temp ? `${v.temp}°C` : '--';
        }

        // Update status text and color
        statusEl.textContent = v.status || 'Inactive';
        statusEl.className = 'status ' + (v.status === 'Critical' ? 'critical' : 'noncritical');
      });
    })
    .catch(err => console.error('Error fetching vitals:', err));
}

// Refresh every 2 seconds
setInterval(refreshVitals, 2000);
refreshVitals();
