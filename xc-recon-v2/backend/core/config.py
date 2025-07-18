#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseSettings, Field
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    app_name: str = "XC-RECON-SYSTEM"
    app_version: str = "2.0.0"
    debug: bool = True
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API配置
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # 数据库配置
    database_url: str = "sqlite:///./xc_recon.db"
    database_echo: bool = False
    
    # 安全配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis配置
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = False
    
    # AI配置
    openai_api_key: Optional[str] = None
    ai_enabled: bool = False
    
    # 文件存储配置
    upload_path: str = "./data/uploads"
    max_file_size: str = "100MB"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._find_config_file()
        self.config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _find_config_file(self) -> str:
        """查找配置文件"""
        # 查找配置文件的可能位置
        possible_paths = [
            Path(__file__).parent.parent.parent / "config" / "app.yml",
            Path(__file__).parent.parent / "config" / "app.yml",
            Path("config/app.yml"),
            Path("app.yml")
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        # 如果找不到配置文件，创建默认配置
        default_config = Path(__file__).parent.parent.parent / "config" / "app.yml"
        if not default_config.exists():
            default_config.parent.mkdir(parents=True, exist_ok=True)
            self._create_default_config(default_config)
        
        return str(default_config)
    
    def _create_default_config(self, config_path: Path):
        """创建默认配置文件"""
        default_config = {
            "app": {
                "name": "XC-RECON-SYSTEM",
                "version": "2.0.0",
                "debug": True,
                "log_level": "INFO",
                "host": "0.0.0.0",
                "port": 8000
            },
            "database": {
                "url": "sqlite:///./xc_recon.db",
                "echo": False
            },
            "security": {
                "secret_key": "your-secret-key-here-change-in-production",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"警告：无法加载配置文件 {self.config_file}: {e}")
            self.config_data = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的键"""
        keys = key.split(".")
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_settings(self) -> Settings:
        """获取Pydantic设置对象"""
        # 从配置文件中提取设置
        app_config = self.config_data.get("app", {})
        api_config = self.config_data.get("api", {})
        db_config = self.config_data.get("database", {})
        security_config = self.config_data.get("security", {})
        redis_config = self.config_data.get("redis", {})
        ai_config = self.config_data.get("ai", {})
        storage_config = self.config_data.get("storage", {})
        
        # 合并配置
        config_dict = {
            # App
            "app_name": app_config.get("name", "XC-RECON-SYSTEM"),
            "app_version": app_config.get("version", "2.0.0"),
            "debug": app_config.get("debug", True),
            "log_level": app_config.get("log_level", "INFO"),
            "host": app_config.get("host", "0.0.0.0"),
            "port": app_config.get("port", 8000),
            
            # API
            "cors_origins": api_config.get("cors_origins", ["http://localhost:3000"]),
            "docs_url": api_config.get("docs_url", "/docs"),
            "redoc_url": api_config.get("redoc_url", "/redoc"),
            "openapi_url": api_config.get("openapi_url", "/openapi.json"),
            
            # Database
            "database_url": db_config.get("url", "sqlite:///./xc_recon.db"),
            "database_echo": db_config.get("echo", False),
            
            # Security
            "secret_key": security_config.get("secret_key", "change-me"),
            "algorithm": security_config.get("algorithm", "HS256"),
            "access_token_expire_minutes": security_config.get("access_token_expire_minutes", 30),
            
            # Redis
            "redis_enabled": redis_config.get("enabled", False),
            
            # AI
            "ai_enabled": ai_config.get("openai", {}).get("enabled", False),
            
            # Storage
            "upload_path": storage_config.get("upload_path", "./data/uploads"),
            "max_file_size": storage_config.get("max_file_size", "100MB"),
        }
        
        return Settings(**config_dict)


# 全局配置管理器实例
_config_manager = None


@lru_cache()
def get_config_manager() -> ConfigManager:
    """获取配置管理器实例（单例）"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置（单例）"""
    return get_config_manager().get_settings()