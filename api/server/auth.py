#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT认证核心模块
基于python-jose和passlib的生产级JWT实现
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from ..models.user import User

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 令牌黑名单（生产环境建议使用Redis）
token_blacklist = set()


class JWTManager:
    """JWT令牌管理器"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """验证令牌"""
        try:
            # 检查令牌是否在黑名单中
            if token in token_blacklist:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌已被撤销",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 解码令牌
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # 验证令牌类型
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌类型错误",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 验证用户名是否存在
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌载荷",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法验证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def revoke_token(token: str):
        """撤销令牌（添加到黑名单）"""
        token_blacklist.add(token)
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """验证用户身份"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not JWTManager.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """从令牌获取当前用户"""
        payload = JWTManager.verify_token(token, "access")
        username: str = payload.get("sub")
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user


# JWT管理器实例
jwt_manager = JWTManager()


def create_default_admin_user(db: Session):
    """创建默认管理员用户"""
    # 检查是否已存在admin用户
    admin_user = db.query(User).filter(User.username == "admin").first()
    if admin_user:
        return admin_user
    
    # 创建默认admin用户
    admin_user = User(
        username="admin",
        email="admin@xc-robot.com",
        password_hash=jwt_manager.get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return admin_user