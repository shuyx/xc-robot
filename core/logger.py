#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 核心日志模块
提供统一的日志配置和管理
"""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(settings) -> None:
    """设置日志配置"""
    
    # 创建日志目录
    settings.logs_dir.mkdir(exist_ok=True)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式器
    formatter = logging.Formatter(settings.log_format)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(
        settings.logs_dir / "xc_robot_api.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 设置特定模块的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("websockets").setLevel(logging.WARNING)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志器实例"""
    return logging.getLogger(name)