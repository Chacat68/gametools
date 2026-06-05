# GUI 资源目录

## `gametools.ico`

- 用作 **PyInstaller 打包 exe 的应用图标**，以及运行时 **tkinter 窗口图标**（与 `build_unified.py` 中 `datas` / `icon=` 及 `gametools_unified._apply_window_icon` 中的路径一致）。
- 若需调整视觉，可修改 `build_gametools_icon.py` 后在本目录执行：

```bash
python build_gametools_icon.py
```

重新生成 `gametools.ico` 后再执行打包脚本。
