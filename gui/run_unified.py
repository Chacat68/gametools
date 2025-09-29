#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools统一版本启动脚本
用于直接运行统一界面，无需打包
"""

import sys
import os
from pathlib import Path

# 确保在正确的目录中运行
if __name__ == "__main__":
    # 导入并运行统一界面
    from gui.gametools_unified import main
    
    print("启动gametools统一界面...")
    main()
