# FR3-Hermes 测试实施指南

## 快速开始

### 1. 环境准备
```bash
# 进入项目目录
cd /mnt/c/xc\ robot/mvp-1/xc-robot

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 进入测试目录
cd fr3_hermes_testing
```

### 2. 测试前检查清单

#### 硬件检查
- [ ] FR3右臂已上电，IP: 192.168.58.2
- [ ] FR3左臂已上电，IP: 192.168.58.3
- [ ] Hermes底盘已启动，IP: 192.168.31.211
- [ ] 急停按钮就位且功能正常
- [ ] 工作区域已清理，无障碍物
- [ ] 安全围栏/警示标识已设置

#### 软件检查
- [ ] 网络连接正常（ping测试通过）
- [ ] Python虚拟环境已激活
- [ ] 依赖包已安装完整
- [ ] 测试脚本权限正确

#### 安全检查
- [ ] 了解急停按钮位置
- [ ] 确认紧急停止快捷键（Space）
- [ ] 测试区域人员已撤离
- [ ] 监控摄像头已开启

## 测试执行步骤

### Level 1: 基础功能测试

#### Step 1: 单臂连接测试
```bash
# 测试右臂连接
python single_arm_connection_test.py --arm right --ip 192.168.58.2

# 测试左臂连接
python single_arm_connection_test.py --arm left --ip 192.168.58.3
```

预期输出：
```
[INFO] 连接到右臂 192.168.58.2...
[SUCCESS] 连接成功！
[INFO] SDK版本: x.x.x
[INFO] 机器人状态: 正常
[INFO] 当前关节角度: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

#### Step 2: 底盘连接测试
```bash
python chassis_connection_test.py --ip 192.168.31.211 --port 1448
```

#### Step 3: 基础运动测试（需谨慎）
```bash
# 单臂点动测试 - 会有运动！
python single_arm_motion_test.py --arm right --mode jog

# 底盘移动测试 - 会有运动！
python chassis_motion_test.py --mode manual
```

### Level 2: 集成测试

#### Step 4: 双臂同步测试
```bash
python dual_arm_sync_test.py --safety-distance 100
```

#### Step 5: 安全距离监控
```bash
python safety_monitor.py --threshold 50 --update-rate 100
```

### Level 3: 场景测试

#### Step 6: 预设动作测试
```bash
# 执行挥手动作
python scenario_wave_test.py --arm both --speed 20

# 执行抓取测试
python scenario_grasp_test.py --object cube --position "300,0,200"
```

## 测试脚本模板

### 基础测试脚本结构
```python
#!/usr/bin/env python3
"""
测试脚本模板
测试ID: XXX-001
测试目的: 描述测试目的
"""

import sys
import time
import logging
from typing import Optional
import argparse

# 添加项目路径
sys.path.append('..')
from fr3_control.fairino.Robot import Robot

class TestRunner:
    def __init__(self, robot_ip: str, test_id: str):
        self.robot_ip = robot_ip
        self.test_id = test_id
        self.robot: Optional[Robot] = None
        self.setup_logging()
        
    def setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/{self.test_id}_{time.strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """连接机器人"""
        try:
            self.logger.info(f"正在连接到机器人 {self.robot_ip}...")
            self.robot = Robot(self.robot_ip)
            self.logger.info("连接成功！")
            return True
        except Exception as e:
            self.logger.error(f"连接失败: {e}")
            return False
            
    def safety_check(self) -> bool:
        """安全检查"""
        self.logger.info("执行安全检查...")
        
        # 检查机器人状态
        error, state = self.robot.GetRobotState()
        if error != 0:
            self.logger.error("无法获取机器人状态")
            return False
            
        # 检查是否在安全位置
        error, joints = self.robot.GetActualJointPosDegree()
        if error != 0:
            self.logger.error("无法获取关节位置")
            return False
            
        self.logger.info(f"当前关节位置: {joints}")
        return True
        
    def run_test(self):
        """执行测试"""
        raise NotImplementedError("子类必须实现run_test方法")
        
    def cleanup(self):
        """清理资源"""
        if self.robot:
            self.logger.info("断开连接...")
            # 断开连接的代码
            
    def execute(self):
        """主执行流程"""
        try:
            if not self.connect():
                return False
                
            if not self.safety_check():
                return False
                
            # 用户确认
            response = input("\n准备开始测试，请确保安全区域已清空。继续？(y/n): ")
            if response.lower() != 'y':
                self.logger.info("测试已取消")
                return False
                
            # 执行测试
            self.run_test()
            
            self.logger.info("测试完成")
            return True
            
        except KeyboardInterrupt:
            self.logger.warning("测试被用户中断")
            self.emergency_stop()
            return False
            
        except Exception as e:
            self.logger.error(f"测试异常: {e}")
            self.emergency_stop()
            return False
            
        finally:
            self.cleanup()
            
    def emergency_stop(self):
        """紧急停止"""
        self.logger.critical("执行紧急停止！")
        if self.robot:
            self.robot.StopMotion()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试脚本模板')
    parser.add_argument('--ip', required=True, help='机器人IP地址')
    parser.add_argument('--test-id', default='TEST-001', help='测试ID')
    
    args = parser.parse_args()
    
    # 这里实现具体的测试类
    # runner = SpecificTestRunner(args.ip, args.test_id)
    # runner.execute()
```

## 安全操作规程

### 紧急情况处理

1. **紧急停止**
   - 按下物理急停按钮（最快）
   - 按键盘 Space 键（软件急停）
   - Ctrl+C 中断测试程序

2. **异常情况处理流程**
   ```
   发现异常 → 立即停止 → 评估情况 → 记录问题 → 安全恢复
   ```

3. **常见异常及处理**
   - **碰撞风险**: 立即急停，检查路径规划
   - **通信中断**: 机器人自动停止，检查网络
   - **异常振动**: 降低速度，检查负载
   - **位置偏差**: 停止测试，重新标定

### 测试人员要求

1. **必备知识**
   - 了解机器人基本操作
   - 熟悉急停程序
   - 理解坐标系概念
   - 掌握基础故障排查

2. **操作要求**
   - 测试前必须进行安全检查
   - 首次运行使用低速（10-20%）
   - 时刻关注机器人状态
   - 发现异常立即停止

## 数据记录与分析

### 日志文件位置
```
fr3_hermes_testing/
├── logs/                    # 测试日志
│   ├── SAT-001_20250115_103000.log
│   └── ...
├── data/                    # 测试数据
│   ├── trajectories/        # 轨迹数据
│   ├── measurements/        # 测量数据
│   └── reports/            # 测试报告
└── videos/                 # 测试录像
```

### 数据分析工具
```bash
# 查看测试日志
python analyze_logs.py --test-id SAT-001

# 生成测试报告
python generate_report.py --date 2025-01-15

# 可视化轨迹数据
python visualize_trajectory.py --file data/trajectories/dual_arm_001.json
```

## 常见问题解决

### Q1: 连接超时
```bash
# 检查网络
ping 192.168.58.2

# 检查防火墙
sudo iptables -L

# 重启机器人控制器
# (通过机器人示教器操作)
```

### Q2: 运动异常
```python
# 检查关节限位
error, limits = robot.GetJointLimits()

# 检查奇异点
error, singular = robot.CheckSingularity(target_pose)

# 降低速度重试
robot.SetSpeed(10)  # 10% 速度
```

### Q3: 数据记录失败
```bash
# 检查磁盘空间
df -h

# 检查文件权限
ls -la logs/

# 创建必要目录
mkdir -p logs data/trajectories data/measurements data/reports videos
```

## 进阶测试技巧

### 1. 批量测试
```bash
# 使用测试套件
python run_test_suite.py --config test_configs/level1_tests.yaml
```

### 2. 并行测试
```python
# 同时测试双臂
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as executor:
    left_future = executor.submit(test_left_arm)
    right_future = executor.submit(test_right_arm)
```

### 3. 自动化报告
```python
# 集成测试报告
import pytest

pytest.main(['--html=reports/test_report.html', '--self-contained-html'])
```

---

**更新日期**: 2025-01-15  
**版本**: v1.0  
**维护**: 测试工程团队