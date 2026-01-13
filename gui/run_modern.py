#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameTools 现代化界面启动脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 启动现代化界面
from gui.gametools_modern import main

if __name__ == "__main__":
    main()
