#!/usr/bin/env python3
"""
Stable chunked paste helper for Zhihu editor via agent-browser.

Usage:
  python3 zhihu_paste_chunks.py \
    --file ~/clawd/publish-content.txt \
    --editor-ref @e28 \
    --cdp 9222 \
    --session zhihu-cdp \
    --chunk-size 500 \
    --wait-ms 800
"""

from __future__ import annotations

import argparse
import platform
import re
import subprocess
import sys
import time
from pathlib import Path


def run(
    cmd: list[str],
    *,
    input_bytes: bytes | None = None,
    timeout_sec: int = 20,
    show_stdout: bool = False,
) -> None:
    try:
        proc = subprocess.run(
            cmd,
            input=input_bytes,
            timeout=timeout_sec,
            check=True,
            capture_output=True,
        )
        if show_stdout and proc.stdout:
            out = proc.stdout.decode("utf-8", errors="ignore").strip()
            if out:
                print(out)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Command timeout after {timeout_sec}s: {' '.join(cmd)}"
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or b"").decode("utf-8", errors="ignore").strip()
        stdout = (exc.stdout or b"").decode("utf-8", errors="ignore").strip()
        detail = stderr or stdout or f"exit code {exc.returncode}"
        raise RuntimeError(f"Command failed: {' '.join(cmd)} | {detail}") from exc


def cdp_health_url(cdp: str) -> str:
    cdp = str(cdp).strip()
    if cdp.startswith("http://") or cdp.startswith("https://"):
        base = cdp.rstrip("/")
        if base.endswith("/json/version"):
            return base
        return f"{base}/json/version"
    return f"http://127.0.0.1:{cdp}/json/version"


def ensure_cdp_alive(cdp: str, timeout_sec: int) -> None:
    run(
        ["curl", "-sf", cdp_health_url(cdp)],
        timeout_sec=max(4, min(timeout_sec, 15)),
    )


def select_clipboard_backend() -> list[str]:
    if platform.system() == "Darwin":
        return ["pbcopy"]
    if platform.system() == "Linux":
        # Prefer Wayland clipboard first, then X11.
        if subprocess.run(["which", "wl-copy"], capture_output=True).returncode == 0:
            return ["wl-copy"]
        if subprocess.run(["which", "xclip"], capture_output=True).returncode == 0:
            return ["xclip", "-selection", "clipboard"]
    raise RuntimeError(
        "No supported clipboard backend found. Install pbcopy (macOS), wl-copy or xclip (Linux)."
    )


def paste_hotkey() -> str:
    return "Meta+v" if platform.system() == "Darwin" else "Control+v"


def move_to_end_hotkey() -> str:
    # Keep paste order stable in long contenteditable editors.
    # macOS: Cmd+ArrowDown jumps to document end.
    # Linux/Windows: Ctrl+End jumps to document end.
    return "Meta+ArrowDown" if platform.system() == "Darwin" else "Control+End"


def chunk_text(text: str, chunk_size: int) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def normalize_for_zhihu(text: str) -> tuple[str, int]:
    """
    Normalize markdown-heavy text into stable plain paragraphs for Zhihu editor.
    Returns (normalized_text, removed_hr_lines_count).
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove common invisible chars that can cause odd spacing behavior.
    text = text.replace("\ufeff", "").replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    text = text.replace("\u00a0", " ")

    removed_hr = 0
    out_lines: list[str] = []
    for raw in text.split("\n"):
        line = raw.rstrip()
        stripped = line.strip()
        # Remove standalone horizontal-rule lines (---, ***, ___, em-dash variants).
        if stripped and (
            re.fullmatch(r"[-_*]{3,}", stripped) is not None
            or re.fullmatch(r"[—–-]{3,}", stripped) is not None
        ):
            removed_hr += 1
            continue
        out_lines.append(line)

    text = "\n".join(out_lines)
    # Normalize excessive vertical whitespace to one blank line between paragraphs.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(), removed_hr


def main() -> int:
    parser = argparse.ArgumentParser(description="Chunked paste for Zhihu editor")
    parser.add_argument("--file", required=True, help="Path to article text file")
    parser.add_argument("--editor-ref", required=True, help="Current body editor ref, e.g. @e28")
    parser.add_argument("--cdp", default="9222", help="CDP port or URL (default: 9222)")
    parser.add_argument(
        "--session",
        default="zhihu-cdp",
        help="agent-browser session name (default: zhihu-cdp)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Characters per chunk (default: 500)",
    )
    parser.add_argument(
        "--focus-wait-ms",
        type=int,
        default=200,
        help="Wait after clicking editor before paste (default: 200ms)",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=800,
        help="Wait between paste chunks (default: 800ms)",
    )
    parser.add_argument(
        "--cmd-timeout-sec",
        type=int,
        default=20,
        help="Timeout for each subprocess command (default: 20s)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=1,
        help="Retries per chunk on transient failures (default: 1)",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable pre-paste normalization (keep raw file text as-is)",
    )
    args = parser.parse_args()

    file_path = Path(args.file).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"Content file not found: {file_path}")
    if args.chunk_size <= 0:
        raise ValueError("--chunk-size must be > 0")
    if args.cmd_timeout_sec <= 0:
        raise ValueError("--cmd-timeout-sec must be > 0")
    if args.retries < 0:
        raise ValueError("--retries must be >= 0")
    if args.wait_ms < 0 or args.focus_wait_ms < 0:
        raise ValueError("--wait-ms and --focus-wait-ms must be >= 0")

    text = file_path.read_text(encoding="utf-8")
    removed_hr = 0
    if not args.no_normalize:
        text, removed_hr = normalize_for_zhihu(text)

    chunks = chunk_text(text, args.chunk_size)
    if not chunks:
        print("No content to paste.")
        return 0

    clip_cmd = select_clipboard_backend()
    hotkey = paste_hotkey()
    end_hotkey = move_to_end_hotkey()
    ensure_cdp_alive(args.cdp, args.cmd_timeout_sec)
    print(f"Clipboard backend: {' '.join(clip_cmd)}")
    if not args.no_normalize:
        print(f"Normalization: enabled (removed_hr_lines={removed_hr})")
    else:
        print("Normalization: disabled")
    print(f"Chunks: {len(chunks)}, chars: {len(text)}")

    for idx, chunk in enumerate(chunks, start=1):
        ok = False
        for attempt in range(0, args.retries + 1):
            try:
                ensure_cdp_alive(args.cdp, args.cmd_timeout_sec)
                run(
                    clip_cmd,
                    input_bytes=chunk.encode("utf-8"),
                    timeout_sec=args.cmd_timeout_sec,
                )
                time.sleep(0.15)

                run(
                    [
                        "agent-browser",
                        "click",
                        args.editor_ref,
                        "--cdp",
                        str(args.cdp),
                        "--session",
                        args.session,
                    ],
                    timeout_sec=args.cmd_timeout_sec,
                )
                run(
                    [
                        "agent-browser",
                        "wait",
                        str(args.focus_wait_ms),
                        "--cdp",
                        str(args.cdp),
                        "--session",
                        args.session,
                    ],
                    timeout_sec=max(args.cmd_timeout_sec, args.focus_wait_ms // 1000 + 6),
                )
                run(
                    [
                        "agent-browser",
                        "press",
                        end_hotkey,
                        "--cdp",
                        str(args.cdp),
                        "--session",
                        args.session,
                    ],
                    timeout_sec=args.cmd_timeout_sec,
                )
                run(
                    [
                        "agent-browser",
                        "wait",
                        "120",
                        "--cdp",
                        str(args.cdp),
                        "--session",
                        args.session,
                    ],
                    timeout_sec=max(args.cmd_timeout_sec, 7),
                )
                run(
                    [
                        "agent-browser",
                        "press",
                        hotkey,
                        "--cdp",
                        str(args.cdp),
                        "--session",
                        args.session,
                    ],
                    timeout_sec=args.cmd_timeout_sec,
                )
                run(
                    [
                        "agent-browser",
                        "wait",
                        str(args.wait_ms),
                        "--cdp",
                        str(args.cdp),
                        "--session",
                        args.session,
                    ],
                    timeout_sec=max(args.cmd_timeout_sec, args.wait_ms // 1000 + 6),
                )
                ensure_cdp_alive(args.cdp, args.cmd_timeout_sec)
                ok = True
                break
            except Exception as exc:
                if attempt < args.retries:
                    print(
                        f"[{idx}/{len(chunks)}] retry {attempt + 1}/{args.retries}: {exc}",
                        file=sys.stderr,
                    )
                    time.sleep(0.6)
                    continue
                raise RuntimeError(f"Chunk {idx}/{len(chunks)} failed: {exc}") from exc

        if not ok:
            raise RuntimeError(f"Chunk {idx}/{len(chunks)} failed unexpectedly")

        done = min(idx * args.chunk_size, len(text))
        print(f"[{idx}/{len(chunks)}] pasted ({done}/{len(text)} chars)")

    print("Paste complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
