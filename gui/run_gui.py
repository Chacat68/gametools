#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的GUI启动脚本
用于直接运行图形界面，无需打包
"""

import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入并运行GUI
from json_format_detector_gui import main

if __name__ == "__main__":
    main()
