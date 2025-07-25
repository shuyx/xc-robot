#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 核心配置模块
用于API服务器的配置管理
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本信息
    app_name: str = "XC-ROBOT API"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API路径配置
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # CORS配置
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 机器人连接配置
    fr3_right_ip: str = "192.168.58.2"
    fr3_left_ip: str = "192.168.58.3" 
    hermes_ip: str = "192.168.0.100"
    
    # 文件路径配置
    data_dir: Path = Path("./data")
    logs_dir: Path = Path("./logs")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
_settings = None

def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings