#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 桥接模块

用于在 Python 后端和 QWebEngineView 中的 JavaScript 前端之间进行通信。
"""

import os
import cv2
import json
import base64
import numpy as np
from PyQt5.QtCore import QObject, pyqtSlot, QTimer, pyqtSignal

class HelpBridge(QObject):
    """
    一个QObject派生的类，其实例将被注册到WebChannel中，
    以便JavaScript可以调用其@pyqtSlot装饰的函数。
    """

    def __init__(self, main_window, parent=None):
        """
        初始化桥接对象。

        Args:
            main_window: 主窗口的引用，用于调用其方法（如显示帮助窗口）。
        """
        super().__init__(parent)
        self._main_window = main_window

    @pyqtSlot(str, result=str)
    def show_document(self, doc_name: str) -> str:
        """
        一个可从JavaScript调用的槽函数，用于请求显示一个帮助文档。

        Args:
            doc_name (str): 请求的文档名称 (例如 'PROJECT_TECHNICAL_OVERVIEW.md')。

        Returns:
            str: 操作结果的反馈信息 (例如 'Success' 或 'Error: File not found')。
        """
        print(f"[Bridge] 接收到JS请求，显示文档: {doc_name}")
        try:
            # 将文档名 (e.g., 'README.md') 转换为HTML文件名 (e.g., 'README.html')
            html_filename = os.path.splitext(doc_name)[0] + '.html'

            # 构建HTML文件的绝对路径
            # __file__ -> web_bridge.py, dirname -> widgets, dirname -> gui, dirname -> project_root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            html_file_path = os.path.join(project_root, 'Md_files', html_filename)

            if os.path.exists(html_file_path):
                # 检查主窗口是否有 show_help_document 方法
                if hasattr(self._main_window, 'show_help_document'):
                    self._main_window.show_help_document(html_file_path)
                    return f"Success: Loaded {html_filename}"
                else:
                    return "Error: Backend is missing the 'show_help_document' method."
            else:
                print(f"[Bridge] 文件未找到: {html_file_path}")
                return f"Error: File not found: {html_filename}"

        except Exception as e:
            error_message = f"Error: An exception occurred in Python: {e}"
            print(f"[Bridge] {error_message}")
            return error_message


class FaceRecognitionBridge(QObject):
    """
    人脸识别功能的桥接类
    """
    
    # 定义信号
    face_detected = pyqtSignal(str)  # 检测到人脸时发出信号
    camera_error = pyqtSignal(str)   # 摄像头错误时发出信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = None
        self.camera_timer = None
        self.is_camera_active = False
        self.face_cascade = None
        self.current_frame = None
        
        # 初始化OpenCV人脸检测器
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            print("[FaceRecognitionBridge] 人脸检测器初始化成功")
        except Exception as e:
            print(f"[FaceRecognitionBridge] 人脸检测器初始化失败: {e}")
    
    @pyqtSlot(result=str)
    def init_camera(self) -> str:
        """
        初始化摄像头
        
        Returns:
            str: 初始化结果
        """
        try:
            print("[FaceRecognitionBridge] 正在初始化摄像头...")
            
            # 尝试打开摄像头
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                # 尝试其他摄像头索引
                for i in range(1, 4):
                    self.camera = cv2.VideoCapture(i)
                    if self.camera.isOpened():
                        break
                
                if not self.camera.isOpened():
                    return json.dumps({"success": False, "error": "无法打开摄像头"})
            
            # 设置摄像头参数
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_camera_active = True
            print("[FaceRecognitionBridge] 摄像头初始化成功")
            
            return json.dumps({
                "success": True,
                "message": "摄像头初始化成功",
                "resolution": "640x480"
            })
            
        except Exception as e:
            error_msg = f"摄像头初始化失败: {e}"
            print(f"[FaceRecognitionBridge] {error_msg}")
            return json.dumps({"success": False, "error": error_msg})
    
    @pyqtSlot(result=str)
    def start_camera_stream(self) -> str:
        """
        开始摄像头流
        
        Returns:
            str: 操作结果
        """
        try:
            if not self.is_camera_active or not self.camera:
                return json.dumps({"success": False, "error": "摄像头未初始化"})
            
            # 启动定时器，定期捕获帧
            if not self.camera_timer:
                self.camera_timer = QTimer()
                self.camera_timer.timeout.connect(self._capture_frame)
            
            self.camera_timer.start(100)  # 100ms间隔，约10fps
            
            print("[FaceRecognitionBridge] 摄像头流已开始")
            return json.dumps({"success": True, "message": "摄像头流已开始"})
            
        except Exception as e:
            error_msg = f"启动摄像头流失败: {e}"
            print(f"[FaceRecognitionBridge] {error_msg}")
            return json.dumps({"success": False, "error": error_msg})
    
    @pyqtSlot(result=str)
    def stop_camera_stream(self) -> str:
        """
        停止摄像头流
        
        Returns:
            str: 操作结果
        """
        try:
            if self.camera_timer:
                self.camera_timer.stop()
            
            print("[FaceRecognitionBridge] 摄像头流已停止")
            return json.dumps({"success": True, "message": "摄像头流已停止"})
            
        except Exception as e:
            error_msg = f"停止摄像头流失败: {e}"
            print(f"[FaceRecognitionBridge] {error_msg}")
            return json.dumps({"success": False, "error": error_msg})
    
    @pyqtSlot(result=str)
    def get_camera_frame(self) -> str:
        """
        获取当前摄像头帧
        
        Returns:
            str: Base64编码的图像数据
        """
        try:
            if not self.is_camera_active or not self.camera:
                return json.dumps({"success": False, "error": "摄像头未激活"})
            
            ret, frame = self.camera.read()
            if not ret:
                return json.dumps({"success": False, "error": "无法读取摄像头帧"})
            
            # 水平翻转图像（镜像效果）
            frame = cv2.flip(frame, 1)
            
            # 转换为JPEG格式
            _, buffer = cv2.imencode('.jpg', frame)
            
            # 转换为base64
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            return json.dumps({
                "success": True,
                "image": f"data:image/jpeg;base64,{jpg_as_text}",
                "timestamp": cv2.getTickCount()
            })
            
        except Exception as e:
            error_msg = f"获取摄像头帧失败: {e}"
            print(f"[FaceRecognitionBridge] {error_msg}")
            return json.dumps({"success": False, "error": error_msg})
    
    @pyqtSlot(result=str)
    def start_face_scan(self) -> str:
        """
        开始人脸扫描
        
        Returns:
            str: 扫描结果
        """
        try:
            if not self.is_camera_active or not self.camera:
                return json.dumps({"success": False, "error": "摄像头未激活"})
            
            if not self.face_cascade:
                return json.dumps({"success": False, "error": "人脸检测器未初始化"})
            
            # 连续捕获几帧进行人脸检测
            face_detected = False
            detection_attempts = 0
            max_attempts = 10
            
            while detection_attempts < max_attempts:
                ret, frame = self.camera.read()
                if not ret:
                    detection_attempts += 1
                    continue
                
                # 转换为灰度图
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 检测人脸
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    face_detected = True
                    break
                
                detection_attempts += 1
            
            if face_detected:
                # 模拟人脸识别结果
                user_data = self._simulate_face_recognition(faces[0])
                return json.dumps({
                    "success": True,
                    "face_detected": True,
                    "user_data": user_data,
                    "message": "人脸识别成功"
                })
            else:
                return json.dumps({
                    "success": True,
                    "face_detected": False,
                    "message": "未检测到人脸"
                })
                
        except Exception as e:
            error_msg = f"人脸扫描失败: {e}"
            print(f"[FaceRecognitionBridge] {error_msg}")
            return json.dumps({"success": False, "error": error_msg})
    
    def _capture_frame(self):
        """
        定时器回调函数，捕获摄像头帧
        """
        try:
            if self.is_camera_active and self.camera:
                ret, frame = self.camera.read()
                if ret:
                    self.current_frame = frame
        except Exception as e:
            print(f"[FaceRecognitionBridge] 捕获帧失败: {e}")
    
    def _simulate_face_recognition(self, face_rect):
        """
        模拟人脸识别功能
        
        Args:
            face_rect: 检测到的人脸区域
            
        Returns:
            dict: 模拟的用户数据
        """
        # 模拟用户数据库
        users = [
            {
                "name": "Kevin Yuan",
                "workstation": "A-12",
                "lastLocation": "实验室",
                "permission": "管理员",
                "avatar": "https://api.dicebear.com/7.x/notionists/svg?scale=200&seed=kevin"
            },
            {
                "name": "Alice Chen",
                "workstation": "B-05",
                "lastLocation": "办公室",
                "permission": "普通用户",
                "avatar": "https://api.dicebear.com/7.x/notionists/svg?scale=200&seed=alice"
            },
            {
                "name": "Bob Wang",
                "workstation": "C-08",
                "lastLocation": "测试室",
                "permission": "普通用户",
                "avatar": "https://api.dicebear.com/7.x/notionists/svg?scale=200&seed=bob"
            }
        ]
        
        # 模拟识别结果（随机选择用户）
        import random
        selected_user = random.choice(users)
        
        # 生成历史任务
        task_history = [
            {
                "time": "2025-07-18 10:30",
                "description": "从\"物料架B\"抓取\"扳手\"到\"工位A-12\"",
                "status": "completed"
            },
            {
                "time": "2025-07-18 09:15",
                "description": "从\"仓库C\"运送\"零件箱\"到\"工位A-12\"",
                "status": "completed"
            },
            {
                "time": "2025-07-18 08:45",
                "description": "从\"物料架A\"抓取\"螺丝刀\"到\"工位B-05\"",
                "status": "cancelled"
            },
            {
                "time": "2025-07-17 16:20",
                "description": "从\"工位A-12\"运送\"成品\"到\"包装区\"",
                "status": "completed"
            },
            {
                "time": "2025-07-17 15:30",
                "description": "从\"物料架D\"抓取\"电路板\"到\"工位A-12\"",
                "status": "completed"
            }
        ]
        
        return {
            **selected_user,
            "taskHistory": task_history,
            "recognition_confidence": 0.85,
            "face_rect": face_rect.tolist()
        }
    
    @pyqtSlot(result=str)
    def release_camera(self) -> str:
        """
        释放摄像头资源
        
        Returns:
            str: 操作结果
        """
        try:
            if self.camera_timer:
                self.camera_timer.stop()
                self.camera_timer = None
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            self.is_camera_active = False
            
            print("[FaceRecognitionBridge] 摄像头资源已释放")
            return json.dumps({"success": True, "message": "摄像头资源已释放"})
            
        except Exception as e:
            error_msg = f"释放摄像头资源失败: {e}"
            print(f"[FaceRecognitionBridge] {error_msg}")
            return json.dumps({"success": False, "error": error_msg})
    
    def __del__(self):
        """
        析构函数，确保资源释放
        """
        self.release_camera()
