#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, JSON, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# 创建基类
Base = declarative_base()

# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# 设备模型
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    device_type = Column(String(50), nullable=False)
    ip_address = Column(String(45))
    port = Column(Integer)
    status = Column(String(20), default="offline", nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    config = Column(JSON, default=dict)
    last_heartbeat = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# 任务模型
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    task_type = Column(String(50), nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="pending", nullable=False, index=True)
    config = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error_message = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

# 日志模型
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(50), index=True)
    function = Column(String(100))
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True, index=True)
    log_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

def init_database():
    """初始化数据库"""
    # 创建数据库引擎
    engine = create_engine(
        "sqlite:///./xc_recon.db",
        echo=True,
        connect_args={"check_same_thread": False}
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 插入初始数据
    session = SessionLocal()
    try:
        # 检查是否已有数据
        if session.query(User).count() == 0:
            # 创建默认管理员用户
            admin_user = User(
                username="admin",
                email="admin@xc-recon.com",
                password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
                role="admin"
            )
            session.add(admin_user)
            
            # 创建默认设备
            devices = [
                Device(
                    name="FR3右臂",
                    device_type="robotic_arm",
                    ip_address="192.168.58.2",
                    port=20003,
                    config={"description": "Franka Emika FR3 右臂机械臂"}
                ),
                Device(
                    name="FR3左臂",
                    device_type="robotic_arm", 
                    ip_address="192.168.58.3",
                    port=20003,
                    config={"description": "Franka Emika FR3 左臂机械臂"}
                ),
                Device(
                    name="Hermes底盘",
                    device_type="mobile_base",
                    ip_address="192.168.31.211",
                    port=1448,
                    config={"description": "Hermes移动底盘"}
                )
            ]
            
            for device in devices:
                session.add(device)
            
            session.commit()
            print("✅ 初始数据插入完成")
        else:
            print("✅ 数据库已存在数据，跳过初始化")
            
    except Exception as e:
        session.rollback()
        print(f"❌ 初始化数据失败: {e}")
    finally:
        session.close()
    
    print("✅ 数据库初始化完成")

if __name__ == "__main__":
    init_database()