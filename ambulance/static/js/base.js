// Navigation active highlight
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    link.classList.add('active');
  });
});

// Soft ambient background animation
const DOT = '#38bdf8'; // healthcare blue
const MIN_R = 0.5;
const MAX_R = 1.2;
const COUNT = 90;

const canvas = document.getElementById('stars');
const ctx = canvas.getContext('2d', { alpha: true });

function draw() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const dpr = window.devicePixelRatio || 1;

  canvas.width = Math.floor(w * dpr);
  canvas.height = Math.floor(h * dpr);
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  ctx.clearRect(0, 0, w, h);

  for (let i = 0; i < COUNT; i++) {
    const r = MIN_R + Math.random() * (MAX_R - MIN_R);
    const x = Math.random() * w;
    const y = Math.random() * h;
    const alpha = 0.25 + Math.random() * 0.3;
    ctx.fillStyle = `rgba(56, 189, 248, ${alpha})`; // light blue dots
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
}

let t;
window.addEventListener('resize', () => {
  clearTimeout(t);
  t = setTimeout(draw, 150);
});

draw();
