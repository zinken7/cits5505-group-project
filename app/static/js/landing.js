/**
 * WatchList Hub — Three.js Cinematic Landing Page
 *
 * Flow:
 *   1. Load poster image URLs from /api/v1/landing/posters
 *   2. Build vertical scrolling columns of poster planes
 *   3. Accelerate columns → explosion → reveal hero card + nav
 */

(function () {
  "use strict";

  /* ================================================================
     CONFIG
     ================================================================ */
  const CFG = {
    // Columns
    NUM_COLS: 9,
    POSTERS_PER_COL: 10,
    POSTER_W: 1.8,
    POSTER_H: 2.7,
    GAP: 0.35,
    COL_GAP: 0.3,

    // Scroll speeds (base — each column gets a random multiplier)
    BASE_SPEED: 0.4,
    SPEED_VARIANCE: 0.6,

    // Phase timing (seconds)
    SCROLL_DURATION: 5.0,     // normal scrolling
    ACCEL_DURATION: 2.5,      // accelerating phase
    EXPLODE_TIME: 7.5,        // SCROLL + ACCEL durations
    POST_EXPLODE_DELAY: 1.2,  // delay before UI appears

    // Explosion
    NUM_PARTICLES: 600,
    SHOCKWAVE_SPEED: 18,

    // Camera
    CAM_Z: 8,
  };

  /* ================================================================
     GLOBALS
     ================================================================ */
  let scene, camera, renderer, clock;
  let columns = [];            // { group, speed, dir, posters[] }
  let particles = null;        // Points object
  let particleData = [];       // per-particle velocity etc.
  let shockwaveRing = null;
  let phase = "loading";       // loading → scrolling → accelerating → exploding → done
  let phaseTime = 0;
  let heroMedia = null;        // the featured media item (random pick)
  let posterTextures = [];     // loaded THREE.Texture[]
  let mediaList = [];          // raw API data

  /* ================================================================
     INIT
     ================================================================ */
  async function init() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050507);
    scene.fog = new THREE.Fog(0x050507, 6, 18);

    // Camera
    camera = new THREE.PerspectiveCamera(
      55,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    );
    camera.position.z = CFG.CAM_Z;

    // Renderer
    const canvas = document.getElementById("landing-canvas");
    renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    clock = new THREE.Clock();

    // Ambient light
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.4);
    dirLight.position.set(0, 5, 5);
    scene.add(dirLight);

    window.addEventListener("resize", onResize);

    // Fetch posters
    try {
      const res = await fetch("/api/v1/landing/posters");
      mediaList = await res.json();
    } catch (e) {
      console.warn("Failed to fetch posters, using placeholder", e);
      mediaList = [];
    }

    if (mediaList.length === 0) {
      // Fallback: skip to done
      showUI();
      return;
    }

    // Pick a random hero
    heroMedia = mediaList[Math.floor(Math.random() * mediaList.length)];

    // Load textures with progress reporting
    await loadTextures();

    // Dismiss loading screen
    dismissLoadingScreen();

    // Build columns
    buildColumns();

    // Start animation
    phase = "scrolling";
    phaseTime = 0;
    animate();
  }

  /* ================================================================
     TEXTURE LOADING
     ================================================================ */
  function loadTextures() {
    return new Promise((resolve) => {
      const loader = new THREE.TextureLoader();
      loader.crossOrigin = "anonymous";

      let loaded = 0;
      const total = mediaList.length;

      function onProgress() {
        loaded++;
        updateLoadingProgress(loaded, total);
        if (loaded >= total) resolve();
      }

      mediaList.forEach((item, i) => {
        loader.load(
          item.image_url,
          (tex) => {
            tex.minFilter = THREE.LinearFilter;
            tex.magFilter = THREE.LinearFilter;
            posterTextures[i] = tex;
            onProgress();
          },
          undefined,
          () => {
            // On error, create a colored placeholder
            posterTextures[i] = createPlaceholderTexture();
            onProgress();
          }
        );
      });

      // Safety timeout — don't wait forever
      setTimeout(resolve, 12000);
    });
  }

  /* ================================================================
     LOADING SCREEN
     ================================================================ */
  function updateLoadingProgress(loaded, total) {
    const pct = Math.round((loaded / total) * 100);
    const bar = document.getElementById("loading-bar");
    const label = document.getElementById("loading-percent");
    if (bar) bar.style.width = pct + "%";
    if (label) label.textContent = pct + "%";
  }

  function dismissLoadingScreen() {
    const screen = document.getElementById("loading-screen");
    if (!screen) return;
    // Ensure bar hits 100%
    updateLoadingProgress(1, 1);
    // Small delay so user sees 100%
    setTimeout(() => {
      screen.classList.add("fade-out");
      // Remove from DOM after transition
      setTimeout(() => screen.remove(), 700);
    }, 300);
  }

  function createPlaceholderTexture() {
    const c = document.createElement("canvas");
    c.width = 128;
    c.height = 192;
    const ctx = c.getContext("2d");
    const hue = Math.random() * 360;
    ctx.fillStyle = `hsl(${hue}, 40%, 18%)`;
    ctx.fillRect(0, 0, 128, 192);
    const tex = new THREE.CanvasTexture(c);
    return tex;
  }

  /* ================================================================
     BUILD COLUMNS
     ================================================================ */
  function buildColumns() {
    const totalW =
      CFG.NUM_COLS * CFG.POSTER_W + (CFG.NUM_COLS - 1) * CFG.COL_GAP;
    const startX = -totalW / 2 + CFG.POSTER_W / 2;
    const colH = CFG.POSTERS_PER_COL * (CFG.POSTER_H + CFG.GAP);

    for (let c = 0; c < CFG.NUM_COLS; c++) {
      const group = new THREE.Group();
      const xPos = startX + c * (CFG.POSTER_W + CFG.COL_GAP);
      group.position.x = xPos;

      const dir = c % 2 === 0 ? 1 : -1; // alternating directions
      const speed =
        CFG.BASE_SPEED + (Math.random() - 0.5) * 2 * CFG.SPEED_VARIANCE;

      const posters = [];

      for (let r = 0; r < CFG.POSTERS_PER_COL; r++) {
        const texIdx = (c * CFG.POSTERS_PER_COL + r) % posterTextures.length;
        const mat = new THREE.MeshBasicMaterial({
          map: posterTextures[texIdx],
          transparent: true,
          opacity: 1,
        });
        const geo = new THREE.PlaneGeometry(CFG.POSTER_W, CFG.POSTER_H);
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.y =
          r * (CFG.POSTER_H + CFG.GAP) - colH / 2 + CFG.POSTER_H / 2;
        mesh.position.z = -0.5 + Math.random() * 0.3;

        // Round corners via vertex displacement (subtle)
        mesh.userData = {
          baseY: mesh.position.y,
          texIdx,
          velocity: new THREE.Vector3(),
        };

        group.add(mesh);
        posters.push(mesh);
      }

      scene.add(group);
      columns.push({ group, speed: Math.abs(speed), dir, posters, colH });
    }
  }

  /* ================================================================
     ANIMATION LOOP
     ================================================================ */
  function animate() {
    requestAnimationFrame(animate);
    const dt = clock.getDelta();
    phaseTime += dt;

    switch (phase) {
      case "scrolling":
        updateScrolling(dt, 1.0);
        if (phaseTime >= CFG.SCROLL_DURATION) {
          phase = "accelerating";
          phaseTime = 0;
        }
        break;

      case "accelerating":
        // Exponential speed ramp
        const accelT = phaseTime / CFG.ACCEL_DURATION;
        const multiplier = 1 + accelT * accelT * 12;
        updateScrolling(dt, multiplier);

        // Shake camera slightly
        camera.position.x = (Math.random() - 0.5) * accelT * 0.15;
        camera.position.y = (Math.random() - 0.5) * accelT * 0.15;

        // Blur/opacity effect — posters fade a bit at max speed
        if (accelT > 0.7) {
          const fade = 1 - (accelT - 0.7) / 0.3;
          columns.forEach((col) =>
            col.posters.forEach((p) => {
              p.material.opacity = Math.max(fade, 0);
            })
          );
        }

        if (phaseTime >= CFG.ACCEL_DURATION) {
          triggerExplosion();
          phase = "exploding";
          phaseTime = 0;
        }
        break;

      case "exploding":
        updateExplosion(dt);
        if (phaseTime >= 3.0) {
          phase = "done";
          showUI();
        }
        break;

      case "done":
        // Gentle particle drift
        if (particles) updateDriftParticles(dt);
        break;
    }

    renderer.render(scene, camera);
  }

  /* ================================================================
     SCROLLING
     ================================================================ */
  function updateScrolling(dt, multiplier) {
    columns.forEach((col) => {
      const dy = col.speed * col.dir * multiplier * dt;
      col.group.position.y += dy;

      // Wrap: seamless looping — reset when entire column has scrolled
      // one full column-height so tiles loop perfectly.
      if (Math.abs(col.group.position.y) >= col.colH) {
        col.group.position.y %= col.colH;
      }
    });
  }

  /* ================================================================
     EXPLOSION
     ================================================================ */
  function triggerExplosion() {
    // Remove poster columns
    columns.forEach((col) => scene.remove(col.group));

    // Camera reset
    camera.position.x = 0;
    camera.position.y = 0;

    // Flash — brief white screen via fog
    scene.background = new THREE.Color(0xffffff);
    setTimeout(() => {
      scene.background = new THREE.Color(0x050507);
    }, 120);

    // Create explosion particles
    createExplosionParticles();

    // Create shockwave ring
    createShockwave();
  }

  function createExplosionParticles() {
    const count = CFG.NUM_PARTICLES;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const sizes = new Float32Array(count);

    particleData = [];

    const palette = [
      new THREE.Color(0x8b5cf6), // purple
      new THREE.Color(0x06b6d4), // cyan
      new THREE.Color(0xf59e0b), // amber
      new THREE.Color(0xef4444), // red
      new THREE.Color(0xffffff), // white
    ];

    for (let i = 0; i < count; i++) {
      // Start from center with scatter
      positions[i * 3] = (Math.random() - 0.5) * 0.5;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 0.5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 0.5;

      // Color
      const col = palette[Math.floor(Math.random() * palette.length)];
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;

      // Size
      sizes[i] = 0.04 + Math.random() * 0.12;

      // Velocity — radial outward
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const speed = 2 + Math.random() * 8;
      particleData.push({
        vx: Math.sin(phi) * Math.cos(theta) * speed,
        vy: Math.sin(phi) * Math.sin(theta) * speed,
        vz: Math.cos(phi) * speed * 0.5,
        decay: 0.93 + Math.random() * 0.05,
        life: 1.0,
      });
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geo.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

    // Custom shader for soft round particles
    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
      },
      vertexShader: `
        attribute float size;
        attribute vec3 color;
        varying vec3 vColor;
        varying float vAlpha;
        void main() {
          vColor = color;
          vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = size * (300.0 / -mvPos.z);
          gl_Position = projectionMatrix * mvPos;
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        void main() {
          float d = length(gl_PointCoord - vec2(0.5));
          if (d > 0.5) discard;
          float alpha = smoothstep(0.5, 0.1, d);
          gl_FragColor = vec4(vColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    particles = new THREE.Points(geo, mat);
    scene.add(particles);
  }

  function createShockwave() {
    const geo = new THREE.RingGeometry(0.1, 0.3, 64);
    const mat = new THREE.MeshBasicMaterial({
      color: 0x8b5cf6,
      transparent: true,
      opacity: 0.8,
      side: THREE.DoubleSide,
    });
    shockwaveRing = new THREE.Mesh(geo, mat);
    shockwaveRing.position.z = 0.1;
    scene.add(shockwaveRing);
  }

  function updateExplosion(dt) {
    // Update particles
    if (particles) {
      const positions = particles.geometry.attributes.position.array;
      const colors = particles.geometry.attributes.color.array;

      for (let i = 0; i < particleData.length; i++) {
        const pd = particleData[i];
        positions[i * 3] += pd.vx * dt;
        positions[i * 3 + 1] += pd.vy * dt;
        positions[i * 3 + 2] += pd.vz * dt;

        // Decay velocity
        pd.vx *= pd.decay;
        pd.vy *= pd.decay;
        pd.vz *= pd.decay;

        // Gravity pull
        pd.vy -= 0.5 * dt;

        // Fade life
        pd.life -= dt * 0.3;

        // Fade colors toward dark
        const fade = Math.max(pd.life, 0);
        colors[i * 3] *= 0.995;
        colors[i * 3 + 1] *= 0.995;
        colors[i * 3 + 2] *= 0.995;
      }

      particles.geometry.attributes.position.needsUpdate = true;
      particles.geometry.attributes.color.needsUpdate = true;
    }

    // Expand shockwave ring
    if (shockwaveRing) {
      const scale = 1 + phaseTime * CFG.SHOCKWAVE_SPEED;
      shockwaveRing.scale.set(scale, scale, 1);
      shockwaveRing.material.opacity = Math.max(0, 0.8 - phaseTime * 0.35);

      if (shockwaveRing.material.opacity <= 0) {
        scene.remove(shockwaveRing);
        shockwaveRing = null;
      }
    }
  }

  function updateDriftParticles(dt) {
    if (!particles) return;
    const positions = particles.geometry.attributes.position.array;
    for (let i = 0; i < particleData.length; i++) {
      const pd = particleData[i];
      // Gentle drift
      positions[i * 3] += pd.vx * dt * 0.02;
      positions[i * 3 + 1] += pd.vy * dt * 0.01 + dt * 0.02;
      positions[i * 3 + 2] += pd.vz * dt * 0.01;
    }
    particles.geometry.attributes.position.needsUpdate = true;
  }

  /* ================================================================
     UI REVEAL
     ================================================================ */
  function showUI() {
    // Populate hero card
    if (heroMedia) {
      document.getElementById("hero-poster").src = heroMedia.image_url;
      document.getElementById("hero-poster").alt = heroMedia.title;
      document.getElementById("hero-title").textContent = heroMedia.title;
      document.getElementById("hero-year").textContent = heroMedia.year || "";
      document.getElementById("hero-rating").textContent =
        heroMedia.rating ? heroMedia.rating.toFixed(1) : "";
    }

    // Staggered reveal
    setTimeout(() => {
      document.getElementById("hero-card").classList.add("visible");
    }, 200);

    setTimeout(() => {
      document.getElementById("landing-nav").classList.add("visible");
    }, 600);

    setTimeout(() => {
      document.getElementById("landing-brand").classList.add("visible");
    }, 800);

    // Add to watchlist button handler
    const btn = document.getElementById("btn-add-watchlist");
    btn.addEventListener("click", async () => {
      if (!heroMedia) return;

      try {
        const res = await fetch("/api/v1/watchlist", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            media_id: heroMedia.id,
            status: "planned",
          }),
        });

        const data = await res.json();

        if (res.status === 401) {
          // Not logged in — redirect to login
          window.location.href = "/login";
          return;
        }

        if (data.success) {
          btn.textContent = "✓ Added!";
          btn.style.background = "linear-gradient(135deg, #10b981, #059669)";
          btn.disabled = true;
        } else {
          btn.textContent = data.message || "Already in list";
          btn.style.background = "linear-gradient(135deg, #6b7280, #4b5563)";
        }
      } catch {
        btn.textContent = "Error — try again";
      }
    });
  }

  /* ================================================================
     RESIZE
     ================================================================ */
  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  /* ================================================================
     BOOT
     ================================================================ */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
