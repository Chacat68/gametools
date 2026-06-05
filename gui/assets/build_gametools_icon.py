#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用标准库生成 gametools 默认 .ico（多尺寸 PNG 嵌入），无第三方依赖。

运行方式（在 gui/assets 目录下）::

    python build_gametools_icon.py

或在仓库根目录::

    python gui/assets/build_gametools_icon.py
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


def _crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", _crc32(chunk_type + data))
    )


def rgba_png(width: int, height: int, pixel) -> bytes:
    """pixel: callable (x, y) -> (r, g, b, a) 每个通道 0..255。"""
    raw_rows = []
    for y in range(height):
        row = bytearray([0])  # filter: None
        for x in range(width):
            r, g, b, a = pixel(x, y)
            row.extend((r, g, b, a))
        raw_rows.append(bytes(row))
    zlib_payload = zlib.compress(b"".join(raw_rows), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib_payload)
        + _png_chunk(b"IEND", b"")
    )


def _sheet_icon_pixel(x: int, y: int, w: int, h: int):
    """策划表 / 工具感：深蓝底 + 金色「表块」+ 深边框。"""
    border = max(1, min(w, h) // 16)
    if x < border or y < border or x >= w - border or y >= h - border:
        return (30, 64, 154, 255)
    x0, x1 = w * 28 // 100, w * 72 // 100
    y0, y1 = h * 30 // 100, h * 70 // 100
    if x0 <= x < x1 and y0 <= y < y1:
        return (255, 210, 72, 255)
    return (45, 108, 223, 255)


def _png_for_size(size: int) -> bytes:
    w = h = size

    def px(x, y):
        return _sheet_icon_pixel(x, y, w, h)

    return rgba_png(w, h, px)


def build_ico_bytes() -> bytes:
    sizes = (16, 32, 48, 256)
    images: list[tuple[int, int, bytes]] = []
    for s in sizes:
        png = _png_for_size(s)
        images.append((s, s, png))

    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries: list[bytes] = []
    payload = bytearray()
    for w, h, png in images:
        wb = 0 if w >= 256 else w
        hb = 0 if h >= 256 else h
        entries.append(
            struct.pack("<BBBBHHII", wb, hb, 0, 0, 1, 32, len(png), offset)
        )
        offset += len(png)
        payload.extend(png)
    return header + b"".join(entries) + bytes(payload)


def main() -> None:
    out = Path(__file__).resolve().parent / "gametools.ico"
    out.write_bytes(build_ico_bytes())
    print(f"已写入: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
