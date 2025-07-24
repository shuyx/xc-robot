#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI依赖注入模块
JWT认证中间件和用户权限依赖
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .auth import jwt_manager
from ..models.user import User

# OAuth2令牌URL
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/token",
    auto_error=False  # 允许可选认证
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户（必需认证）"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return jwt_manager.get_current_user(db, token)


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选认证）"""
    if not token:
        return None
    
    try:
        return jwt_manager.get_current_user(db, token)
    except HTTPException:
        return None


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """需要管理员权限的依赖"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def check_device_permission(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """检查设备操作权限"""
    allowed_roles = ["admin", "operator", "user"]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无设备操作权限"
        )
    return current_user