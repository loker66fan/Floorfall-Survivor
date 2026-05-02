import {
  COLORS,
  DEFAULT_DIFFICULTY,
  DEATH_BUFFER,
  DIFFICULTY_LABELS,
  DIFFICULTY_PRESETS,
  FRAGILE_BREAK_DELAY,
  LANDING_TOLERANCE,
  MOVING_PLATFORM_SPEED_MAX,
  MOVING_PLATFORM_SPEED_MIN,
  PLATFORM_BOUNCE,
  PLATFORM_EDGE_PADDING,
  PLATFORM_FRAGILE,
  PLATFORM_GAP_MAX,
  PLATFORM_GAP_MIN,
  PLATFORM_HEIGHT,
  PLATFORM_MAX_WIDTH,
  PLATFORM_MIN_WIDTH,
  PLATFORM_MOVING,
  PLATFORM_NORMAL,
  PLATFORM_SPIKE,
  PLATFORM_SPAWN_BUFFER,
  PLATFORM_TARGET_COUNT,
  PLAYER_BOUNCE_SPEED,
  PLAYER_GRAVITY,
  PLAYER_HEIGHT,
  PLAYER_MAX_FALL_SPEED,
  PLAYER_MOVE_SPEED,
  PLAYER_START_X,
  PLAYER_START_Y,
  PLAYER_WIDTH,
  SCORE_DISTANCE_FACTOR,
  SCORE_TIME_FACTOR,
  STATE_GAME_OVER,
  STATE_PAUSED,
  STATE_PLAYING,
  STATE_START,
  TOP_BOUNDARY_Y,
  WORLD_HEIGHT,
  WORLD_SCROLL_ACCEL,
  WORLD_SCROLL_BASE,
  WORLD_SCROLL_MAX,
  WORLD_WIDTH,
} from "./constants.js";

class Player {
  constructor() {
    this.reset();
  }

  reset() {
    this.x = PLAYER_START_X;
    this.y = PLAYER_START_Y;
    this.prevX = this.x;
    this.prevY = this.y;
    this.vy = 0;
    this.alive = true;
    this.facing = 1;
  }

  beginFrame() {
    this.prevX = this.x;
    this.prevY = this.y;
  }

  handleInput(input, dt) {
    const direction = Number(input.right) - Number(input.left);
    if (direction !== 0) {
      this.x += direction * PLAYER_MOVE_SPEED * dt;
      this.facing = direction > 0 ? 1 : -1;
    }
    this.x = clamp(this.x, 0, WORLD_WIDTH - PLAYER_WIDTH);
  }

  update(dt) {
    this.vy = Math.min(this.vy + PLAYER_GRAVITY * dt, PLAYER_MAX_FALL_SPEED);
    this.y += this.vy * dt;
  }

  landOn(platform) {
    this.y = platform.y - PLAYER_HEIGHT;
    this.vy = 0;
  }

  ridePlatform(dx) {
    this.x = clamp(this.x + dx, 0, WORLD_WIDTH - PLAYER_WIDTH);
  }

  bounce(power = PLAYER_BOUNCE_SPEED) {
    this.vy = -power;
  }

  hitCeiling(boundaryY) {
    this.y = boundaryY;
    if (this.vy < 0) {
      this.vy = 0;
    }
  }

  die() {
    this.alive = false;
  }

  get rect() {
    return {
      left: this.x,
      right: this.x + PLAYER_WIDTH,
      top: this.y,
      bottom: this.y + PLAYER_HEIGHT,
      width: PLAYER_WIDTH,
      height: PLAYER_HEIGHT,
      centerX: this.x + PLAYER_WIDTH / 2,
      centerY: this.y + PLAYER_HEIGHT / 2,
    };
  }

  get prevRect() {
    return {
      left: this.prevX,
      right: this.prevX + PLAYER_WIDTH,
      top: this.prevY,
      bottom: this.prevY + PLAYER_HEIGHT,
      width: PLAYER_WIDTH,
      height: PLAYER_HEIGHT,
    };
  }
}

class Platform {
  constructor({ x, y, width, kind = PLATFORM_NORMAL, moveSpeed = 0, moveDirection = 1 }) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.kind = kind;
    this.moveSpeed = kind === PLATFORM_MOVING && moveSpeed <= 0 ? (MOVING_PLATFORM_SPEED_MIN + MOVING_PLATFORM_SPEED_MAX) / 2 : moveSpeed;
    this.moveDirection = moveDirection;
    this.broken = false;
    this.breaking = false;
    this.breakTimer = null;
    this.frameDx = 0;
    this.prevX = this.x;
    this.prevY = this.y;
  }

  beginFrame() {
    this.prevX = this.x;
    this.prevY = this.y;
    this.frameDx = 0;
  }

  update(dt) {
    if (this.breaking && this.breakTimer !== null) {
      this.breakTimer -= dt;
      if (this.breakTimer <= 0) {
        this.broken = true;
      }
    }

    if (this.broken) {
      return;
    }

    if (this.kind === PLATFORM_MOVING) {
      this.frameDx = this.moveSpeed * this.moveDirection * dt;
      this.x += this.frameDx;
      if (this.x <= 0) {
        this.x = 0;
        this.moveDirection = 1;
      } else if (this.x + this.width >= WORLD_WIDTH) {
        this.x = WORLD_WIDTH - this.width;
        this.moveDirection = -1;
      }
    }
  }

  shift(dy) {
    this.y += dy;
  }

  triggerFragile() {
    if (this.kind === PLATFORM_FRAGILE && !this.breaking) {
      this.breaking = true;
      this.breakTimer = FRAGILE_BREAK_DELAY;
    }
  }

  shouldRemove() {
    return this.broken || this.y + PLATFORM_HEIGHT < -90;
  }

  get isSolid() {
    return !this.broken && this.kind !== PLATFORM_SPIKE;
  }

  get rect() {
    return {
      left: this.x,
      right: this.x + this.width,
      top: this.y,
      bottom: this.y + PLATFORM_HEIGHT,
      width: this.width,
      height: PLATFORM_HEIGHT,
      centerX: this.x + this.width / 2,
      centerY: this.y + PLATFORM_HEIGHT / 2,
    };
  }

  get prevRect() {
    return {
      left: this.prevX,
      right: this.prevX + this.width,
      top: this.prevY,
      bottom: this.prevY + PLATFORM_HEIGHT,
      width: this.width,
      height: PLATFORM_HEIGHT,
    };
  }
}

class LevelManager {
  constructor(difficultyMode = DEFAULT_DIFFICULTY) {
    this.setDifficultyMode(difficultyMode);
    this.reset();
  }

  setDifficultyMode(difficultyMode) {
    this.difficultyMode = DIFFICULTY_PRESETS[difficultyMode] ? difficultyMode : DEFAULT_DIFFICULTY;
    this.preset = DIFFICULTY_PRESETS[this.difficultyMode];
  }

  reset() {
    this.spawnCursor = PLAYER_START_Y + PLAYER_HEIGHT + 40;
    this.lastSpawnX = PLAYER_START_X;
    this.spikeStreak = 0;
  }

  buildInitialPlatforms() {
    this.reset();
    const platforms = [];

    const startWidth = 132;
    const startX = clamp(PLAYER_START_X - 46, PLATFORM_EDGE_PADDING, WORLD_WIDTH - startWidth - PLATFORM_EDGE_PADDING);
    const startY = PLAYER_START_Y + PLAYER_HEIGHT + 34;
    platforms.push(new Platform({ x: startX, y: startY, width: startWidth, kind: PLATFORM_NORMAL }));
    this.lastSpawnX = startX;
    this.spawnCursor = startY;

    while (this.spawnCursor < WORLD_HEIGHT + PLATFORM_SPAWN_BUFFER + this.preset.spawnBufferOffset) {
      const platform = this.spawnPlatform(this.spawnCursor + this.nextGap(0), 0, true);
      platforms.push(platform);
      this.spawnCursor = platform.y;
    }

    return platforms;
  }

  ensurePlatforms(platforms, difficulty) {
    if (platforms.length > 0) {
      this.spawnCursor = Math.max(this.spawnCursor, ...platforms.map((platform) => platform.y));
    }

    const targetCount = Math.max(10, PLATFORM_TARGET_COUNT + this.preset.platformCountBonus);
    const spawnLimit = WORLD_HEIGHT + PLATFORM_SPAWN_BUFFER + this.preset.spawnBufferOffset;
    let activeCount = platforms.filter((platform) => !platform.broken).length;
    while (activeCount < targetCount || this.spawnCursor < spawnLimit) {
      const platform = this.spawnPlatform(this.spawnCursor + this.nextGap(difficulty), difficulty, false);
      platforms.push(platform);
      this.spawnCursor = platform.y;
      activeCount += 1;
    }
  }

  spawnPlatform(y, difficulty, safeBias = false) {
    const widthShrink = Math.trunc(20 * difficulty);
    const minWidth = Math.max(68, PLATFORM_MIN_WIDTH - widthShrink + this.preset.widthBonus);
    const maxWidth = Math.max(minWidth + 8, PLATFORM_MAX_WIDTH - widthShrink + this.preset.widthBonus);
    const width = randomInt(minWidth, maxWidth);

    const reach = Math.trunc(160 + difficulty * 65 + this.preset.reachBonus);
    let x = 0;
    if (Math.random() < 0.2) {
      x = randomInt(PLATFORM_EDGE_PADDING, WORLD_WIDTH - width - PLATFORM_EDGE_PADDING);
    } else {
      let minX = Math.max(PLATFORM_EDGE_PADDING, Math.trunc(this.lastSpawnX - reach));
      let maxX = Math.min(WORLD_WIDTH - width - PLATFORM_EDGE_PADDING, Math.trunc(this.lastSpawnX + reach));
      if (minX > maxX) {
        minX = PLATFORM_EDGE_PADDING;
        maxX = WORLD_WIDTH - width - PLATFORM_EDGE_PADDING;
      }
      x = randomInt(minX, maxX);
    }

    const kind = this.choosePlatformType(difficulty, safeBias);
    let moveSpeed = 0;
    let moveDirection = 1;
    if (kind === PLATFORM_MOVING) {
      moveSpeed = randomFloat(MOVING_PLATFORM_SPEED_MIN, MOVING_PLATFORM_SPEED_MAX + difficulty * 20);
      moveDirection = Math.random() < 0.5 ? -1 : 1;
    }

    this.lastSpawnX = x;
    if (kind === PLATFORM_SPIKE) {
      this.spikeStreak += 1;
    } else {
      this.spikeStreak = 0;
    }

    return new Platform({ x, y, width, kind, moveSpeed, moveDirection });
  }

  choosePlatformType(difficulty, safeBias = false) {
    if (safeBias) {
      const choices = [PLATFORM_NORMAL, PLATFORM_MOVING, PLATFORM_FRAGILE];
      for (let index = 0; index < this.preset.safeChoiceBias; index += 1) {
        choices.push(PLATFORM_NORMAL);
      }
      return choices[randomInt(0, choices.length - 1)];
    }

    if (this.spikeStreak >= 1) {
      return [PLATFORM_NORMAL, PLATFORM_MOVING, PLATFORM_FRAGILE, PLATFORM_BOUNCE][randomInt(0, 3)];
    }

    const weights = [
      [PLATFORM_MOVING, 0.16 + difficulty * 0.06 + this.preset.movingWeightBonus],
      [PLATFORM_FRAGILE, 0.13 + difficulty * 0.04 + this.preset.fragileWeightBonus],
      [PLATFORM_SPIKE, (0.08 + difficulty * 0.11) * this.preset.hazardWeightScale],
      [PLATFORM_BOUNCE, 0.08 + difficulty * 0.03 + this.preset.bounceWeightBonus],
    ];
    const weightedOthers = weights.reduce((sum, [, weight]) => sum + Math.max(0.02, weight), 0);
    weights.unshift([PLATFORM_NORMAL, Math.max(0.25, 1 - weightedOthers)]);
    const total = weights.reduce((sum, [, weight]) => sum + Math.max(0.02, weight), 0);
    let pick = Math.random() * total;
    for (const [kind, weight] of weights) {
      pick -= Math.max(0.02, weight);
      if (pick <= 0) {
        return kind;
      }
    }
    return PLATFORM_NORMAL;
  }

  nextGap(difficulty) {
    const extraGap = Math.trunc(26 * difficulty);
    const minGap = Math.max(58, PLATFORM_GAP_MIN + Math.trunc(extraGap / 2) + this.preset.gapMinOffset);
    const maxGap = Math.max(minGap + 8, PLATFORM_GAP_MAX + extraGap + this.preset.gapMaxOffset);
    return randomInt(minGap, maxGap);
  }
}

export class GameEngine {
  constructor({ canvas, onStateChange, difficultyMode = DEFAULT_DIFFICULTY }) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.onStateChange = onStateChange;
    this.levelManager = new LevelManager(difficultyMode);
    this.player = new Player();
    this.platforms = [];
    this.state = STATE_START;
    this.running = false;
    this.elapsed = 0;
    this.totalScroll = 0;
    this.score = 0;
    this.bestScore = loadBestScore();
    this.currentScrollSpeed = WORLD_SCROLL_BASE;
    this.currentDifficulty = 0;
    this.difficultyMode = this.levelManager.difficultyMode;
    this.difficultyLabel = DIFFICULTY_LABELS[this.difficultyMode];
    this.scrollSpeedMultiplier = this.levelManager.preset.scrollSpeedMultiplier;
    this.lastTime = 0;
    this.rafId = 0;
    this.input = { left: false, right: false };
    this.backgroundOffset = 0;
    this.handleVisibilityChange = this.handleVisibilityChange.bind(this);

    this.platforms = this.levelManager.buildInitialPlatforms();
    this.emit();
    this.draw();
    document.addEventListener("visibilitychange", this.handleVisibilityChange);
  }

  destroy() {
    this.running = false;
    cancelAnimationFrame(this.rafId);
    document.removeEventListener("visibilitychange", this.handleVisibilityChange);
  }

  handleVisibilityChange() {
    if (document.hidden && this.state === STATE_PLAYING) {
      this.pause();
    }
  }

  start() {
    if (!this.running) {
      this.running = true;
      this.rafId = requestAnimationFrame((time) => this.loop(time));
    }
  }

  loop(timestamp) {
    if (!this.running) {
      return;
    }

    if (this.lastTime === 0) {
      this.lastTime = timestamp;
    }
    const dt = Math.min((timestamp - this.lastTime) / 1000, 1 / 20);
    this.lastTime = timestamp;

    if (this.state === STATE_PLAYING) {
      this.update(dt);
    }
    this.draw();
    this.emit();

    this.rafId = requestAnimationFrame((time) => this.loop(time));
  }

  startRound() {
    this.player.reset();
    this.platforms = this.levelManager.buildInitialPlatforms();
    this.elapsed = 0;
    this.totalScroll = 0;
    this.score = 0;
    this.currentScrollSpeed = WORLD_SCROLL_BASE * this.scrollSpeedMultiplier;
    this.currentDifficulty = 0;
    this.state = STATE_PLAYING;
  }

  restart() {
    this.startRound();
  }

  pause() {
    if (this.state === STATE_PLAYING) {
      this.state = STATE_PAUSED;
    }
  }

  resume() {
    if (this.state === STATE_PAUSED) {
      this.state = STATE_PLAYING;
    }
  }

  togglePause() {
    if (this.state === STATE_PLAYING) {
      this.pause();
    } else if (this.state === STATE_PAUSED) {
      this.resume();
    }
  }

  setDirectionalInput(direction, pressed) {
    if (direction === "left") {
      this.input.left = pressed;
    }
    if (direction === "right") {
      this.input.right = pressed;
    }
  }

  handleAction() {
    if (this.state === STATE_START || this.state === STATE_GAME_OVER) {
      this.startRound();
      return;
    }
    if (this.state === STATE_PAUSED) {
      this.resume();
    }
  }

  handleKeyDown(code) {
    if (code === "ArrowLeft" || code === "KeyA") {
      this.setDirectionalInput("left", true);
      return;
    }
    if (code === "ArrowRight" || code === "KeyD") {
      this.setDirectionalInput("right", true);
      return;
    }
    if (code === "Space" || code === "Enter") {
      this.handleAction();
      return;
    }
    if (code === "KeyR") {
      this.restart();
      return;
    }
    if (code === "KeyP" || code === "Escape") {
      if (this.state !== STATE_START && this.state !== STATE_GAME_OVER) {
        this.togglePause();
      }
    }
  }

  handleKeyUp(code) {
    if (code === "ArrowLeft" || code === "KeyA") {
      this.setDirectionalInput("left", false);
    }
    if (code === "ArrowRight" || code === "KeyD") {
      this.setDirectionalInput("right", false);
    }
  }

  update(dt) {
    this.elapsed += dt;
    this.currentDifficulty = Math.min(1, this.elapsed / 85);
    this.currentScrollSpeed = Math.min(
      (WORLD_SCROLL_BASE + this.elapsed * WORLD_SCROLL_ACCEL) * this.scrollSpeedMultiplier,
      WORLD_SCROLL_MAX * this.scrollSpeedMultiplier,
    );
    const scrollStep = this.currentScrollSpeed * dt;
    this.totalScroll += scrollStep;
    this.backgroundOffset += scrollStep * 0.6;

    this.player.beginFrame();
    for (const platform of this.platforms) {
      platform.beginFrame();
    }

    this.player.handleInput(this.input, dt);
    this.player.update(dt);

    for (const platform of this.platforms) {
      platform.update(dt);
      platform.shift(-scrollStep);
    }

    this.resolveCollisions();
    this.handleTopBoundary();

    this.platforms = this.platforms.filter((platform) => !platform.shouldRemove());
    this.levelManager.ensurePlatforms(this.platforms, this.currentDifficulty);

    this.score = Math.trunc(this.elapsed * SCORE_TIME_FACTOR + this.totalScroll * SCORE_DISTANCE_FACTOR);
    if (!this.player.alive || this.player.rect.top > WORLD_HEIGHT + DEATH_BUFFER) {
      this.finishRound();
    }
  }

  resolveCollisions() {
    let landingPlatform = null;
    const playerRect = this.player.rect;
    const playerPrevRect = this.player.prevRect;

    for (const platform of this.platforms) {
      if (platform.broken) {
        continue;
      }

      if (platform.kind === PLATFORM_SPIKE && rectsOverlap(playerRect, insetRect(platform.rect, 8, 3))) {
        this.player.die();
        return;
      }

      if (this.player.vy < 0 || !platform.isSolid) {
        continue;
      }

      if (!rectsOverlap(playerRect, platform.rect)) {
        continue;
      }

      const landedFromAbove =
        playerPrevRect.bottom <= platform.prevRect.top + LANDING_TOLERANCE && playerRect.bottom >= platform.rect.top;

      if (landedFromAbove) {
        if (!landingPlatform || platform.rect.top < landingPlatform.rect.top) {
          landingPlatform = platform;
        }
      }
    }

    if (!landingPlatform) {
      return;
    }

    this.player.landOn(landingPlatform);
    if (landingPlatform.kind === PLATFORM_MOVING) {
      this.player.ridePlatform(landingPlatform.frameDx);
    } else if (landingPlatform.kind === PLATFORM_FRAGILE) {
      landingPlatform.triggerFragile();
    } else if (landingPlatform.kind === PLATFORM_BOUNCE) {
      this.player.bounce();
    }
  }

  handleTopBoundary() {
    if (this.player.rect.top > TOP_BOUNDARY_Y) {
      return;
    }

    this.player.hitCeiling(TOP_BOUNDARY_Y);
    for (const platform of this.platforms) {
      if (platform.isSolid && rectsOverlap(this.player.rect, platform.rect)) {
        this.player.die();
        return;
      }
    }
  }

  finishRound() {
    this.state = STATE_GAME_OVER;
    if (this.score > this.bestScore) {
      this.bestScore = this.score;
      saveBestScore(this.bestScore);
    }
  }

  emit() {
    if (!this.onStateChange) {
      return;
    }

    this.onStateChange({
      state: this.state,
      score: this.score,
      bestScore: this.bestScore,
      elapsed: this.elapsed,
      speed: this.currentScrollSpeed,
      difficulty: this.currentDifficulty,
      difficultyMode: this.difficultyMode,
      difficultyLabel: this.difficultyLabel,
    });
  }

  draw() {
    const ctx = this.ctx;
    if (!ctx) {
      return;
    }

    ctx.clearRect(0, 0, WORLD_WIDTH, WORLD_HEIGHT);
    drawBackground(ctx, this.backgroundOffset);

    for (const platform of this.platforms) {
      drawPlatform(ctx, platform);
    }

    if (this.state !== STATE_START || this.platforms.length > 0) {
      drawPlayer(ctx, this.player);
    }
  }
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomFloat(min, max) {
  return Math.random() * (max - min) + min;
}

function rectsOverlap(a, b) {
  return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
}

function insetRect(rect, insetX, insetY) {
  return {
    left: rect.left + insetX,
    right: rect.right - insetX,
    top: rect.top + insetY,
    bottom: rect.bottom - insetY,
  };
}

function loadBestScore() {
  try {
    return Number.parseInt(window.localStorage.getItem("down100_best_score") ?? "0", 10) || 0;
  } catch {
    return 0;
  }
}

function saveBestScore(score) {
  try {
    window.localStorage.setItem("down100_best_score", String(score));
  } catch {
    return;
  }
}

function drawBackground(ctx, scrollDistance) {
  const gradient = ctx.createLinearGradient(0, 0, 0, WORLD_HEIGHT);
  gradient.addColorStop(0, COLORS.backgroundTop);
  gradient.addColorStop(1, COLORS.backgroundBottom);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, WORLD_WIDTH, WORLD_HEIGHT);

  ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
  ctx.lineWidth = 1;
  const offset = Math.trunc(scrollDistance) % 80;

  for (let x = 40; x < WORLD_WIDTH; x += 80) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, WORLD_HEIGHT);
    ctx.stroke();
  }

  for (let y = -80; y < WORLD_HEIGHT + 80; y += 80) {
    const lineY = y - offset;
    ctx.beginPath();
    ctx.moveTo(0, lineY);
    ctx.lineTo(WORLD_WIDTH, lineY);
    ctx.stroke();
  }

  for (let index = 0; index < 6; index += 1) {
    const radius = 18 + index * 12;
    const alpha = Math.max(0.08, 0.26 - index * 0.03);
    ctx.fillStyle = `rgba(255, 214, 102, ${alpha})`;
    ctx.beginPath();
    ctx.arc(WORLD_WIDTH - 115 - index * 10, 92 + index * 12, radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawPlatform(ctx, platform) {
  if (platform.broken) {
    return;
  }

  roundRect(ctx, platform.x, platform.y + 4, platform.width, PLATFORM_HEIGHT, 9, COLORS.shadow);
  roundRect(ctx, platform.x, platform.y, platform.width, PLATFORM_HEIGHT, 9, COLORS.platform[platform.kind]);

  ctx.strokeStyle = "rgba(255, 255, 255, 0.9)";
  ctx.lineWidth = 2;
  strokeRoundRect(ctx, platform.x + 8, platform.y + 4, platform.width - 16, PLATFORM_HEIGHT - 10, 6);

  if (platform.kind === PLATFORM_MOVING) {
    drawMovingIndicator(ctx, platform);
  } else if (platform.kind === PLATFORM_FRAGILE) {
    drawFragileIndicator(ctx, platform);
  } else if (platform.kind === PLATFORM_SPIKE) {
    drawSpikes(ctx, platform);
  } else if (platform.kind === PLATFORM_BOUNCE) {
    drawBounceIndicator(ctx, platform);
  }
}

function drawMovingIndicator(ctx, platform) {
  const centerY = platform.y + PLATFORM_HEIGHT / 2;
  const leftX = platform.x + 16;
  const rightX = platform.x + platform.width - 16;
  ctx.strokeStyle = "#123563";
  ctx.fillStyle = "#123563";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(leftX, centerY);
  ctx.lineTo(rightX, centerY);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(leftX, centerY);
  ctx.lineTo(leftX + 10, centerY - 7);
  ctx.lineTo(leftX + 10, centerY + 7);
  ctx.closePath();
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(rightX, centerY);
  ctx.lineTo(rightX - 10, centerY - 7);
  ctx.lineTo(rightX - 10, centerY + 7);
  ctx.closePath();
  ctx.fill();
}

function drawFragileIndicator(ctx, platform) {
  ctx.strokeStyle = "#7a572c";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(platform.x + 12, platform.y + 5);
  ctx.lineTo(platform.x + platform.width / 2 - 5, platform.y + PLATFORM_HEIGHT / 2);
  ctx.lineTo(platform.x + platform.width / 2 + 4, platform.y + 4);
  ctx.lineTo(platform.x + platform.width - 14, platform.y + PLATFORM_HEIGHT / 2 + 4);
  ctx.stroke();
}

function drawSpikes(ctx, platform) {
  const count = Math.max(4, Math.floor(platform.width / 16));
  const spikeWidth = platform.width / count;
  ctx.fillStyle = "#7b0d18";
  for (let index = 0; index < count; index += 1) {
    const left = platform.x + spikeWidth * index;
    const right = left + spikeWidth;
    const top = platform.y - 10;
    ctx.beginPath();
    ctx.moveTo(left, platform.y + PLATFORM_HEIGHT - 2);
    ctx.lineTo((left + right) / 2, top);
    ctx.lineTo(right, platform.y + PLATFORM_HEIGHT - 2);
    ctx.closePath();
    ctx.fill();
  }
}

function drawBounceIndicator(ctx, platform) {
  const baseY = platform.y + PLATFORM_HEIGHT / 2 + 1;
  const points = [
    [platform.x + 18, baseY],
    [platform.x + 28, baseY - 5],
    [platform.x + 38, baseY + 5],
    [platform.x + 48, baseY - 5],
    [platform.x + 58, baseY + 5],
    [platform.x + platform.width - 18, baseY],
  ];
  ctx.strokeStyle = "#522491";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(points[0][0], points[0][1]);
  for (let index = 1; index < points.length; index += 1) {
    ctx.lineTo(points[index][0], points[index][1]);
  }
  ctx.stroke();
}

function drawPlayer(ctx, player) {
  const { left, top, width, height, centerX, centerY } = player.rect;
  roundRect(ctx, left, top + 5, width, height, 12, COLORS.shadow);
  roundRect(ctx, left, top, width, height, 12, COLORS.player);
  roundRect(ctx, left + 7, top + 8, width - 14, 11, 6, COLORS.playerAccent);

  const eyeY = centerY + 3;
  const offset = 5 * player.facing;
  ctx.fillStyle = "#302212";
  ctx.beginPath();
  ctx.arc(centerX - 6 + offset, eyeY, 2, 0, Math.PI * 2);
  ctx.arc(centerX + 2 + offset, eyeY, 2, 0, Math.PI * 2);
  ctx.fill();

  const feetY = top + height - 4;
  ctx.strokeStyle = "#a65823";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(left + 9, feetY);
  ctx.lineTo(left + 15, feetY);
  ctx.moveTo(left + width - 15, feetY);
  ctx.lineTo(left + width - 9, feetY);
  ctx.stroke();
}

function roundRect(ctx, x, y, width, height, radius, fillStyle) {
  ctx.fillStyle = fillStyle;
  ctx.beginPath();
  ctx.roundRect(x, y, width, height, radius);
  ctx.fill();
}

function strokeRoundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  ctx.roundRect(x, y, width, height, radius);
  ctx.stroke();
}

export {
  DEFAULT_DIFFICULTY,
  DIFFICULTY_LABELS,
  STATE_GAME_OVER,
  STATE_PAUSED,
  STATE_PLAYING,
  STATE_START,
  WORLD_HEIGHT,
  WORLD_WIDTH,
};
