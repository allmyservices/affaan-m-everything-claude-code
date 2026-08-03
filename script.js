(() => {
  "use strict";

  const canvas = document.getElementById("matrix");
  const ctx = canvas.getContext("2d");

  const CHARSETS = {
    katakana:
      "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789",
    binary: "01",
    latin: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    hex: "0123456789ABCDEF",
  };

  const THEMES = {
    green: { fg: "#00ff66", head: "#c8ffdc" },
    amber: { fg: "#ffb000", head: "#fff2cc" },
    cyan: { fg: "#00e5ff", head: "#d6faff" },
    red: { fg: "#ff2b2b", head: "#ffd6d6" },
    white: { fg: "#dfe7e7", head: "#ffffff" },
    rainbow: { fg: null, head: "#ffffff" },
  };

  const state = {
    charset: "katakana",
    customChars: "",
    theme: "green",
    speed: 1,
    density: 1,
    fontSize: 16,
    trail: 0.05,
    glow: true,
    glitch: false,
    mouseReact: true,
    paused: false,
  };

  let drops = [];
  let columns = 0;
  let width = 0;
  let height = 0;
  let mouseX = -9999;
  let mouseY = -9999;
  let lastFrame = performance.now();
  let frameAccum = 0;
  let frameCount = 0;

  function currentCharset() {
    if (state.charset === "custom") {
      return state.customChars.trim() || CHARSETS.katakana;
    }
    return CHARSETS[state.charset] || CHARSETS.katakana;
  }

  function randChar() {
    const set = currentCharset();
    return set[(Math.random() * set.length) | 0];
  }

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    initDrops();
  }

  function initDrops() {
    columns = Math.max(1, Math.floor((width / state.fontSize) * state.density));
    drops = new Array(columns).fill(0).map(() => ({
      y: Math.random() * -100,
      speed: 0.5 + Math.random() * 0.5,
      hue: Math.random() * 360,
    }));
  }

  function themeColor(drop, isHead) {
    const theme = THEMES[state.theme];
    if (state.theme === "rainbow") {
      return isHead
        ? "#ffffff"
        : `hsl(${drop.hue}, 100%, ${isHead ? 80 : 50}%)`;
    }
    return isHead ? theme.head : theme.fg;
  }

  function draw() {
    ctx.fillStyle = `rgba(0, 0, 0, ${state.trail})`;
    ctx.fillRect(0, 0, width, height);

    const colWidth = width / columns;
    ctx.font = `${state.fontSize}px monospace`;
    ctx.textBaseline = "top";

    for (let i = 0; i < columns; i++) {
      const drop = drops[i];
      const x = i * colWidth;
      const y = drop.y * state.fontSize;

      let speedMul = 1;
      if (state.mouseReact) {
        const dx = x - mouseX;
        const dy = y - mouseY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 150) speedMul = 2.5;
      }

      const glitchSkip = state.glitch && Math.random() < 0.02;

      if (!glitchSkip) {
        ctx.fillStyle = themeColor(drop, true);
        if (state.glow) {
          ctx.shadowBlur = 8;
          ctx.shadowColor = ctx.fillStyle;
        } else {
          ctx.shadowBlur = 0;
        }
        ctx.fillText(randChar(), x, y);

        ctx.shadowBlur = 0;
        ctx.fillStyle = themeColor(drop, false);
        ctx.globalAlpha = 0.85;
        ctx.fillText(randChar(), x, y - state.fontSize);
        ctx.globalAlpha = 1;
      }

      if (y > height && Math.random() > 0.975) {
        drop.y = 0;
        drop.speed = 0.5 + Math.random() * 0.5;
        drop.hue = Math.random() * 360;
      }
      drop.y += drop.speed * state.speed * speedMul;
    }
  }

  function loop(now) {
    const dt = now - lastFrame;
    lastFrame = now;
    frameAccum += dt;
    frameCount++;
    if (frameAccum >= 500) {
      const fps = Math.round((frameCount * 1000) / frameAccum);
      document.getElementById("fps").textContent = `${fps} fps`;
      frameAccum = 0;
      frameCount = 0;
    }

    if (!state.paused) draw();
    requestAnimationFrame(loop);
  }

  window.addEventListener("resize", resize);
  window.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });
  window.addEventListener("mouseleave", () => {
    mouseX = -9999;
    mouseY = -9999;
  });

  // --- UI wiring ---
  const panel = document.getElementById("panel");
  const panelToggle = document.getElementById("panelToggle");

  function setPanelOpen(open) {
    panel.classList.toggle("open", open);
    panel.setAttribute("aria-hidden", String(!open));
    panelToggle.setAttribute("aria-expanded", String(open));
  }

  panelToggle.addEventListener("click", () =>
    setPanelOpen(!panel.classList.contains("open"))
  );

  const charsetEl = document.getElementById("charset");
  const customField = document.getElementById("customField");
  const customCharsEl = document.getElementById("customChars");
  charsetEl.addEventListener("change", () => {
    state.charset = charsetEl.value;
    customField.hidden = state.charset !== "custom";
  });
  customCharsEl.addEventListener("input", () => {
    state.customChars = customCharsEl.value;
  });

  document.getElementById("theme").addEventListener("change", (e) => {
    state.theme = e.target.value;
  });

  const speedEl = document.getElementById("speed");
  const speedOut = document.getElementById("speedOut");
  speedEl.addEventListener("input", () => {
    state.speed = parseFloat(speedEl.value);
    speedOut.textContent = `${state.speed.toFixed(1)}×`;
  });

  const densityEl = document.getElementById("density");
  const densityOut = document.getElementById("densityOut");
  densityEl.addEventListener("input", () => {
    state.density = parseFloat(densityEl.value);
    densityOut.textContent = `${state.density.toFixed(1)}×`;
    initDrops();
  });

  const fontSizeEl = document.getElementById("fontSize");
  const fontSizeOut = document.getElementById("fontSizeOut");
  fontSizeEl.addEventListener("input", () => {
    state.fontSize = parseInt(fontSizeEl.value, 10);
    fontSizeOut.textContent = `${state.fontSize}px`;
    initDrops();
  });

  const trailEl = document.getElementById("trail");
  const trailOut = document.getElementById("trailOut");
  trailEl.addEventListener("input", () => {
    state.trail = parseFloat(trailEl.value);
    trailOut.textContent = state.trail.toFixed(2);
  });

  document.getElementById("glow").addEventListener("change", (e) => {
    state.glow = e.target.checked;
  });
  document.getElementById("glitch").addEventListener("change", (e) => {
    state.glitch = e.target.checked;
  });
  document.getElementById("mouse").addEventListener("change", (e) => {
    state.mouseReact = e.target.checked;
  });

  const pauseBtn = document.getElementById("pauseBtn");
  pauseBtn.addEventListener("click", () => {
    state.paused = !state.paused;
    pauseBtn.textContent = state.paused ? "Resume" : "Pause";
  });

  document.getElementById("resetBtn").addEventListener("click", () => {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, width, height);
    initDrops();
  });

  window.addEventListener("keydown", (e) => {
    if (e.code === "Space") {
      e.preventDefault();
      pauseBtn.click();
    } else if (e.key.toLowerCase() === "h") {
      setPanelOpen(!panel.classList.contains("open"));
    }
  });

  resize();
  requestAnimationFrame(loop);
})();
