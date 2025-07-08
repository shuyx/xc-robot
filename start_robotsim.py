#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RobotSim 启动脚本
提供更好的启动和退出体验
"""
import sys
import os
import signal

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 XC-ROBOT RobotSim 仿真系统")
    print("=" * 50)
    
    # 检查依赖
    print("检查依赖...")
    try:
        import PyQt5
        print("✅ PyQt5 已安装")
    except ImportError:
        print("❌ PyQt5 未安装，请运行: pip install PyQt5")
        return
    
    try:
        import vtk
        print("✅ VTK 已安装")
    except ImportError:
        print("❌ VTK 未安装，请运行: pip install vtk")
        return
    
    try:
        import numpy
        print("✅ NumPy 已安装")
    except ImportError:
        print("❌ NumPy 未安装，请运行: pip install numpy")
        return
    
    print("✅ 所有依赖检查通过")
    
    # 设置路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    gui_dir = os.path.join(current_dir, 'gui')
    sys.path.insert(0, gui_dir)
    
    print("\n启动RobotSim...")
    print("提示:")
    print("- 使用窗口关闭按钮正常退出")
    print("- 终端中按 Ctrl+C 也可以安全退出")
    print("- 如果程序无响应，可以使用 Ctrl+Z 然后 kill %1")
    print("-" * 50)
    
    try:
        # 导入并启动主窗口
        from main_window import main as gui_main
        gui_main()
        
    except KeyboardInterrupt:
        print("\n\n🔴 收到键盘中断信号")
        print("正在安全关闭程序...")
        
    except Exception as e:
        print(f"\n\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n✅ 程序已退出")
        print("感谢使用 XC-ROBOT RobotSim！")

if __name__ == "__main__":
    main()