#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关API端点
完整的JWT认证实现
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import jwt_manager, create_default_admin_user
from backend.core.dependencies import (
    get_current_user,
    get_current_active_user,
    oauth2_scheme
)
from backend.models.user import User

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录获取访问令牌"""
    try:
        # 确保默认admin用户存在
        create_default_admin_user(db)
        
        # 认证用户
        user = jwt_manager.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成JWT令牌
        access_token = jwt_manager.create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        refresh_token = jwt_manager.create_refresh_token(
            data={"sub": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30分钟
            "user_info": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "permissions": _get_user_permissions(current_user.role),
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    try:
        # 将令牌添加到黑名单
        jwt_manager.revoke_token(token)
        
        return {
            "status": "success",
            "message": f"用户 {current_user.username} 登出成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        refresh_token = refresh_token_data.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少刷新令牌"
            )
        
        # 验证刷新令牌
        payload = jwt_manager.verify_token(refresh_token, "refresh")
        username = payload.get("sub")
        
        # 获取用户
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # 生成新的访问令牌
        new_access_token = jwt_manager.create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"令牌刷新失败: {str(e)}"
        )


@router.post("/register")
async def register_user(
    user_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)  # 需要管理员权限
):
    """注册新用户（仅管理员）"""
    try:
        # 检查管理员权限
        if current_admin.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        username = user_data.get("username")
        email = user_data.get("email")
        password = user_data.get("password")
        role = user_data.get("role", "user")
        
        if not all([username, email, password]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少必需字段"
            )
        
        # 检查用户是否已存在
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或邮箱已存在"
            )
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            password_hash=jwt_manager.get_password_hash(password),
            role=role,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "status": "success",
            "message": f"用户 {username} 创建成功",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"用户创建失败: {str(e)}"
        )


def _get_user_permissions(role: str) -> list:
    """根据角色获取权限列表"""
    permissions_map = {
        "admin": ["read", "write", "delete", "admin", "device_control", "user_management"],
        "operator": ["read", "write", "device_control"],
        "user": ["read", "device_view"],
        "guest": ["read"]
    }
    return permissions_map.get(role, ["read"])