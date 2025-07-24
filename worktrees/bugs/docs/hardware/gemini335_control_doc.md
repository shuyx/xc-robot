# **Gemini 335 系列深度相机控制手册**

**版本**: 1.0  
**日期**: 2025-07-18  
**来源**: 本文档基于`vision_datas`文件夹中的产品规格书、快速启动指南及功能矩阵推断和整理而成。

---

## 1. 概述

### 1.1 产品简介
- **型号**: Gemini 335 / 335L 系列
- **类型**: ToF (Time of Flight) 深度相机
- **核心功能**: 提供高精度的深度图像、红外(IR)图像和RGB彩色图像。
- **数据接口**: USB 3.0 (必须连接到USB 3.0接口以保证带宽和供电)。

### 1.2 核心数据流
相机可以同时输出多种数据流：
- **深度 (Depth)**: 包含每个像素点距离信息的图像。
- **红外 (IR)**: ToF传感器主动发出的红外光形成的灰度图像，用于在暗光环境下进行视觉分析。
- **彩色 (RGB)**: 标准的彩色图像。
- **点云 (Point Cloud)**: 根据深度和相机内参计算出的三维空间点集合。

## 2. 系统要求与环境设置

### 2.1 硬件要求
- **接口**: **必须使用 USB 3.0 Type-A 接口**。USB 2.0 会导致带宽不足或无法识别设备。
- **主机**: 推荐使用具有足够计算能力的x86架构PC。

### 2.2 软件要求
- **操作系统**: 支持 Windows 10/11 和 Linux (Ubuntu 18.04/20.04)。
- **SDK**: 需要安装官方提供的 **Gemini SDK**。该SDK应包含必要的驱动、运行时库以及开发用的API（如Python Wrapper）。

### 2.3 (推断的) Python环境设置
```bash
# 假设官方SDK提供了一个名为 gemini_sdk 的Python包
# 首先，需要将SDK的库路径添加到环境变量中

# 然后通过pip安装
pip install gemini_sdk

# 或者，如果提供的是.whl文件
pip install GeminiSDK-x.x.x-cp39-cp39-manylinux_x86_64.whl
```

## 3. (推断的) Python SDK 控制流程与API详解

以下API是基于通用相机SDK设计模式的推断，旨在提供一个符合逻辑的编程框架。实际函数名请参考官方SDK文档。

### 3.1 核心控制流程
一个标准的相机使用流程如下：
1.  **初始化SDK上下文**: 创建一个SDK实例。
2.  **枚举设备**: 查找并列出当前连接的Gemini相机。
3.  **打开设备**: 选择并打开一个指定的相机。
4.  **配置数据流**: 设置需要开启的数据流（如Depth, RGB）及其分辨率、帧率。
5.  **启动数据流**: 命令相机开始采集和传输数据。
6.  **循环读取帧**: 在一个循环中不断获取最新的数据帧。
7.  **处理数据**: 对获取的帧数据进行处理（如显示、保存、分析）。
8.  **停止数据流**: 任务完成，停止相机数据传输。
9.  **关闭设备**: 释放设备句柄。

### 3.2 推断的API参考

```python
# 导入SDK (推断的包名)
import gemini_sdk as gemini

# --- 1. 初始化与设备管理 ---

# context = gemini.Context()
# 初始化SDK环境

# device_list = context.query_devices()
# 获取一个包含所有已连接Gemini设备的列表

# dev = device_list[0].open()
# 打开列表中的第一个设备

# dev.close()
# 关闭设备

# --- 2. 数据流配置与控制 ---

# config = gemini.Config()
# 创建一个配置对象

# config.enable_stream(gemini.Stream.DEPTH, 640, 480, 30)
# 启用深度流，分辨率640x480，帧率30fps

# config.enable_stream(gemini.Stream.RGB, 1920, 1080, 30)
# 启用RGB流，分辨率1920x1080，帧率30fps

# pipeline = dev.start(config)
# 使用配置启动数据流，返回一个处理管道

# pipeline.stop()
# 停止数据流

# --- 3. 数据帧读取 ---

# frames = pipeline.wait_for_frames(timeout_ms=1000)
# 阻塞式等待一组成套的帧数据（包含已启用的所有流）

# depth_frame = frames.get_depth_frame()
# 从帧集合中获取深度帧

# rgb_frame = frames.get_rgb_frame()
# 从帧集合中获取RGB帧

# --- 4. 帧数据处理 ---

# depth_data = depth_frame.get_data()
# 获取原始深度数据 (通常是一个NumPy数组)

# rgb_data = rgb_frame.get_data()
# 获取原始RGB数据 (NumPy数组)

# width = depth_frame.get_width()
# height = depth_frame.get_height()
# timestamp = depth_frame.get_timestamp()

# --- 5. 参数设置 ---

# exposure = dev.get_option(gemini.Option.EXPOSURE)
# dev.set_option(gemini.Option.EXPOSURE, 150)
# 获取/设置相机参数，如曝光、增益、HDR模式等
```

## 4. 核心功能代码示例

以下是基于上述推断API的实用代码示例。

### 4.1 示例：连接相机并打印设备信息

```python
import gemini_sdk as gemini

def print_device_info():
    ctx = gemini.Context()
    devices = ctx.query_devices()
    if not devices:
        print("未找到Gemini设备。请检查USB 3.0连接。")
        return

    print(f"找到 {len(devices)} 台设备:")
    for i, dev_info in enumerate(devices):
        print(f"  设备 {i}:")
        print(f"    序列号: {dev_info.get_serial_number()}")
        print(f"    固件版本: {dev_info.get_firmware_version()}")

if __name__ == "__main__":
    print_device_info()
```

### 4.2 示例：捕获并保存一张RGB图像

```python
import gemini_sdk as gemini
import cv2 # 使用OpenCV进行图像处理和保存

def capture_single_rgb_image(filepath="rgb_image.jpg"):
    pipeline = None
    try:
        # --- 初始化和配置 ---
        ctx = gemini.Context()
        dev = ctx.query_devices()[0].open()
        
        config = gemini.Config()
        config.enable_stream(gemini.Stream.RGB, 1920, 1080, 30)
        
        # --- 启动并捕获 ---
        pipeline = dev.start(config)
        print("相机已启动，正在捕获RGB图像...")
        
        frames = pipeline.wait_for_frames(2000) # 等待2秒
        rgb_frame = frames.get_rgb_frame()
        
        if rgb_frame:
            # --- 数据处理 ---
            # SDK返回的数据可能是BGR格式，需要转换为RGB
            image_data = rgb_frame.get_data() # 获取NumPy数组
            # 假设数据是 BGR, OpenCV默认使用BGR格式保存
            cv2.imwrite(filepath, image_data)
            print(f"成功捕获图像并保存到 {filepath}")
        else:
            print("捕获图像失败。")
            
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # --- 清理 ---
        if pipeline:
            pipeline.stop()
        print("相机已停止。")

if __name__ == "__main__":
    capture_single_rgb_image()
```

### 4.3 示例：获取深度图并进行伪彩显示

```python
import gemini_sdk as gemini
import cv2
import numpy as np

def display_depth_stream():
    pipeline = None
    try:
        # --- 初始化和配置 ---
        ctx = gemini.Context()
        dev = ctx.query_devices()[0].open()
        config = gemini.Config()
        config.enable_stream(gemini.Stream.DEPTH, 640, 480, 30)
        pipeline = dev.start(config)
        
        print("按 'q' 键退出深度视频流显示...")
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            if not depth_frame:
                continue

            # --- 数据处理与可视化 ---
            depth_image = np.asanyarray(depth_frame.get_data())
            # 将深度图（单位通常是毫米）转换为可视化的伪彩图
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03), # alpha用于调整对比度
                cv2.COLORMAP_JET
            )
            
            cv2.imshow("Depth Stream", depth_colormap)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if pipeline:
            pipeline.stop()
        cv2.destroyAllWindows()
        print("视频流已停止。")

if __name__ == "__main__":
    display_depth_stream()
```

## 5. 关键参数与功能说明

根据文档，Gemini 335系列支持多种高级功能，这些功能应该可以通过SDK的`set_option`方法进行配置。

- **工作模式 (Work Mode)**: 相机有多种工作模式，如高精度模式、高帧率模式等，会影响深度图的质量和帧率。
- **HDR (高动态范围)**: 支持HDR合成，通过多次曝光融合，可以减少黑暗区域或高光区域的噪点，提升深度图质量。
- **滤波 (Filtering)**: SDK可能内置多种滤波器（如时间滤波、空间滤波）来平滑深度数据，减少噪点。
- **同步 (Sync)**: 如果使用多台相机，需要配置主从同步，以防止相互之间的红外光干扰。

## 6. 故障排除

- **问题：设备未找到或无法识别**
  - **解决方案**: 确认相机已牢固连接到 **USB 3.0** 端口。检查设备管理器（Windows）或`lsusb`（Linux）中设备是否被正确识别。

- **问题：数据流不稳定，帧率低**
  - **解决方案**: 确保使用的是USB 3.0端口和高质量的数据线。关闭其他占用USB带宽的设备。降低分辨率或帧率设置。

- **问题：深度图有大量黑洞或噪点**
  - **解决方案**: 
    1. 检查物体表面材质，黑色、透明或高反光材质会吸收或散射红外光，导致深度测量失败。
    2. 尝试开启HDR模式。
    3. 调整曝光和增益参数。
    4. 确保没有其他红外光源（如其他深度相机、遥控器）的干扰。

---