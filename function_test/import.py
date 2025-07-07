# 手动测试
import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
fairino_path = os.path.join(current_dir, "fr3_control", "fairino")
libfairino_path = os.path.join(current_dir, "fr3_control", "fairino", "libfairino")

sys.path.insert(0, fairino_path)
sys.path.insert(0, libfairino_path)

# 尝试导入
try:
    from fairino import Robot
    print("✅ fairino导入成功")
except:
    try:
        import Robot
        print("✅ Robot导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")