# Floorfall Survivor

`Floorfall Survivor` 是一个“是男人就下100层”风格的 2D 下落生存游戏，提供两种游玩方式：

- `Pygame` 窗口版
- `Vue 3 + Vite` 网页版

项目当前支持运行时选择游玩方式，并提供 `easy` / `hard` 两档难度。

## 功能概览

- 运行时启动器，可选择窗口版或网页版
- 窗口版开始菜单、暂停界面、结算界面
- 网页版响应式界面，支持键盘和触屏按钮
- 多种平台类型：普通、移动、脆弱、尖刺、弹跳
- 计分系统：生存时间 + 下落距离
- 本地最高分保存
- 简单 / 困难两种难度模式

## 目录结构

```text
.
├── main.py
├── launcher.py
├── build_web.py
├── game.py
├── player.py
├── game_platform.py
├── level_manager.py
├── ui.py
├── settings.py
├── requirements.txt
├── best_score.txt
├── README.md
├── 开发方案.md
└── web
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── src
    │   ├── App.vue
    │   ├── main.js
    │   ├── style.css
    │   └── game
    │       ├── constants.js
    │       └── engine.js
    └── dist
```

## 环境要求

- Python `3.10+`
- Node.js `18+`
- npm

## 安装依赖

窗口版依赖：

```bash
pip install -r requirements.txt
```

网页版开发依赖：

```bash
cd web
npm install
```

## 运行方式

### 运行时选择模式

```bash
python3 main.py
```

默认会弹出启动器窗口；如果图形环境不可用，则回退到命令行选择。

### 直接启动窗口版

```bash
python3 main.py --mode desktop --difficulty easy
python3 main.py --mode desktop --difficulty hard
```

### 直接启动网页版

```bash
python3 main.py --mode web --difficulty easy
python3 main.py --mode web --difficulty hard
```

如果不想自动打开浏览器：

```bash
python3 main.py --mode web --difficulty hard --no-browser
```

## 网页版构建

开发时可进入 `web/` 单独运行：

```bash
cd web
npm run dev
```

生成正式静态资源：

```bash
python3 build_web.py
```

`build_web.py` 会在 `/tmp` 临时目录中安装前端依赖并执行构建，然后把产物复制到 `web/dist/`。

## 操作说明

### 窗口版

- `A / D` 或 `← / →`：左右移动
- `Space / Enter`：开始或再来一局
- `P / ESC`：暂停 / 继续
- `R`：重新开始

### 网页版

- 键盘与窗口版一致
- 移动端可使用屏幕底部触控按钮

## 难度说明

### `easy`

- 平台更密
- 危险平台更少
- 平台宽度更大
- 下落速度更平缓

### `hard`

- 平台更稀
- 尖刺和复杂平台更常见
- 平台更窄
- 下落速度更快

## 平台类型

- `普通平台`：安全落脚点
- `移动平台`：左右移动，可带动角色
- `脆弱平台`：踩中后短暂延迟碎裂
- `尖刺平台`：碰到即死亡
- `弹跳平台`：落下后反弹

## 分数规则

最终分数由两部分构成：

- 生存时间
- 累计下落距离

最高分默认保存在 `best_score.txt`。

## 常见问题

### 网页版启动时报缺少 `web/dist`

先执行：

```bash
python3 build_web.py
```

### 没有图形界面时无法弹出启动器

程序会自动回退到命令行选择模式，不影响运行。

### 网页版无法自动打开浏览器

可以使用 `--no-browser`，然后手动访问终端输出的本地地址。

## 当前技术栈

- 窗口版：`Python + Pygame`
- 网页版：`Vue 3 + Vite + Canvas`
- 本地网页托管：`http.server`

## 相关文档

- 技术文档见 [开发方案.md](./开发方案.md)
