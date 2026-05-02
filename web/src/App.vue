<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import {
  DEFAULT_DIFFICULTY,
  GameEngine,
  STATE_GAME_OVER,
  STATE_PAUSED,
  STATE_PLAYING,
  STATE_START,
  WORLD_HEIGHT,
  WORLD_WIDTH,
} from "./game/engine.js";

const canvasRef = ref(null);
const engineRef = ref(null);
const hud = reactive({
  state: STATE_START,
  score: 0,
  bestScore: 0,
  elapsed: 0,
  speed: 140,
  difficulty: 0,
  difficultyMode: DEFAULT_DIFFICULTY,
  difficultyLabel: "简单",
});

const isPlaying = computed(() => hud.state === STATE_PLAYING);
const isPaused = computed(() => hud.state === STATE_PAUSED);
const isStart = computed(() => hud.state === STATE_START);
const isGameOver = computed(() => hud.state === STATE_GAME_OVER);
const difficultyLabel = computed(() => (hud.difficulty * 9 + 1).toFixed(1));
const primaryActionLabel = computed(() => (isGameOver.value ? "再来一局" : "开始游戏"));
const sideActionLabel = computed(() => (isPlaying.value ? "重新开始" : primaryActionLabel.value));
const selectedDifficulty = ref(resolveDifficultyFromQuery());

onMounted(() => {
  const engine = new GameEngine({
    canvas: canvasRef.value,
    onStateChange: (nextHud) => Object.assign(hud, nextHud),
    difficultyMode: selectedDifficulty.value,
  });
  engineRef.value = engine;
  engine.start();

  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeyDown);
  window.removeEventListener("keyup", handleKeyUp);
  engineRef.value?.destroy();
});

function handleKeyDown(event) {
  if (["ArrowLeft", "ArrowRight", "Space", "Enter", "Escape"].includes(event.code) || event.code.startsWith("Key")) {
    event.preventDefault();
  }
  engineRef.value?.handleKeyDown(event.code);
}

function handleKeyUp(event) {
  if (["ArrowLeft", "ArrowRight"].includes(event.code) || event.code === "KeyA" || event.code === "KeyD") {
    event.preventDefault();
  }
  engineRef.value?.handleKeyUp(event.code);
}

function pressDirection(direction, pressed) {
  engineRef.value?.setDirectionalInput(direction, pressed);
}

function startOrResume() {
  engineRef.value?.handleAction();
}

function restart() {
  engineRef.value?.restart();
}

function togglePause() {
  engineRef.value?.togglePause();
}

function handleSideAction() {
  if (isPlaying.value) {
    restart();
    return;
  }
  startOrResume();
}

function resolveDifficultyFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return params.get("difficulty") === "hard" ? "hard" : DEFAULT_DIFFICULTY;
}
</script>

<template>
  <main class="page-shell">
    <section class="hero-panel">
      <div class="hero-copy">
        <p class="eyebrow">Vue Web Mode</p>
        <h1>是男人就下100层</h1>
        <p class="summary">
          保留窗口版 `pygame` 玩法，同时补了一套 Vue 网页端。浏览器里可以键盘玩，也可以直接触屏玩。
        </p>
      </div>

      <div class="stats-grid">
        <article class="stat-card">
          <span>当前得分</span>
          <strong>{{ hud.score }}</strong>
        </article>
        <article class="stat-card">
          <span>最高分</span>
          <strong>{{ hud.bestScore }}</strong>
        </article>
        <article class="stat-card">
          <span>生存时间</span>
          <strong>{{ hud.elapsed.toFixed(1) }}s</strong>
        </article>
        <article class="stat-card">
          <span>当前模式</span>
          <strong>{{ hud.difficultyLabel }}</strong>
        </article>
      </div>
    </section>

    <section class="playground">
      <div class="canvas-frame">
        <div class="hud-panel">
          <div>
            <span class="hud-label">Score</span>
            <strong>{{ hud.score }}</strong>
          </div>
          <div>
            <span class="hud-label">Best</span>
            <strong>{{ hud.bestScore }}</strong>
          </div>
          <div>
            <span class="hud-label">Time</span>
            <strong>{{ hud.elapsed.toFixed(1) }}s</strong>
          </div>
          <div>
            <span class="hud-label">Speed</span>
            <strong>{{ Math.round(hud.speed) }}</strong>
          </div>
        </div>

        <canvas
          ref="canvasRef"
          class="game-canvas"
          :width="WORLD_WIDTH"
          :height="WORLD_HEIGHT"
        />

        <div v-if="isStart || isPaused || isGameOver" class="overlay">
          <div class="overlay-card">
            <template v-if="isStart">
              <p class="overlay-tag">Web Play</p>
              <h2>开始下落</h2>
              <p>当前难度：{{ hud.difficultyLabel }}</p>
              <p>键盘：A / D 或左右键移动，P / ESC 暂停，R 重新开始。</p>
              <p>手机：使用底部触控按钮控制左右移动。</p>
            </template>

            <template v-else-if="isPaused">
              <p class="overlay-tag">Paused</p>
              <h2>已暂停</h2>
              <p>按 P 或 ESC 继续，也可以点下面的继续按钮。</p>
            </template>

            <template v-else>
              <p class="overlay-tag">Game Over</p>
              <h2>本局 {{ hud.score }}</h2>
              <p>模式 {{ hud.difficultyLabel }}，坚持了 {{ hud.elapsed.toFixed(1) }} 秒，最高分 {{ hud.bestScore }}。</p>
            </template>

            <div class="overlay-actions">
              <button class="primary-button" @click="startOrResume">
                {{ isPaused ? "继续游戏" : primaryActionLabel }}
              </button>
              <button v-if="!isStart" class="secondary-button" @click="restart">
                重新开始
              </button>
            </div>
          </div>
        </div>
      </div>

      <aside class="control-panel">
        <div class="panel-block">
          <p class="panel-title">游玩方式</p>
          <p class="panel-text">电脑端优先用键盘，手机端可长按左右按钮持续移动。</p>
        </div>

        <div class="panel-block">
          <p class="panel-title">当前模式</p>
          <p class="panel-text">{{ hud.difficultyMode === "hard" ? "困难：平台更稀，危险板更多。" : "简单：平台更密，危险板更少。" }}</p>
        </div>

        <div class="panel-block">
          <p class="panel-title">操作提示</p>
          <p class="panel-text">踩中紫色平台会弹起，橙色平台会碎裂，红色尖刺会直接结束。</p>
        </div>

        <div class="panel-block panel-actions">
          <button class="primary-button" @click="handleSideAction">
            {{ sideActionLabel }}
          </button>
          <button class="secondary-button" :disabled="isStart" @click="togglePause">
            {{ isPaused ? "继续" : "暂停" }}
          </button>
        </div>
      </aside>
    </section>

    <section class="mobile-controls">
      <button
        class="control-button"
        @pointerdown="pressDirection('left', true)"
        @pointerup="pressDirection('left', false)"
        @pointerleave="pressDirection('left', false)"
        @pointercancel="pressDirection('left', false)"
      >
        向左
      </button>
      <button class="control-button accent" @click="togglePause">
        {{ isPaused ? "继续" : "暂停" }}
      </button>
      <button
        class="control-button"
        @pointerdown="pressDirection('right', true)"
        @pointerup="pressDirection('right', false)"
        @pointerleave="pressDirection('right', false)"
        @pointercancel="pressDirection('right', false)"
      >
        向右
      </button>
    </section>
  </main>
</template>

<style scoped>
.page-shell {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
  padding: 32px 0 28px;
}

.hero-panel {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 20px;
  align-items: stretch;
}

.hero-copy,
.stats-grid,
.control-panel,
.canvas-frame {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  box-shadow: 0 24px 64px var(--shadow);
  backdrop-filter: blur(18px);
}

.hero-copy {
  padding: 28px;
  border-radius: 28px;
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--accent);
  font-size: 0.9rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(2rem, 5vw, 4rem);
  line-height: 0.95;
}

.summary {
  margin: 18px 0 0;
  max-width: 34rem;
  color: var(--text-dim);
  font-size: 1.02rem;
  line-height: 1.7;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 18px;
  border-radius: 28px;
}

.stat-card {
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card span {
  display: block;
  color: var(--text-dim);
  font-size: 0.86rem;
}

.stat-card strong {
  display: block;
  margin-top: 10px;
  font-size: 1.6rem;
}

.playground {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(280px, 0.55fr);
  gap: 20px;
  margin-top: 22px;
}

.canvas-frame {
  position: relative;
  padding: 18px;
  border-radius: 34px;
  overflow: hidden;
}

.hud-panel {
  position: absolute;
  z-index: 2;
  top: 30px;
  left: 30px;
  display: grid;
  grid-template-columns: repeat(2, minmax(90px, 1fr));
  gap: 10px;
  padding: 12px;
  border-radius: 20px;
  background: rgba(6, 11, 19, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(14px);
}

.hud-panel strong {
  display: block;
  margin-top: 4px;
  font-size: 1.05rem;
}

.hud-label {
  display: block;
  color: var(--text-dim);
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.game-canvas {
  display: block;
  width: 100%;
  max-height: min(78vh, 800px);
  aspect-ratio: 3 / 5;
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.overlay {
  position: absolute;
  inset: 18px;
  z-index: 3;
  display: grid;
  place-items: center;
  padding: 20px;
  background: linear-gradient(180deg, rgba(4, 7, 13, 0.3), rgba(4, 7, 13, 0.72));
}

.overlay-card {
  width: min(420px, 100%);
  padding: 26px;
  border-radius: 26px;
  text-align: center;
  background: rgba(7, 12, 21, 0.86);
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 28px 64px rgba(0, 0, 0, 0.28);
}

.overlay-tag {
  margin: 0 0 8px;
  color: var(--accent);
  font-size: 0.88rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.overlay-card h2 {
  margin: 0;
  font-size: clamp(1.9rem, 4vw, 2.8rem);
}

.overlay-card p {
  margin: 14px 0 0;
  color: var(--text-dim);
  line-height: 1.65;
}

.overlay-actions,
.panel-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.overlay-actions {
  justify-content: center;
  margin-top: 22px;
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  border-radius: 30px;
}

.panel-block {
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-title {
  margin: 0;
  font-size: 0.92rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.panel-text {
  margin: 10px 0 0;
  color: var(--text-dim);
  line-height: 1.7;
}

.primary-button,
.secondary-button,
.control-button {
  border: 0;
  cursor: pointer;
  transition:
    transform 160ms ease,
    filter 160ms ease,
    opacity 160ms ease;
}

.primary-button,
.secondary-button {
  min-width: 136px;
  padding: 12px 18px;
  border-radius: 999px;
}

.primary-button {
  color: #1f2937;
  background: linear-gradient(135deg, #ffd05d, #ff9855);
  box-shadow: 0 16px 30px rgba(255, 162, 72, 0.28);
}

.secondary-button {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.secondary-button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.primary-button:hover,
.secondary-button:hover,
.control-button:hover {
  transform: translateY(-1px);
  filter: brightness(1.04);
}

.mobile-controls {
  display: none;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 16px;
}

.control-button {
  padding: 14px 12px;
  border-radius: 18px;
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  user-select: none;
  touch-action: manipulation;
}

.control-button.accent {
  background: rgba(255, 204, 84, 0.2);
  border-color: rgba(255, 204, 84, 0.3);
}

@media (max-width: 980px) {
  .hero-panel,
  .playground {
    grid-template-columns: 1fr;
  }

  .control-panel {
    order: -1;
  }
}

@media (max-width: 640px) {
  .page-shell {
    width: min(100% - 20px, 1200px);
    padding-top: 18px;
  }

  .hero-copy,
  .stats-grid,
  .canvas-frame,
  .control-panel {
    border-radius: 22px;
  }

  .canvas-frame {
    padding: 12px;
  }

  .overlay {
    inset: 12px;
  }

  .hud-panel {
    top: 22px;
    left: 22px;
    grid-template-columns: repeat(2, minmax(76px, 1fr));
  }

  .mobile-controls {
    display: grid;
  }
}
</style>
