/**
 * WatchList Hub — Three.js Cinematic Landing Page
 *
 * Phases:
 *   1. LOADING   — fetch posters, show progress bar
 *   2. SCROLLING  — 5 columns scroll up/down at varied speeds
 *   3. ACCEL      — columns accelerate, motion-blur intensifies
 *   4. SHATTER    — posters shatter into hundreds of fragments flying outward
 *   5. REVERSE    — fragments fly back to center, reassembling into hero card
 *   6. DONE       — hero card + UI visible, ambient particle drift
 */

(function () {
  "use strict";

  /* ================================================================
     CONFIG
     ================================================================ */
  const CFG = {
    // NUM_COLS is computed dynamically in calcNumCols()
    POSTERS_PER_COL: 8,
    POSTER_W: 2.0,
    POSTER_H: 3.0,
    GAP: 0.4,
    COL_GAP: 0.35,

    BASE_SPEED: 0.5,
    SPEED_VARIANCE: 0.5,

    // Timing (seconds)
    SCROLL_DURATION: 2.0,
    ACCEL_DURATION: 2.0,
    SHATTER_DURATION: 0.7,
    REVERSE_DURATION: 1.4,

    // Fragments per poster mesh during shatter
    FRAG_COLS: 4,
    FRAG_ROWS: 6,

    // Particles
    NUM_SPARKLES: 400,

    CAM_Z: 7,
  };

  /* ================================================================
     GLOBALS
     ================================================================ */
  let scene, camera, renderer, clock;
  let columns = [];
  let phase = "loading";
  let phaseTime = 0;
  let heroMedia = null;
  let posterTextures = [];
  let mediaList = [];

  // Shatter / Reverse
  let fragments = [];
  let sparkles = null;
  let sparkleData = [];

  // Fire effect
  let firePoints = null;
  let fireData = [];
  const FIRE_COUNT = 600;

  // Motion blur
  let blurPlane = null;

  /* ================================================================
     INIT
     ================================================================ */
  async function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050507);
    scene.fog = new THREE.Fog(0x050507, 5, 20);

    camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = CFG.CAM_Z;

    const canvas = document.getElementById("landing-canvas");
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    clock = new THREE.Clock();

    scene.add(new THREE.AmbientLight(0xffffff, 0.65));
    const dLight = new THREE.DirectionalLight(0xffffff, 0.45);
    dLight.position.set(2, 4, 5);
    scene.add(dLight);

    // Neon point lights for glow
    const neonPurple = new THREE.PointLight(0x8b5cf6, 0, 15);
    neonPurple.position.set(0, 0, 3);
    scene.add(neonPurple);
    neonPurple.userData.ref = neonPurple; // keep ref for intensity changes

    const neonCyan = new THREE.PointLight(0x06b6d4, 0, 15);
    neonCyan.position.set(0, 0, 3);
    scene.add(neonCyan);

    window.addEventListener("resize", onResize);

    // Fetch posters
    try {
      const res = await fetch("/api/v1/landing/posters");
      mediaList = await res.json();
    } catch (e) {
      console.warn("Failed to fetch posters", e);
      mediaList = [];
    }
    if (mediaList.length === 0) {
      dismissLoadingScreen();
      showUI();
      return;
    }

    heroMedia = mediaList[Math.floor(Math.random() * mediaList.length)];

    await loadTextures();
    dismissLoadingScreen();

    // Create motion blur overlay
    createBlurOverlay();

    buildColumns();

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
          (tex) => { tex.minFilter = THREE.LinearFilter; tex.magFilter = THREE.LinearFilter; posterTextures[i] = tex; onProgress(); },
          undefined,
          () => { posterTextures[i] = createPlaceholderTex(); onProgress(); }
        );
      });
      setTimeout(resolve, 12000);
    });
  }

  function createPlaceholderTex() {
    const c = document.createElement("canvas"); c.width = 128; c.height = 192;
    const ctx = c.getContext("2d");
    ctx.fillStyle = `hsl(${Math.random()*360},40%,18%)`;
    ctx.fillRect(0, 0, 128, 192);
    return new THREE.CanvasTexture(c);
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
    updateLoadingProgress(1, 1);
    setTimeout(() => {
      screen.classList.add("fade-out");
      setTimeout(() => screen.remove(), 700);
    }, 300);
  }

  /* ================================================================
     MOTION BLUR OVERLAY
     ================================================================ */
  function createBlurOverlay() {
    const geo = new THREE.PlaneGeometry(30, 30);
    const mat = new THREE.MeshBasicMaterial({
      color: 0x050507,
      transparent: true,
      opacity: 0,
      depthTest: false,
    });
    blurPlane = new THREE.Mesh(geo, mat);
    blurPlane.position.z = CFG.CAM_Z - 0.5;
    blurPlane.renderOrder = 999;
    scene.add(blurPlane);
  }

  /* ================================================================
     RESPONSIVE COLUMN COUNT
     ================================================================ */
  function calcNumCols() {
    // Compute visible width of the frustum at z=0 (where posters sit)
    const vFov = THREE.MathUtils.degToRad(camera.fov);
    const visibleH = 2 * CFG.CAM_Z * Math.tan(vFov / 2);
    const visibleW = visibleH * (window.innerWidth / window.innerHeight);
    const colWidth = CFG.POSTER_W + CFG.COL_GAP;
    // +2 extra columns so edges are always covered
    return Math.ceil(visibleW / colWidth) + 2;
  }

  /* ================================================================
     BUILD COLUMNS
     ================================================================ */
  function buildColumns() {
    const numCols = calcNumCols();
    const totalW = numCols * CFG.POSTER_W + (numCols - 1) * CFG.COL_GAP;
    const startX = -totalW / 2 + CFG.POSTER_W / 2;
    const colH = CFG.POSTERS_PER_COL * (CFG.POSTER_H + CFG.GAP);

    for (let c = 0; c < numCols; c++) {
      const group = new THREE.Group();
      group.position.x = startX + c * (CFG.POSTER_W + CFG.COL_GAP);

      const dir = c % 2 === 0 ? 1 : -1;
      const speed = CFG.BASE_SPEED + (Math.random() - 0.5) * 2 * CFG.SPEED_VARIANCE;
      const posters = [];

      for (let r = 0; r < CFG.POSTERS_PER_COL; r++) {
        const texIdx = (c * CFG.POSTERS_PER_COL + r) % posterTextures.length;
        const mat = new THREE.MeshBasicMaterial({ map: posterTextures[texIdx], transparent: true, opacity: 1 });
        const geo = new THREE.PlaneGeometry(CFG.POSTER_W, CFG.POSTER_H);
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.y = r * (CFG.POSTER_H + CFG.GAP) - colH / 2 + CFG.POSTER_H / 2;
        mesh.position.z = -0.3 + Math.random() * 0.2;
        mesh.userData = { baseY: mesh.position.y, texIdx };
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
    const dt = Math.min(clock.getDelta(), 0.05); // cap to prevent huge jumps
    phaseTime += dt;

    switch (phase) {
      case "scrolling":
        updateScrolling(dt, 1.0);
        if (phaseTime >= CFG.SCROLL_DURATION) { phase = "accel"; phaseTime = 0; }
        break;

      case "accel":
        handleAccelPhase(dt);
        break;

      case "shatter":
        handleShatterPhase(dt);
        break;

      case "reverse":
        handleReversePhase(dt);
        break;

      case "done":
        if (sparkles) updateSparklesDrift(dt);
        if (firePoints) updateFire(dt);
        break;
    }

    renderer.render(scene, camera);
  }

  /* ================================================================
     SCROLLING
     ================================================================ */
  function updateScrolling(dt, multiplier) {
    columns.forEach((col) => {
      col.group.position.y += col.speed * col.dir * multiplier * dt;
      if (Math.abs(col.group.position.y) >= col.colH) {
        col.group.position.y %= col.colH;
      }
    });
  }

  /* ================================================================
     PHASE: ACCELERATE
     ================================================================ */
  function handleAccelPhase(dt) {
    const t = phaseTime / CFG.ACCEL_DURATION; // 0→1
    const multiplier = 1 + t * t * 18; // exponential ramp
    updateScrolling(dt, multiplier);

    // Camera shake
    camera.position.x = (Math.random() - 0.5) * t * 0.2;
    camera.position.y = (Math.random() - 0.5) * t * 0.2;

    // Simulated motion blur: fade overlay in
    if (blurPlane) {
      blurPlane.material.opacity = t * 0.45;
    }

    // Fade posters at end
    if (t > 0.75) {
      const fade = 1 - (t - 0.75) / 0.25;
      columns.forEach(col => col.posters.forEach(p => { p.material.opacity = Math.max(fade, 0); }));
    }

    if (phaseTime >= CFG.ACCEL_DURATION) {
      triggerShatter();
      phase = "shatter";
      phaseTime = 0;
    }
  }

  /* ================================================================
     PHASE: SHATTER — posters break into fragments
     ================================================================ */
  function triggerShatter() {
    // Reset camera
    camera.position.set(0, 0, CFG.CAM_Z);

    // Hide blur overlay
    if (blurPlane) { blurPlane.material.opacity = 0; blurPlane.visible = false; }

    // Flash
    scene.background = new THREE.Color(0xffffff);
    setTimeout(() => { scene.background = new THREE.Color(0x050507); }, 100);

    // Turn on neon lights
    scene.children.forEach(c => {
      if (c.isPointLight) c.intensity = 3;
    });

    // Collect all visible poster meshes' world positions + textures
    const allPosters = [];
    columns.forEach(col => {
      col.posters.forEach(p => {
        const worldPos = new THREE.Vector3();
        p.getWorldPosition(worldPos);
        allPosters.push({ worldPos, texIdx: p.userData.texIdx });
      });
    });

    // Remove column groups
    columns.forEach(col => scene.remove(col.group));

    // Create fragments from each poster
    fragments = [];
    const fragW = CFG.POSTER_W / CFG.FRAG_COLS;
    const fragH = CFG.POSTER_H / CFG.FRAG_ROWS;

    allPosters.forEach(({ worldPos, texIdx }) => {
      const tex = posterTextures[texIdx];

      for (let fy = 0; fy < CFG.FRAG_ROWS; fy++) {
        for (let fx = 0; fx < CFG.FRAG_COLS; fx++) {
          // UV offset for this fragment
          const uOff = fx / CFG.FRAG_COLS;
          const vOff = fy / CFG.FRAG_ROWS;
          const uSize = 1 / CFG.FRAG_COLS;
          const vSize = 1 / CFG.FRAG_ROWS;

          const geo = new THREE.PlaneGeometry(fragW, fragH);
          // Map UVs to the sub-region of the original texture
          const uvAttr = geo.attributes.uv;
          for (let i = 0; i < uvAttr.count; i++) {
            const u = uvAttr.getX(i);
            const v = uvAttr.getY(i);
            uvAttr.setXY(i, uOff + u * uSize, vOff + v * vSize);
          }
          uvAttr.needsUpdate = true;

          const mat = new THREE.MeshBasicMaterial({
            map: tex,
            transparent: true,
            opacity: 1,
            side: THREE.DoubleSide,
          });

          const mesh = new THREE.Mesh(geo, mat);

          // Position: within the poster grid
          const localX = (fx - CFG.FRAG_COLS / 2 + 0.5) * fragW;
          const localY = (fy - CFG.FRAG_ROWS / 2 + 0.5) * fragH;
          mesh.position.set(
            worldPos.x + localX,
            worldPos.y + localY,
            worldPos.z
          );

          // Store start position
          const startPos = mesh.position.clone();
          const startRot = new THREE.Euler(0, 0, 0);

          // Explosion velocity — radial outward from center + random
          const dirX = mesh.position.x + (Math.random() - 0.5) * 2;
          const dirY = mesh.position.y + (Math.random() - 0.5) * 2;
          const dirZ = 2 + Math.random() * 6;
          const velocity = new THREE.Vector3(dirX * 1.5, dirY * 1.5, dirZ);

          // Random rotation rate
          const rotRate = new THREE.Vector3(
            (Math.random() - 0.5) * 8,
            (Math.random() - 0.5) * 8,
            (Math.random() - 0.5) * 6
          );

          scene.add(mesh);
          fragments.push({
            mesh,
            startPos,
            startRot,
            velocity,
            rotRate,
            // Target will be set in reverse phase
            targetPos: new THREE.Vector3(0, 0, 0),
            targetRot: new THREE.Euler(0, 0, 0),
            // Snapshot of max-exploded position (set at end of shatter)
            explodedPos: null,
            explodedRot: null,
          });
        }
      }
    });

    // Create sparkles / light streaks
    createSparkles();
  }

  function handleShatterPhase(dt) {
    const t = phaseTime / CFG.SHATTER_DURATION;

    // Update fragment positions — fly outward
    fragments.forEach(frag => {
      frag.mesh.position.x += frag.velocity.x * dt;
      frag.mesh.position.y += frag.velocity.y * dt;
      frag.mesh.position.z += frag.velocity.z * dt;

      frag.mesh.rotation.x += frag.rotRate.x * dt;
      frag.mesh.rotation.y += frag.rotRate.y * dt;
      frag.mesh.rotation.z += frag.rotRate.z * dt;

      // Gravity
      frag.velocity.y -= 2 * dt;
    });

    // Update sparkles
    updateSparklesExplode(dt);

    // Neon glow pulse
    scene.children.forEach(c => {
      if (c.isPointLight) c.intensity = 3 + Math.sin(phaseTime * 20) * 1.5;
    });

    if (phaseTime >= CFG.SHATTER_DURATION) {
      // Snapshot exploded positions for reverse lerp
      fragments.forEach(frag => {
        frag.explodedPos = frag.mesh.position.clone();
        frag.explodedRot = frag.mesh.rotation.clone();
      });

      // Set target: all fragments converge to center to form hero card
      assignReverseTargets();

      phase = "reverse";
      phaseTime = 0;
    }
  }

  /* ================================================================
     PHASE: REVERSE — fragments fly back & reassemble
     ================================================================ */
  function assignReverseTargets() {
    const cardW = CFG.POSTER_W;
    const cardH = CFG.POSTER_H;
    const fragW = cardW / CFG.FRAG_COLS;
    const fragH = cardH / CFG.FRAG_ROWS;
    const totalCells = CFG.FRAG_COLS * CFG.FRAG_ROWS;

    const heroTex = posterTextures[mediaList.indexOf(heroMedia)] || posterTextures[0];

    // ALL fragments converge to the hero card.
    // Each fragment is assigned a random cell in the 4×6 grid.
    fragments.forEach((frag) => {
      const cellIdx = Math.floor(Math.random() * totalCells);
      const fx = cellIdx % CFG.FRAG_COLS;
      const fy = Math.floor(cellIdx / CFG.FRAG_COLS);

      frag.targetPos.set(
        (fx - CFG.FRAG_COLS / 2 + 0.5) * fragW,
        (fy - CFG.FRAG_ROWS / 2 + 0.5) * fragH,
        0
      );
      frag.targetRot = new THREE.Euler(0, 0, 0);

      // Re-map UVs to the hero texture sub-region for this cell
      const uvAttr = frag.mesh.geometry.attributes.uv;
      const uOff = fx / CFG.FRAG_COLS;
      const vOff = fy / CFG.FRAG_ROWS;
      const uSize = 1 / CFG.FRAG_COLS;
      const vSize = 1 / CFG.FRAG_ROWS;
      uvAttr.setXY(0, uOff, vOff);
      uvAttr.setXY(1, uOff + uSize, vOff);
      uvAttr.setXY(2, uOff, vOff + vSize);
      uvAttr.setXY(3, uOff + uSize, vOff + vSize);
      uvAttr.needsUpdate = true;

      frag.mesh.material.map = heroTex;
      frag.mesh.material.needsUpdate = true;
    });
  }

  function handleReversePhase(dt) {
    const rawT = Math.min(phaseTime / CFG.REVERSE_DURATION, 1);
    const t = easeInOutCubic(rawT);

    fragments.forEach(frag => {
      // ALL fragments lerp from exploded position → hero card target
      frag.mesh.position.lerpVectors(frag.explodedPos, frag.targetPos, t);
      frag.mesh.rotation.x = THREE.MathUtils.lerp(frag.explodedRot.x, frag.targetRot.x, t);
      frag.mesh.rotation.y = THREE.MathUtils.lerp(frag.explodedRot.y, frag.targetRot.y, t);
      frag.mesh.rotation.z = THREE.MathUtils.lerp(frag.explodedRot.z, frag.targetRot.z, t);
      frag.mesh.material.opacity = 1;
    });

    // Fade neon lights down
    scene.children.forEach(c => {
      if (c.isPointLight) c.intensity = 3 * (1 - t) + 0.3;
    });

    // Sparkles converge toward center
    updateSparklesReverse(dt, t);

    if (rawT >= 1) {
      finalizeHeroCard();
      phase = "done";
      phaseTime = 0;
      showUI();
    }
  }

  /* ================================================================
     HERO CARD FINALIZATION
     ================================================================ */
  function finalizeHeroCard() {
    // Remove ALL fragment meshes — replace with a single clean rounded poster
    fragments.forEach(frag => scene.remove(frag.mesh));
    fragments = [];

    // ── 1. Rounded-corner hero poster ──
    const heroTex = posterTextures[mediaList.indexOf(heroMedia)] || posterTextures[0];
    const heroMesh = createRoundedPoster(heroTex, CFG.POSTER_W, CFG.POSTER_H, 0.15);
    heroMesh.position.set(0, 0.5, 0);
    scene.add(heroMesh);

    // ── 2. Fire particle system around the card ──
    createFireSystem(0, 0.5, CFG.POSTER_W, CFG.POSTER_H);

    // ── 3. Scatter sparkles fullscreen ──
    scatterSparklesFullscreen();

    // Dim neon lights
    scene.children.forEach(c => {
      if (c.isPointLight) c.intensity = 0.6;
    });
  }

  /**
   * Create a poster mesh with rounded corners using a canvas alpha mask.
   */
  function createRoundedPoster(texture, w, h, radius) {
    // Create alpha mask via canvas
    const maskSize = 512;
    const maskCanvas = document.createElement("canvas");
    maskCanvas.width = maskSize;
    maskCanvas.height = Math.round(maskSize * (h / w));
    const mH = maskCanvas.height;
    const ctx = maskCanvas.getContext("2d");

    // Draw rounded rectangle
    const r = radius * maskSize / w; // scale radius to canvas pixels
    ctx.beginPath();
    ctx.moveTo(r, 0);
    ctx.lineTo(maskSize - r, 0);
    ctx.quadraticCurveTo(maskSize, 0, maskSize, r);
    ctx.lineTo(maskSize, mH - r);
    ctx.quadraticCurveTo(maskSize, mH, maskSize - r, mH);
    ctx.lineTo(r, mH);
    ctx.quadraticCurveTo(0, mH, 0, mH - r);
    ctx.lineTo(0, r);
    ctx.quadraticCurveTo(0, 0, r, 0);
    ctx.closePath();
    ctx.fillStyle = "#fff";
    ctx.fill();

    const alphaTex = new THREE.CanvasTexture(maskCanvas);

    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uMap: { value: texture },
        uAlpha: { value: alphaTex },
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D uMap;
        uniform sampler2D uAlpha;
        varying vec2 vUv;
        void main() {
          vec4 color = texture2D(uMap, vUv);
          float a = texture2D(uAlpha, vUv).r;
          gl_FragColor = vec4(color.rgb, a);
        }
      `,
      transparent: true,
      side: THREE.DoubleSide,
    });

    const geo = new THREE.PlaneGeometry(w, h);
    return new THREE.Mesh(geo, mat);
  }

  /**
   * Scatter existing sparkles across the full viewport as ambient background.
   */
  function scatterSparklesFullscreen() {
    if (!sparkles) return;
    const pos = sparkles.geometry.attributes.position.array;
    const vFov = THREE.MathUtils.degToRad(camera.fov);
    const visH = 2 * CFG.CAM_Z * Math.tan(vFov / 2);
    const visW = visH * (window.innerWidth / window.innerHeight);

    for (let i = 0; i < sparkleData.length; i++) {
      // Spread across full visible area
      pos[i * 3] = (Math.random() - 0.5) * visW * 1.2;
      pos[i * 3 + 1] = (Math.random() - 0.5) * visH * 1.2;
      pos[i * 3 + 2] = -2 + Math.random() * -3; // behind the poster

      // Reset velocities for gentle drift
      sparkleData[i].vx = (Math.random() - 0.5) * 0.3;
      sparkleData[i].vy = 0.05 + Math.random() * 0.15;
      sparkleData[i].vz = 0;
    }
    sparkles.geometry.attributes.position.needsUpdate = true;
    // Make visible again (reverse phase may have faded them)
    sparkles.material.opacity = 1;
  }

  /* ================================================================
     FIRE PARTICLE SYSTEM
     ================================================================ */
  function createFireSystem(cx, cy, cardW, cardH) {
    const count = FIRE_COUNT;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    fireData = [];

    const halfW = cardW / 2;
    const halfH = cardH / 2;

    for (let i = 0; i < count; i++) {
      // Spawn on a random edge of the card
      const fd = spawnFlameParticle(cx, cy, halfW, halfH);
      fireData.push(fd);

      positions[i * 3] = fd.x;
      positions[i * 3 + 1] = fd.y;
      positions[i * 3 + 2] = fd.z;

      colors[i * 3] = fd.r;
      colors[i * 3 + 1] = fd.g;
      colors[i * 3 + 2] = fd.b;

      sizes[i] = fd.size;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geo.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

    const mat = new THREE.ShaderMaterial({
      vertexShader: `
        attribute float size;
        attribute vec3 color;
        varying vec3 vColor;
        varying float vAlpha;
        void main() {
          vColor = color;
          vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = size * (350.0 / -mvPos.z);
          gl_Position = projectionMatrix * mvPos;
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        void main() {
          float d = length(gl_PointCoord - vec2(0.5));
          if (d > 0.5) discard;
          // Soft radial falloff for fire glow
          float alpha = smoothstep(0.5, 0.0, d);
          gl_FragColor = vec4(vColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    firePoints = new THREE.Points(geo, mat);
    scene.add(firePoints);
  }

  function spawnFlameParticle(cx, cy, halfW, halfH) {
    const edge = Math.random();
    let x, y;

    // All spawn positions are OUTSIDE the card edges
    const outward = 0.1 + Math.random() * 0.2; // 0.1–0.3 outside edge

    if (edge < 0.3) {
      // Bottom edge — spawn BELOW the card
      x = cx + (Math.random() - 0.5) * halfW * 2.4;
      y = cy - halfH - outward - Math.random() * 0.3; // 0.1–0.6 below
    } else if (edge < 0.55) {
      // Left edge — spawn LEFT of the card
      x = cx - halfW - outward;
      y = cy + (Math.random() - 0.5) * halfH * 2.2;
    } else if (edge < 0.8) {
      // Right edge — spawn RIGHT of the card
      x = cx + halfW + outward;
      y = cy + (Math.random() - 0.5) * halfH * 2.2;
    } else {
      // Top edge — spawn right at the card edge
      x = cx + (Math.random() - 0.5) * halfW * 2.4;
      y = cy + halfH + Math.random() * 0.05; // barely above
    }

    // Fire colors — more white-hot and intense
    const colorRoll = Math.random();
    let r, g, b;
    if (colorRoll < 0.25) {
      // White-hot core
      r = 1.0; g = 0.9 + Math.random() * 0.1; b = 0.6 + Math.random() * 0.4;
    } else if (colorRoll < 0.45) {
      // Bright orange
      r = 1.0; g = 0.5 + Math.random() * 0.2; b = 0.05;
    } else if (colorRoll < 0.65) {
      // Yellow
      r = 1.0; g = 0.85 + Math.random() * 0.15; b = 0.1 + Math.random() * 0.2;
    } else if (colorRoll < 0.8) {
      // Deep red
      r = 0.95 + Math.random() * 0.05; g = 0.1 + Math.random() * 0.2; b = 0.02;
    } else if (colorRoll < 0.92) {
      // Amber
      r = 1.0; g = 0.65 + Math.random() * 0.1; b = 0.0;
    } else {
      // Violet-pink anime ember
      r = 0.8 + Math.random() * 0.2; g = 0.1; b = 0.6 + Math.random() * 0.3;
    }

    return {
      x, y,
      z: -(0.05 + Math.random() * 0.15), // BEHIND the poster (z < 0)
      vx: (Math.random() - 0.5) * 0.8,
      vy: 1.0 + Math.random() * 3.0,
      life: 1.0,
      maxLife: 0.4 + Math.random() * 0.7,
      age: Math.random() * 0.3,
      size: 0.15 + Math.random() * 0.35,
      r, g, b,
      cx, cy, halfW, halfH,
    };
  }

  function updateFire(dt) {
    if (!firePoints) return;
    const pos = firePoints.geometry.attributes.position.array;
    const col = firePoints.geometry.attributes.color.array;
    const siz = firePoints.geometry.attributes.size.array;

    for (let i = 0; i < fireData.length; i++) {
      const f = fireData[i];
      f.age += dt;

      if (f.age >= f.maxLife) {
        // Respawn
        const nf = spawnFlameParticle(f.cx, f.cy, f.halfW, f.halfH);
        Object.assign(f, nf);
        f.age = 0;
      }

      const t = f.age / f.maxLife; // 0→1 lifecycle

      // Move: rise + intense turbulence
      const turbX = Math.sin(f.age * 12 + i * 0.5) * 0.6;
      const turbZ = Math.cos(f.age * 10 + i * 1.1) * 0.2;
      f.x += (f.vx + turbX) * dt;
      f.y += f.vy * dt;
      f.z += turbZ * dt;

      // Accelerate upward
      f.vy += 0.8 * dt;

      pos[i * 3] = f.x;
      pos[i * 3 + 1] = f.y;
      pos[i * 3 + 2] = f.z;

      // Fade color: bright → dim as particle ages
      const fade = 1.0 - t * t;
      col[i * 3] = f.r * fade;
      col[i * 3 + 1] = f.g * fade * 0.7; // green fades faster
      col[i * 3 + 2] = f.b * fade * 0.5;

      // Size: swell slightly then shrink
      const sizeCurve = t < 0.2 ? t / 0.2 : 1.0 - (t - 0.2) / 0.8;
      siz[i] = f.size * sizeCurve;
    }

    firePoints.geometry.attributes.position.needsUpdate = true;
    firePoints.geometry.attributes.color.needsUpdate = true;
    firePoints.geometry.attributes.size.needsUpdate = true;
  }

  /* ================================================================
     SPARKLES / PARTICLES
     ================================================================ */
  function createSparkles() {
    const count = CFG.NUM_SPARKLES;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    sparkleData = [];

    const palette = [
      new THREE.Color(0x8b5cf6),
      new THREE.Color(0xd946ef),
      new THREE.Color(0x06b6d4),
      new THREE.Color(0xf0abfc),
      new THREE.Color(0xffffff),
    ];

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 0.5;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 0.5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 0.5;

      const col = palette[Math.floor(Math.random() * palette.length)];
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;

      sizes[i] = 0.03 + Math.random() * 0.1;

      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const spd = 3 + Math.random() * 10;
      sparkleData.push({
        vx: Math.sin(phi) * Math.cos(theta) * spd,
        vy: Math.sin(phi) * Math.sin(theta) * spd,
        vz: Math.cos(phi) * spd * 0.6,
        life: 1,
      });
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geo.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

    const mat = new THREE.ShaderMaterial({
      vertexShader: `
        attribute float size;
        attribute vec3 color;
        varying vec3 vColor;
        void main() {
          vColor = color;
          vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = size * (280.0 / -mvPos.z);
          gl_Position = projectionMatrix * mvPos;
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        void main() {
          float d = length(gl_PointCoord - vec2(0.5));
          if (d > 0.5) discard;
          float alpha = smoothstep(0.5, 0.05, d);
          gl_FragColor = vec4(vColor, alpha * 0.9);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    sparkles = new THREE.Points(geo, mat);
    scene.add(sparkles);
  }

  function updateSparklesExplode(dt) {
    if (!sparkles) return;
    const pos = sparkles.geometry.attributes.position.array;
    for (let i = 0; i < sparkleData.length; i++) {
      const s = sparkleData[i];
      pos[i * 3] += s.vx * dt;
      pos[i * 3 + 1] += s.vy * dt;
      pos[i * 3 + 2] += s.vz * dt;
      s.vx *= 0.96;
      s.vy *= 0.96;
      s.vz *= 0.96;
      s.vy -= 1.5 * dt;
    }
    sparkles.geometry.attributes.position.needsUpdate = true;
  }

  function updateSparklesReverse(dt, t) {
    if (!sparkles) return;
    const pos = sparkles.geometry.attributes.position.array;
    for (let i = 0; i < sparkleData.length; i++) {
      // Pull toward center
      pos[i * 3] *= (1 - t * 0.03);
      pos[i * 3 + 1] *= (1 - t * 0.03);
      pos[i * 3 + 2] *= (1 - t * 0.02);
    }
    sparkles.geometry.attributes.position.needsUpdate = true;
    // Fade sparkles
    sparkles.material.opacity = 1 - t;
  }

  function updateSparklesDrift(dt) {
    if (!sparkles) return;
    const pos = sparkles.geometry.attributes.position.array;
    const vFov = THREE.MathUtils.degToRad(camera.fov);
    const visH = 2 * CFG.CAM_Z * Math.tan(vFov / 2);
    const visW = visH * (window.innerWidth / window.innerHeight);
    const halfW = visW * 0.7;
    const halfH = visH * 0.7;

    for (let i = 0; i < sparkleData.length; i++) {
      const s = sparkleData[i];
      // Gentle upward float + horizontal sway
      pos[i * 3] += s.vx * dt + Math.sin(phaseTime * 0.5 + i) * 0.002;
      pos[i * 3 + 1] += s.vy * dt;

      // Wrap particles that go off-screen
      if (pos[i * 3 + 1] > halfH) pos[i * 3 + 1] = -halfH;
      if (pos[i * 3] > halfW) pos[i * 3] = -halfW;
      if (pos[i * 3] < -halfW) pos[i * 3] = halfW;
    }
    sparkles.geometry.attributes.position.needsUpdate = true;
  }

  /* ================================================================
     EASING
     ================================================================ */
  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  /* ================================================================
     UI REVEAL
     ================================================================ */
  function showUI() {
    // Populate hero text (poster is the Three.js assembled card — no img needed)
    if (heroMedia) {
      document.getElementById("hero-title").textContent = heroMedia.title;
      document.getElementById("hero-year").textContent = heroMedia.year || "";
      document.getElementById("hero-rating").textContent =
        heroMedia.rating ? heroMedia.rating.toFixed(1) : "";
    }

    setTimeout(() => { document.getElementById("hero-card").classList.add("visible"); }, 200);
    setTimeout(() => { document.getElementById("landing-nav").classList.add("visible"); }, 600);
    setTimeout(() => { document.getElementById("landing-brand").classList.add("visible"); }, 800);

    const btn = document.getElementById("btn-add-watchlist");
    btn.addEventListener("click", async () => {
      if (!heroMedia) return;
      try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        const token = csrfToken ? csrfToken.getAttribute('content') : '';
        
        const res = await fetch("/api/v1/watchlist", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": token
          },
          body: JSON.stringify({ 
            mediaId: heroMedia.id, 
            mediaType: "movie",
            status: "planned" 
          }),
        });
        const data = await res.json();
        if (res.status === 401) { window.location.href = "/login"; return; }
        if (data.success) {
          btn.textContent = "✓ Added!";
          btn.style.background = "linear-gradient(135deg, #10b981, #059669)";
          btn.disabled = true;
        } else {
          btn.textContent = data.message || "Already in list";
          btn.style.background = "linear-gradient(135deg, #6b7280, #4b5563)";
        }
      } catch { btn.textContent = "Error — try again"; }
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
