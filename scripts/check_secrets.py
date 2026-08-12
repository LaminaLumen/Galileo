"""扫描 Git 将纳管的文件，并在发现疑似秘密时返回失败。"""

from __future__ import annotations

import json
import subprocess
import sys


def _repository_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def _scanner_command() -> list[str]:
    """通过当前解释器启动扫描器，兼容 venv、Conda 与各平台脚本目录。"""

    return [sys.executable, "-m", "detect_secrets"]


def main() -> int:
    files = _repository_files()
    if not files:
        print("没有需要扫描的 Git 文件。")
        return 0

    result = subprocess.run(
        [*_scanner_command(), "scan", *files],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    report = json.loads(result.stdout)
    findings = report.get("results", {})
    if findings:
        print("发现疑似秘密，请人工核查；真实秘密必须轮换并从仓库移除：")
        for filename, items in findings.items():
            lines = ", ".join(str(item.get("line_number", "?")) for item in items)
            print(f"- {filename}: 行 {lines}")
        return 1

    print(f"秘密扫描通过：已检查 {len(files)} 个 Git 文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
