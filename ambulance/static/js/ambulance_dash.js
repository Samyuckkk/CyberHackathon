(function(){
  // Vitals simulation
  const ecgEl = document.getElementById('ecg');
  const spo2El = document.getElementById('spo2');
  const nibpEl = document.getElementById('nibp');
  const rrEl = document.getElementById('rr');
  const tempEl = document.getElementById('temp');
  const statusEl = document.getElementById('vitalStatus');
  const aiCategoryEl = document.getElementById('aiCategory');
  const ai_spo2 = document.getElementById('ai_spo2');
  const ai_nibp = document.getElementById('ai_nibp');
  const ai_ecg = document.getElementById('ai_ecg');

  function randBetween(min,max){ return Math.round((Math.random()*(max-min))+min); }

  function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


  // start with realistic baseline
  let vitals = {
    ecg: 'Normal',
    spo2: 97,
    nibp_sys: 120,
    nibp_dia: 78,
    rr: 16,
    temp: 36.8
  };

  function updateVitals(){
    // small random drift
    vitals.spo2 = Math.max(80, Math.min(100, vitals.spo2 + (Math.random()*2-1)));
    vitals.nibp_sys = Math.max(80, Math.min(160, vitals.nibp_sys + Math.round(Math.random()*3-2)));
    vitals.nibp_dia = Math.max(50, Math.min(110, vitals.nibp_dia + Math.round(Math.random()*3-2)));
    vitals.rr = Math.max(8, Math.min(30, Math.round(vitals.rr + (Math.random()*2-1))));
    vitals.temp = Math.round((vitals.temp + (Math.random()*0.18-0.09))*10)/10;

    // occasionally flip ECG
    if(Math.random() < 0.06) vitals.ecg = (vitals.ecg === 'Normal') ? 'Irregular' : 'Normal';

    // push to DOM
    ecgEl.textContent = vitals.ecg;
    spo2El.textContent = vitals.spo2.toFixed(1) + '%';
    nibpEl.textContent = vitals.nibp_sys + '/' + vitals.nibp_dia + ' mmHg';
    rrEl.textContent = vitals.rr + ' /min';
    tempEl.textContent = vitals.temp + ' °C';

    // AI field mirrors
    ai_spo2.textContent = vitals.spo2.toFixed(1) + '%';
    ai_nibp.textContent = vitals.nibp_sys + '/' + vitals.nibp_dia;
    ai_ecg.textContent = vitals.ecg;

    // decide status
    let critical = (vitals.spo2 < 92) || (vitals.nibp_sys < 90) || (vitals.nibp_sys > 150) || vitals.ecg === 'Irregular';
    if(critical){
      statusEl.classList.remove('noncritical'); statusEl.classList.add('critical'); statusEl.textContent = 'Critical'; aiCategoryEl.textContent = 'Critical';
    } else {
      statusEl.classList.remove('critical'); statusEl.classList.add('noncritical'); statusEl.textContent = 'Stable'; aiCategoryEl.textContent = 'Stable';
    }

    // send vitals to backend
// send vitals securely (Hybrid PQC prototype)
// Secure vitals send
fetch('/api/update-vitals-secure/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken'),
  },
  body: JSON.stringify({
    ambulance_id: window.currentUser, // || 'ambulance1@gmail.com',  // 👈 Add this
    ecg: vitals.ecg,
    spo2: vitals.spo2.toFixed(1),
    nibp: vitals.nibp_sys + '/' + vitals.nibp_dia,
    rr: vitals.rr,
    temp: vitals.temp,
    status: statusEl.textContent
  })
})
  .then(res => res.json())
  .then(data => console.log('✅ Sent secure vitals:', data))
  .catch(err => console.error('❌ Error sending secure vitals:', err));


  }

  // run updates every 1.5s
  updateVitals();
  setInterval(updateVitals, 1500);

  // Symptoms add/remove logic
  const symptomInput = document.getElementById('symptomInput');
  const addSymptomBtn = document.getElementById('addSymptomBtn');
  const symptomList = document.getElementById('symptomList');

  function createSymptomPill(text){
    const pill = document.createElement('div');
    pill.className = 'symptom-pill';
    pill.innerHTML = `<div class="symptom-text">${text}</div><button class="remove">✕</button>`;
    pill.querySelector('.remove').addEventListener('click', ()=> pill.remove());
    return pill;
  }

  addSymptomBtn.addEventListener('click', ()=>{
    const txt = symptomInput.value && symptomInput.value.trim();
    if(!txt) return;
    const p = createSymptomPill(txt);
    symptomList.prepend(p);
    symptomInput.value = '';
  });

  symptomInput.addEventListener('keydown', (e)=>{ if(e.key === 'Enter') addSymptomBtn.click(); });

  // ETA simulation: start at 12 minutes and decrease
  let etaSeconds = 12*60; // 12 minutes
  const etaEl = document.getElementById('eta');
  function formatMMSS(s){ const m = Math.floor(s/60); const r = s%60; return `${String(m).padStart(2,'0')}:${String(r).padStart(2,'0')}`; }
  etaEl.textContent = formatMMSS(etaSeconds);
  setInterval(()=>{
    if(etaSeconds>0) etaSeconds--; etaEl.textContent = formatMMSS(etaSeconds);
  },1000);

  // Open maps link (example center coords) - replace with real ambulance/hospital coords
  const openMapsLink = document.getElementById('openMapsLink');
  const hospitalLat = 18.5204; const hospitalLng = 73.8567; // Pune fallback
  const ambulanceLat = 18.507; const ambulanceLng = 73.851; // simulated
  openMapsLink.href = `https://www.google.com/maps/dir/?api=1&origin=${ambulanceLat},${ambulanceLng}&destination=${hospitalLat},${hospitalLng}&travelmode=driving`;

  // Contact buttons (dummy actions)
  document.getElementById('callER').addEventListener('click', ()=> alert('Calling Emergency: +91-xxxxxxxxxx'));
  document.getElementById('msgTT').addEventListener('click', ()=> alert('ETA and notes sent to hospital.'));
  document.getElementById('shareLoc').addEventListener('click', ()=> alert('Location shared with hospital.'));

  // Expand button placeholder - you could wire this to open a modal similar to hospital dash expand
  document.getElementById('openExpand').addEventListener('click', ()=>{
    document.querySelector('.dash-full-block').classList.toggle('expanded');
  });

})();
