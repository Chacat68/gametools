# -*- coding: utf-8 -*-
"""统一的轻量级 Tkinter 主题配置。"""

from tkinter import ttk


UI_PALETTE = {
    'app_bg': '#eef3f1',
    'surface': '#f8fbfa',
    'surface_alt': '#edf4f2',
    'sidebar_bg': '#173a3a',
    'sidebar_active': '#245151',
    'sidebar_hover': '#1d4747',
    'sidebar_text': '#f3fbf9',
    'sidebar_muted': '#b9d1cd',
    'accent': '#2f8f83',
    'accent_active': '#256f66',
    'accent_text': '#ffffff',
    'text': '#1f2a2a',
    'muted_text': '#5d7070',
    'border': '#d6e2df',
    'success': '#2d7d46',
    'error': '#b44343',
    'warning': '#9a6a1f',
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
        relief='solid',
        lightcolor=UI_PALETTE['border'],
        darkcolor=UI_PALETTE['border'],
    )
    style.configure(
        'TLabelframe.Label',
        background=UI_PALETTE['surface'],
        foreground=UI_PALETTE['text'],
        font=('Microsoft YaHei UI', 10, 'bold'),
    )

    style.configure('TLabel', background=UI_PALETTE['surface'], foreground=UI_PALETTE['text'])
    style.configure('Title.TLabel', font=('Microsoft YaHei UI', 15, 'bold'))
    style.configure('Heading.TLabel', font=('Microsoft YaHei UI', 11, 'bold'))
    style.configure('Info.TLabel', font=('Microsoft YaHei UI', 9), foreground=UI_PALETTE['muted_text'])
    style.configure('Success.TLabel', font=('Microsoft YaHei UI', 9), foreground=UI_PALETTE['success'])
    style.configure('Error.TLabel', font=('Microsoft YaHei UI', 9), foreground=UI_PALETTE['error'])
    style.configure(
        'HeaderTitle.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['text'],
        font=('Microsoft YaHei UI', 18, 'bold'),
    )
    style.configure(
        'HeaderSubtitle.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['muted_text'],
        font=('Microsoft YaHei UI', 10),
    )
    style.configure(
        'Badge.TLabel',
        background=UI_PALETTE['surface_alt'],
        foreground=UI_PALETTE['accent'],
        font=('Segoe UI', 9, 'bold'),
    )
    style.configure(
        'SidebarTitle.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_text'],
        font=('Microsoft YaHei UI', 16, 'bold'),
    )
    style.configure(
        'SidebarMeta.TLabel',
        background=UI_PALETTE['sidebar_bg'],
        foreground=UI_PALETTE['sidebar_muted'],
        font=('Microsoft YaHei UI', 9),
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
        padding=(12, 7),
        borderwidth=0,
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
    )
    style.map(
        'Subtle.TButton',
        background=[('active', '#dce9e5'), ('pressed', '#dce9e5')],
    )

    style.configure(
        'TEntry',
        fieldbackground='#ffffff',
        foreground=UI_PALETTE['text'],
        bordercolor=UI_PALETTE['border'],
        lightcolor=UI_PALETTE['border'],
        darkcolor=UI_PALETTE['border'],
        padding=6,
    )
    style.configure(
        'TCombobox',
        fieldbackground='#ffffff',
        foreground=UI_PALETTE['text'],
        bordercolor=UI_PALETTE['border'],
        arrowsize=14,
        padding=5,
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