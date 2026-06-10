# -*- coding: utf-8 -*-
"""统一的轻量级 Tkinter 主题配置。"""

import tkinter as tk
from tkinter import ttk


UI_PALETTE = {
    'app_bg': '#f5efe7',
    'surface': '#fffaf4',
    'surface_alt': '#e4ede8',
    'sidebar_bg': '#20343b',
    'sidebar_active': '#2d4952',
    'sidebar_hover': '#3a5963',
    'sidebar_text': '#f7f4ee',
    'sidebar_muted': '#b7c5bf',
    'accent': '#c86c40',
    'accent_active': '#ab582f',
    'accent_text': '#fff9f4',
    'text': '#1f2422',
    'muted_text': '#64706c',
    'border': '#d4ddd7',
    'success': '#3f7b5d',
    'error': '#b44f3f',
    'warning': '#a97b2b',
    'info': '#2c7088',
    'button_hover': '#d7e2dd',
    'button_pressed': '#cad8d1',
    'input_bg': '#fffdfa',
}


def _clamp_font_size(font_size):
    """约束字号，避免 UI 在不同机器上失控。"""
    try:
        value = int(font_size)
    except (TypeError, ValueError):
        value = 10
    return max(9, min(value, 14))


def _checkbutton_layout_with_indicator(indicator_element):
    """构建带自定义 indicator 的 Checkbutton 布局。"""
    return [
        (
            'Checkbutton.padding',
            {
                'sticky': 'nswe',
                'children': [
                    (indicator_element, {'side': 'left', 'sticky': ''}),
                    (
                        'Checkbutton.focus',
                        {
                            'side': 'left',
                            'sticky': 'w',
                            'children': [('Checkbutton.label', {'sticky': 'nswe'})],
                        },
                    ),
                ],
            },
        ),
    ]


def _line_pixels(x0, y0, x1, y1, thickness=2):
    """Bresenham 直线像素集合，用于绘制勾选标记。"""
    points = set()
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0

    while True:
        for offset_x in range(-(thickness // 2), thickness // 2 + 1):
            for offset_y in range(-(thickness // 2), thickness // 2 + 1):
                points.add((x + offset_x, y + offset_y))
        if x == x1 and y == y1:
            break
        err2 = err * 2
        if err2 > -dy:
            err -= dy
            x += sx
        if err2 < dx:
            err += dx
            y += sy

    return points


def _create_checkbutton_images(root, size=16):
    """用 PhotoImage 绘制方框勾选指示器（无第三方依赖）。"""
    bg = UI_PALETTE['input_bg']
    border = UI_PALETTE['border']
    check = UI_PALETTE['success']
    check_pixels = _line_pixels(3, 8, 6, 11, thickness=2) | _line_pixels(6, 11, 12, 5, thickness=2)

    def make_image(checked):
        img = tk.PhotoImage(width=size, height=size, master=root)
        for y in range(size):
            for x in range(size):
                on_border = x == 0 or y == 0 or x == size - 1 or y == size - 1
                if checked and (x, y) in check_pixels:
                    color = check
                elif on_border:
                    color = border
                else:
                    color = bg
                img.put(color, (x, y))
        return img

    return {
        'unchecked': make_image(False),
        'checked': make_image(True),
    }


def _install_checkbutton_checkmark(style, root):
    """将 clam 主题下选中时显示的 X 改为勾。"""
    layout = _checkbutton_layout_with_indicator('Gametools.indicator')

    for source_theme in ('vista', 'xpnative', 'default', 'alt'):
        if source_theme not in style.theme_names():
            continue
        try:
            style.element_create(
                'Gametools.indicator',
                'from',
                source_theme,
                'Checkbutton.indicator',
            )
            style.layout('TCheckbutton', layout)
            return
        except tk.TclError:
            continue

    images = _create_checkbutton_images(root)
    root._gametools_checkbox_images = images
    style.element_create(
        'Gametools.indicator',
        'image',
        images['unchecked'],
        ('selected', images['checked']),
    )
    style.layout('TCheckbutton', layout)


def apply_ui_theme(root, font_size=10):
    """应用统一主题并返回配色和样式对象。"""
    style = ttk.Style(root)
    font_size = _clamp_font_size(font_size)
    body_font_size = max(font_size - 1, 8)
    section_font_size = font_size + 1
    title_font_size = font_size + 8
    hero_font_size = font_size + 14

    root.option_add('*Font', f'{{Microsoft YaHei UI}} {body_font_size}')

    for theme_name in ('clam', 'vista', 'default'):
        if theme_name in style.theme_names():
            style.theme_use(theme_name)
            break

    root.configure(bg=UI_PALETTE['app_bg'])

    style.configure('TFrame', background=UI_PALETTE['surface'])
    style.configure('App.TFrame', background=UI_PALETTE['app_bg'])
    style.configure('Page.TFrame', background=UI_PALETTE['surface'])

    style.configure(
        'TLabelframe',
        background=UI_PALETTE['surface'],
        bordercolor=UI_PALETTE['border'],
        borderwidth=1,
        relief='solid',
        lightcolor=UI_PALETTE['border'],
        darkcolor=UI_PALETTE['border'],
    )
    style.configure(
        'TLabelframe.Label',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['text'],
        font=('Bahnschrift', section_font_size, 'bold'),
    )

    style.configure('TLabel', background=UI_PALETTE['surface'], foreground=UI_PALETTE['text'])
    style.configure('Title.TLabel', font=('Bahnschrift', title_font_size, 'bold'))
    style.configure('Heading.TLabel', font=('Bahnschrift', section_font_size, 'bold'))
    style.configure('Info.TLabel', font=('Microsoft YaHei UI', body_font_size), foreground=UI_PALETTE['muted_text'])
    style.configure(
        'AccentInfo.TLabel',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['info'],
        font=('Bahnschrift', body_font_size, 'bold'),
    )
    style.configure('Success.TLabel', font=('Microsoft YaHei UI', body_font_size), foreground=UI_PALETTE['success'])
    style.configure('Error.TLabel', font=('Microsoft YaHei UI', body_font_size), foreground=UI_PALETTE['error'])
    style.configure(
        'HeaderTitle.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['text'],
        font=('Bahnschrift', hero_font_size, 'bold'),
    )
    style.configure(
        'HeaderMeta.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['accent'],
        font=('Bahnschrift', font_size, 'bold'),
    )
    style.configure(
        'HeaderTag.TLabel',
        background=UI_PALETTE['accent'],
        foreground=UI_PALETTE['accent_text'],
        font=('Bahnschrift', font_size, 'bold'),
        padding=(10, 4),
    )
    style.configure(
        'Badge.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['accent'],
        font=('Bahnschrift', body_font_size, 'bold'),
    )
    style.configure(
        'SidebarTitle.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_text'],
        font=('Bahnschrift', title_font_size, 'bold'),
    )
    style.configure(
        'SidebarMeta.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_muted'],
        font=('Bahnschrift', body_font_size, 'bold'),
    )
    style.configure(
        'SidebarFoot.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_muted'],
        font=('Microsoft YaHei UI', body_font_size),
    )
    style.configure(
        'Status.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['muted_text'],
        padding=(10, 7),
        font=('Microsoft YaHei UI', body_font_size),
    )

    style.configure(
        'TButton',
        font=('Microsoft YaHei UI', body_font_size),
        padding=(14, 8),
        borderwidth=0,
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['text'],
        focusthickness=0,
    )
    style.map(
        'TButton',
        background=[('active', UI_PALETTE['button_hover']), ('pressed', UI_PALETTE['button_pressed'])],
    )
    style.configure(
        'Accent.TButton',
        font=('Microsoft YaHei UI', body_font_size, 'bold'),
        background=UI_PALETTE['accent'],
        foreground=UI_PALETTE['accent_text'],
        padding=(14, 9),
        focusthickness=0,
    )
    style.map(
        'Accent.TButton',
        background=[('active', UI_PALETTE['accent_active']), ('pressed', UI_PALETTE['accent_active'])],
        foreground=[('disabled', '#dbe7e4')],
    )

    style.configure(
        'Subtle.TButton',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['text'],
        padding=(12, 7),
    )
    style.map(
        'Subtle.TButton',
        background=[('active', UI_PALETTE['button_hover']), ('pressed', UI_PALETTE['button_pressed'])],
    )

    style.configure(
        'Quiet.TButton',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['muted_text'],
        padding=(10, 7),
    )
    style.map(
        'Quiet.TButton',
        background=[('active', UI_PALETTE['surface_alt']), ('pressed', UI_PALETTE['button_pressed'])],
        foreground=[('active', UI_PALETTE['text'])],
    )

    style.configure(
        'Danger.TButton',
        background='#f2dfd8',
        foreground=UI_PALETTE['error'],
        padding=(12, 7),
    )
    style.map(
        'Danger.TButton',
        background=[('active', '#e8c7bb'), ('pressed', '#ddb3a4')],
        foreground=[('active', UI_PALETTE['error'])],
    )

    style.configure(
        'TEntry',
        fieldbackground=UI_PALETTE['input_bg'],
        foreground=UI_PALETTE['text'],
        bordercolor=UI_PALETTE['border'],
        lightcolor=UI_PALETTE['border'],
        darkcolor=UI_PALETTE['border'],
        padding=8,
    )
    style.configure(
        'TCombobox',
        fieldbackground=UI_PALETTE['input_bg'],
        foreground=UI_PALETTE['text'],
        bordercolor=UI_PALETTE['border'],
        arrowsize=14,
        padding=7,
    )
    style.configure(
        'TCheckbutton',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['text'],
        font=('Microsoft YaHei UI', body_font_size),
    )
    _install_checkbutton_checkmark(style, root)
    style.configure(
        'TRadiobutton',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['text'],
        font=('Microsoft YaHei UI', body_font_size),
    )

    style.configure(
        'Navigation.TNotebook',
        background=UI_PALETTE['app_bg'],
        borderwidth=0,
        tabmargins=0,
    )
    style.layout('Navigation.TNotebook.Tab', [])

    return UI_PALETTE, style