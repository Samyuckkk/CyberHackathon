    // Navigation link activation
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        link.classList.add('active');
      });
    });

    const DOT = '#000000';
    const MIN_R = 0.4;  // very small radius in CSS px
    const MAX_R = 0.9;  // very small radius in CSS px
    const COUNT = 0;   // approximately 80 dots

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
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); // draw in CSS pixels

      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = DOT;

      for (let i = 0; i < COUNT; i++) {
        const r = MIN_R + Math.random() * (MAX_R - MIN_R);
        const x = Math.random() * w;
        const y = Math.random() * h;

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