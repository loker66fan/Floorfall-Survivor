from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
WEB_DIR = PROJECT_ROOT / "web"
DIST_DIR = WEB_DIR / "dist"


def run() -> None:
    if not WEB_DIR.exists():
        raise FileNotFoundError(f"未找到 web 目录：{WEB_DIR}")

    with tempfile.TemporaryDirectory(prefix="down100-web-build-", dir="/tmp") as temp_dir:
        temp_path = Path(temp_dir)
        temp_web_dir = temp_path / "web"
        shutil.copytree(WEB_DIR, temp_web_dir, ignore=shutil.ignore_patterns("dist", "node_modules"))

        subprocess.run(["npm", "install"], cwd=temp_web_dir, check=True)
        subprocess.run(["npm", "run", "build"], cwd=temp_web_dir, check=True)

        built_dist = temp_web_dir / "dist"
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        shutil.copytree(built_dist, DIST_DIR)

    print(f"网页资源构建完成：{DIST_DIR}")


if __name__ == "__main__":
    run()
