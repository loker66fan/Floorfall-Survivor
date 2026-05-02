from __future__ import annotations

import argparse
import sys
import threading
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from settings import DEFAULT_DIFFICULTY, DIFFICULTY_LABELS, DIFFICULTY_PRESETS


PROJECT_ROOT = Path(__file__).resolve().parent
WEB_DIST_DIR = PROJECT_ROOT / "web" / "dist"


class SpaRequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):  # type: ignore[override]
        path = self.translate_path(self.path)
        requested = Path(path)

        if self.path == "/" or requested.exists():
            return super().send_head()

        self.path = "/index.html"
        return super().send_head()


def run_desktop(difficulty: str = DEFAULT_DIFFICULTY) -> None:
    from game import Game

    Game(difficulty_mode=difficulty).run()


def run_web(difficulty: str = DEFAULT_DIFFICULTY, open_browser: bool = True) -> None:
    if not WEB_DIST_DIR.exists():
        raise FileNotFoundError(
            f"未找到网页资源目录：{WEB_DIST_DIR}\n"
            "请先执行 python3 build_web.py 生成网页静态资源。"
        )

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(SpaRequestHandler, directory=str(WEB_DIST_DIR)),
    )
    host, port = server.server_address
    url = f"http://{host}:{port}?difficulty={difficulty}"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    if open_browser:
        webbrowser.open(url, new=2)

    print(f"网页模式已启动：{url}")
    print("浏览器关闭后，可在终端按 Ctrl+C 停止本地服务。")

    try:
        while thread.is_alive():
            thread.join(timeout=0.5)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n正在关闭网页服务...")
    finally:
        server.shutdown()
        server.server_close()


def launch(mode: str, difficulty: str = DEFAULT_DIFFICULTY, open_browser: bool = True) -> None:
    if mode == "desktop":
        run_desktop(difficulty=difficulty)
        return
    if mode == "web":
        run_web(difficulty=difficulty, open_browser=open_browser)
        return
    raise ValueError(f"未知模式: {mode}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="是男人就下100层 启动器")
    parser.add_argument(
        "--mode",
        choices=("prompt", "desktop", "web"),
        default="prompt",
        help="启动模式：prompt 为运行时选择，desktop 为窗口版，web 为网页版本。",
    )
    parser.add_argument(
        "--difficulty",
        choices=tuple(DIFFICULTY_PRESETS.keys()),
        default=DEFAULT_DIFFICULTY,
        help="难度模式：easy 为简单，hard 为困难。",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="网页模式下不自动打开浏览器。",
    )
    return parser


def choose_mode_interactively() -> tuple[str, str] | None:
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:
        return _choose_mode_cli()

    selection: dict[str, str | None] = {"mode": None, "difficulty": DEFAULT_DIFFICULTY}

    try:
        root = tk.Tk()
    except Exception:
        return _choose_mode_cli()

    root.title("是男人就下100层 启动台")
    root.resizable(False, False)
    root.configure(bg="#0b1020")
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("Picker.TFrame", background="#0b1020")
    style.configure("Picker.TLabelframe", background="#111831", foreground="#f8fafc")
    style.configure("Picker.TLabelframe.Label", background="#111831", foreground="#f8fafc", font=("Microsoft YaHei UI", 11, "bold"))
    style.configure("Picker.TLabel", background="#0b1020", foreground="#d6def7", font=("Microsoft YaHei UI", 11))
    style.configure("PickerTitle.TLabel", background="#0b1020", foreground="#f8fafc", font=("Microsoft YaHei UI", 20, "bold"))
    style.configure("PickerSub.TLabel", background="#0b1020", foreground="#f3c969", font=("Microsoft YaHei UI", 10))
    style.configure("Picker.TRadiobutton", background="#111831", foreground="#eef3ff", font=("Microsoft YaHei UI", 11))
    style.map("Picker.TRadiobutton", background=[("active", "#111831")], foreground=[("active", "#ffffff")])
    style.configure("Launch.TButton", font=("Microsoft YaHei UI", 11, "bold"), padding=10)
    style.configure("Ghost.TButton", font=("Microsoft YaHei UI", 10), padding=8)

    container = tk.Frame(root, bg="#0b1020", padx=22, pady=22, highlightthickness=0)
    container.grid()

    header = tk.Frame(container, bg="#0b1020")
    header.grid(row=0, column=0, sticky="ew")
    tk.Label(
        header,
        text="是男人就下100层",
        bg="#0b1020",
        fg="#f8fafc",
        font=("Microsoft YaHei UI", 22, "bold"),
    ).grid(row=0, column=0, sticky="w")
    tk.Label(
        header,
        text="选择游玩方式与难度",
        bg="#0b1020",
        fg="#f3c969",
        font=("Microsoft YaHei UI", 10),
    ).grid(row=1, column=0, sticky="w", pady=(6, 0))

    card_row = tk.Frame(container, bg="#0b1020")
    card_row.grid(row=1, column=0, pady=(18, 14), sticky="ew")

    difficulty_var = tk.StringVar(value=DEFAULT_DIFFICULTY)

    def pick(mode: str) -> None:
        selection["mode"] = mode
        selection["difficulty"] = difficulty_var.get()
        root.destroy()

    def add_mode_card(parent: tk.Widget, *, title: str, subtitle: str, detail: str, button_text: str, mode: str, accent: str) -> None:
        card = tk.Frame(parent, bg="#111831", bd=0, highlightthickness=1, highlightbackground="#253154", padx=16, pady=16)
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(card, text=title, bg="#111831", fg="#ffffff", font=("Microsoft YaHei UI", 15, "bold")).pack(anchor="w")
        tk.Label(card, text=subtitle, bg="#111831", fg=accent, font=("Microsoft YaHei UI", 10)).pack(anchor="w", pady=(6, 0))
        tk.Label(
            card,
            text=detail,
            bg="#111831",
            fg="#c5d1ee",
            font=("Microsoft YaHei UI", 10),
            justify="left",
            wraplength=210,
        ).pack(anchor="w", pady=(12, 16))
        ttk.Button(card, text=button_text, style="Launch.TButton", command=lambda: pick(mode)).pack(fill="x")

    add_mode_card(
        card_row,
        title="窗口游玩",
        subtitle="Pygame 桌面版",
        detail="原生窗口运行，适合键盘操作，响应更直接。",
        button_text="启动窗口版",
        mode="desktop",
        accent="#7dd3fc",
    )
    add_mode_card(
        card_row,
        title="网页游玩",
        subtitle="Vue 浏览器版",
        detail="自动启动本地网页，可在电脑浏览器或手机浏览器游玩。",
        button_text="启动网页版",
        mode="web",
        accent="#fca5a5",
    )

    difficulty_frame = ttk.LabelFrame(container, text="难度设置", style="Picker.TLabelframe", padding=14)
    difficulty_frame.grid(row=2, column=0, sticky="ew")
    ttk.Radiobutton(
        difficulty_frame,
        text="简单  平台更密、危险板更少、节奏更稳",
        value="easy",
        variable=difficulty_var,
        style="Picker.TRadiobutton",
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))
    ttk.Radiobutton(
        difficulty_frame,
        text="困难  平台更稀、危险板更多、下落更快",
        value="hard",
        variable=difficulty_var,
        style="Picker.TRadiobutton",
    ).grid(row=1, column=0, sticky="w")

    footer = tk.Frame(container, bg="#0b1020")
    footer.grid(row=3, column=0, sticky="ew", pady=(14, 0))
    ttk.Label(footer, text="关闭窗口则取消启动", style="Picker.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Button(footer, text="取消", style="Ghost.TButton", command=root.destroy).grid(row=0, column=1, sticky="e")
    footer.grid_columnconfigure(0, weight=1)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = max(0, (root.winfo_screenwidth() - width) // 2)
    y = max(0, (root.winfo_screenheight() - height) // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.mainloop()

    if selection["mode"] is None:
        return None
    return selection["mode"], selection["difficulty"] or DEFAULT_DIFFICULTY


def _choose_mode_cli() -> tuple[str, str] | None:
    if not sys.stdin.isatty():
        return None

    print("请选择游玩方式：")
    print("1. 窗口游玩")
    print("2. 网页游玩")

    while True:
        answer = input("输入 1 或 2，留空取消：").strip()
        if answer == "":
            return None
        if answer == "1":
            mode = "desktop"
            break
        if answer == "2":
            mode = "web"
            break
        print("输入无效，请重新选择。")

    print("请选择难度：")
    print(f"1. {DIFFICULTY_LABELS['easy']}  平台更密、危险板更少")
    print(f"2. {DIFFICULTY_LABELS['hard']}  平台更稀、危险板更多")
    while True:
        answer = input("输入 1 或 2，默认 1：").strip()
        if answer in ("", "1"):
            return mode, "easy"
        if answer == "2":
            return mode, "hard"
        print("输入无效，请重新选择。")
