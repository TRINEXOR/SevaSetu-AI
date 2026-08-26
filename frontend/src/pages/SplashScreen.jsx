/**
 * SevaSetu AI — Splash Screen
 * Author: Rahul Jha | Made in India 🇮🇳
 *
 * 3D animated intro:
 *  - Starfield particle background
 *  - India tricolor flag stripes
 *  - Ashoka Chakra spinning wheel
 *  - 3D logo entrance (CSS perspective transforms)
 *  - Staggered text reveals
 *  - "Made in India" finale with tricolor
 *  - Enter button → routes to Login
 */

import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./SplashScreen.module.css";

export default function SplashScreen({ onComplete }) {
  const navigate     = useNavigate();
  const canvasRef    = useRef(null);
  const [phase, setPhase] = useState(0);
  // phase 0 = mounting, 1 = logo in, 2 = taglines in, 3 = button visible, 4 = fade out

  // ── Particle canvas ───────────────────────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx    = canvas.getContext("2d");
    let animId;

    const resize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // Generate particles
    const PARTICLE_COUNT = 200;
    const particles = Array.from({ length: PARTICLE_COUNT }, () => ({
      x:    Math.random() * canvas.width,
      y:    Math.random() * canvas.height,
      r:    Math.random() * 1.8 + 0.3,
      vx:   (Math.random() - 0.5) * 0.3,
      vy:   (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.7 + 0.2,
      color: ["#FF6B00", "#FFD700", "#138808", "#4F8EF7", "#ffffff"][
        Math.floor(Math.random() * 5)
      ],
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0)             p.x = canvas.width;
        if (p.x > canvas.width)  p.x = 0;
        if (p.y < 0)             p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
      });
      ctx.globalAlpha = 1;
      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  // ── Phase sequencer ───────────────────────────────────────────────────────
  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 300),   // logo entrance
      setTimeout(() => setPhase(2), 1800),  // taglines
      setTimeout(() => setPhase(3), 2800),  // button
    ];
    return () => timers.forEach(clearTimeout);
  }, []);

  // ── Enter handler ─────────────────────────────────────────────────────────
  const handleEnter = () => {
    setPhase(4);
    setTimeout(() => {
      onComplete?.();
      navigate("/login");
    }, 800);
  };

  // ── Ashoka chakra spokes (24 spokes) ─────────────────────────────────────
  const spokes = Array.from({ length: 24 }, (_, i) => i * 15);

  return (
    <div className={`${styles.splash} ${phase === 4 ? styles.fadeOut : ""}`}>
      {/* Particle canvas */}
      <canvas ref={canvasRef} className={styles.canvas} />

      {/* Radial glow behind logo */}
      <div className={styles.glow} />

      {/* India flag stripe (top) */}
      <div className={styles.flagTop}>
        <div className={styles.stripe} style={{ background: "#FF6B00" }} />
        <div className={styles.stripe} style={{ background: "#ffffff", opacity: 0.6 }} />
        <div className={styles.stripe} style={{ background: "#138808" }} />
      </div>

      {/* Main content */}
      <div className={styles.content}>

        {/* Ashoka Chakra */}
        <div className={`${styles.chakraWrap} ${phase >= 1 ? styles.chakraVisible : ""}`}>
          <div className={styles.chakra}>
            <svg viewBox="0 0 100 100" className={styles.chakraSvg}>
              <circle cx="50" cy="50" r="46" fill="none" stroke="#003580" strokeWidth="2" />
              <circle cx="50" cy="50" r="6" fill="#003580" />
              {spokes.map((angle) => (
                <line
                  key={angle}
                  x1="50" y1="50"
                  x2={50 + 44 * Math.cos((angle * Math.PI) / 180)}
                  y2={50 + 44 * Math.sin((angle * Math.PI) / 180)}
                  stroke="#003580"
                  strokeWidth="1.5"
                  opacity="0.8"
                />
              ))}
            </svg>
          </div>
        </div>

        {/* 3D Logo */}
        <div className={`${styles.logo3d} ${phase >= 1 ? styles.logoVisible : ""}`}>
          <div className={styles.logoInner}>
            <div className={styles.logoSeva}>Seva</div>
            <div className={styles.logoSetu}>Setu</div>
          </div>
          <div className={styles.logoAI}>
            <span>A</span><span>I</span>
          </div>
        </div>

        {/* Tagline */}
        <div className={`${styles.tagline} ${phase >= 2 ? styles.taglineVisible : ""}`}>
          Bridging Citizens to Government Services
        </div>

        {/* Inventor */}
        <div className={`${styles.inventor} ${phase >= 2 ? styles.inventorVisible : ""}`}>
          Invented by{" "}
          <span className={styles.authorName}>RAHUL JHA</span>
        </div>

        {/* Made in India */}
        <div className={`${styles.madeInIndia} ${phase >= 2 ? styles.madeVisible : ""}`}>
          <div className={styles.tricolorLine}>
            <span className={styles.tc} style={{ background: "#FF6B00" }} />
            <span className={styles.tc} style={{ background: "#fff", opacity: 0.7 }} />
            <span className={styles.tc} style={{ background: "#138808" }} />
          </div>
          <span className={styles.madeText}>🇮🇳 Made in India</span>
          <div className={styles.tricolorLine}>
            <span className={styles.tc} style={{ background: "#138808" }} />
            <span className={styles.tc} style={{ background: "#fff", opacity: 0.7 }} />
            <span className={styles.tc} style={{ background: "#FF6B00" }} />
          </div>
        </div>

        {/* Enter button */}
        <button
          className={`${styles.enterBtn} ${phase >= 3 ? styles.enterVisible : ""}`}
          onClick={handleEnter}
        >
          <span>Enter SevaSetu AI</span>
          <span className={styles.arrow}>→</span>
        </button>

        {/* Version pill */}
        <div className={`${styles.version} ${phase >= 3 ? styles.versionVisible : ""}`}>
          v1.0.0 · AI-Powered · Multilingual · Secure
        </div>
      </div>

      {/* India flag stripe (bottom) */}
      <div className={styles.flagBottom}>
        <div className={styles.stripe} style={{ background: "#FF6B00" }} />
        <div className={styles.stripe} style={{ background: "#ffffff", opacity: 0.6 }} />
        <div className={styles.stripe} style={{ background: "#138808" }} />
      </div>
    </div>
  );
}
