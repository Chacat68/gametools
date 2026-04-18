# -*- coding: utf-8 -*-
"""统一的轻量级 Tkinter 主题配置。"""

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


def apply_ui_theme(root):
    """应用统一主题并返回配色和样式对象。"""
    style = ttk.Style(root)

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
        font=('Bahnschrift', 11, 'bold'),
    )

    style.configure('TLabel', background=UI_PALETTE['surface'], foreground=UI_PALETTE['text'])
    style.configure('Title.TLabel', font=('Bahnschrift', 18, 'bold'))
    style.configure('Heading.TLabel', font=('Bahnschrift', 11, 'bold'))
    style.configure('Info.TLabel', font=('Microsoft YaHei UI', 9), foreground=UI_PALETTE['muted_text'])
    style.configure(
        'AccentInfo.TLabel',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['info'],
        font=('Bahnschrift', 9, 'bold'),
    )
    style.configure('Success.TLabel', font=('Microsoft YaHei UI', 9), foreground=UI_PALETTE['success'])
    style.configure('Error.TLabel', font=('Microsoft YaHei UI', 9), foreground=UI_PALETTE['error'])
    style.configure(
        'HeaderTitle.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['text'],
        font=('Bahnschrift', 24, 'bold'),
    )
    style.configure(
        'HeaderMeta.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['accent'],
        font=('Bahnschrift', 10, 'bold'),
    )
    style.configure(
        'HeaderTag.TLabel',
        background=UI_PALETTE['accent'],
        foreground=UI_PALETTE['accent_text'],
        font=('Bahnschrift', 10, 'bold'),
        padding=(10, 4),
    )
    style.configure(
        'Badge.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['accent'],
        font=('Bahnschrift', 9, 'bold'),
    )
    style.configure(
        'SidebarTitle.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_text'],
        font=('Bahnschrift', 18, 'bold'),
    )
    style.configure(
        'SidebarMeta.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_muted'],
        font=('Bahnschrift', 9, 'bold'),
    )
    style.configure(
        'SidebarFoot.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_muted'],
        font=('Microsoft YaHei UI', 9),
    )
    style.configure(
        'Status.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['muted_text'],
        padding=(10, 7),
        font=('Microsoft YaHei UI', 9),
    )

    style.configure(
        'TButton',
        font=('Microsoft YaHei UI', 9),
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
        font=('Microsoft YaHei UI', 9, 'bold'),
        background=UI_PALETTE['accent'],
        foreground=UI_PALETTE['accent_text'],
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
        font=('Microsoft YaHei UI', 9),
    )
    style.configure(
        'TRadiobutton',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['text'],
        font=('Microsoft YaHei UI', 9),
    )

    style.configure(
        'Navigation.TNotebook',
        background=UI_PALETTE['app_bg'],
        borderwidth=0,
        tabmargins=0,
    )
    style.layout('Navigation.TNotebook.Tab', [])

    return UI_PALETTE, style