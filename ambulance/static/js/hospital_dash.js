function refreshVitals() {
  fetch('/api/get-vitals/')
    .then(res => res.json())
    .then(data => {
      data.forEach((v, i) => {
        const block = document.querySelectorAll('.dash-block')[i];
        if (!block) return;
        block.querySelector('.v-ekg .value').textContent = v.ecg;
        block.querySelector('.v-spo2 .value').textContent = v.spo2 + '%';
        block.querySelector('.v-nibp .value').textContent = v.nibp;
        block.querySelector('.v-rr .value').textContent = v.rr;
        block.querySelector('.v-temp .value').textContent = v.temp + '°C';
        const statusEl = block.querySelector('.status');
        statusEl.textContent = v.status;
        statusEl.className = 'status ' + (v.status === 'Critical' ? 'critical' : 'noncritical');
      });
    })
    .catch(err => console.error('Error fetching vitals:', err));
}

setInterval(refreshVitals, 2000); // every 2 seconds
refreshVitals();

