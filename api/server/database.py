#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理模块
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
import sqlite3

from .config import get_settings

# 创建数据库基类
Base = declarative_base()

# 全局变量
engine = None
SessionLocal = None


def init_database():
    """初始化数据库连接"""
    global engine, SessionLocal
    
    settings = get_settings()
    
    # 创建数据库引擎
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    
    # 为SQLite启用外键支持
    if "sqlite" in settings.database_url:
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if isinstance(dbapi_connection, sqlite3.Connection):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
    
    # 创建会话工厂
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine


def get_db() -> Session:
    """获取数据库会话"""
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有数据表"""
    if engine is None:
        init_database()
    
    # 导入所有模型以确保它们被注册到Base中
    from ..models import User, Device, Task, Log
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """删除所有数据表（仅用于开发和测试）"""
    if engine is None:
        init_database()
    
    Base.metadata.drop_all(bind=engine)


def check_database_connection() -> bool:
    """检查数据库连接是否正常"""
    try:
        if engine is None:
            init_database()
        
        # 测试连接
        with engine.connect() as connection:
            from sqlalchemy import text
            connection.execute(text("SELECT 1"))
        
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def get_database_info():
    """获取数据库信息"""
    settings = get_settings()
    info = {
        "database_url": settings.database_url,
        "database_echo": settings.database_echo,
        "engine_info": None,
        "tables": []
    }
    
    if engine is not None:
        info["engine_info"] = {
            "name": engine.name,
            "driver": engine.driver,
            "url": str(engine.url).replace(engine.url.password or "", "***") if engine.url.password else str(engine.url)
        }
        
        # 获取表信息
        try:
            with engine.connect() as connection:
                from sqlalchemy import inspect
                inspector = inspect(connection)
                info["tables"] = inspector.get_table_names()
        except Exception as e:
            info["tables"] = [f"Error getting tables: {e}"]
    
    return info