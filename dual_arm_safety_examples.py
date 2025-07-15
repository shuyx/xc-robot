"""
双臂机器人安全避障模型使用示例
展示如何在实际应用中使用安全模型
"""

import numpy as np
from dual_arm_safety_model import DualArmSafetyModel, check_dual_arm_safety


def example_basic_safety_check():
    """基础安全检查示例"""
    print("=== 基础安全检查示例 ===\n")
    
    # 创建安全模型
    model = DualArmSafetyModel()
    model.base_distance = 400  # 设置两臂间距为400mm
    
    # 定义两臂的目标位姿
    left_target = np.eye(4)
    left_target[:3, 3] = [-150, 200, 400]  # 左臂目标位置
    
    right_target = np.eye(4)
    right_target[:3, 3] = [550, -200, 400]  # 右臂目标位置
    
    # 当前关节角度（示例）
    left_angles = [0, -np.pi/4, np.pi/4, 0, 0, 0]
    right_angles = [0, -np.pi/4, np.pi/4, 0, 0, 0]
    
    # 执行安全检查
    safety_result = check_dual_arm_safety(
        left_target, right_target, 
        left_angles, right_angles,
        model
    )
    
    print(f"安全状态: {'安全' if safety_result['safe'] else '危险'}")
    print(f"左臂工作空间: {'正常' if safety_result['left_in_workspace'] else '超限'}")
    print(f"右臂工作空间: {'正常' if safety_result['right_in_workspace'] else '超限'}")
    print(f"碰撞检测: {'有碰撞' if safety_result['collision_detected'] else '无碰撞'}")
    
    if safety_result['messages']:
        print("\n警告信息:")
        for msg in safety_result['messages']:
            print(f"  - {msg}")
    print()


def example_trajectory_planning():
    """轨迹规划示例"""
    print("=== 轨迹规划示例 ===\n")
    
    model = DualArmSafetyModel()
    
    # 左臂从初始位置到目标位置
    start_angles = [0, 0, 0, 0, 0, 0]
    
    target_pose = np.eye(4)
    target_pose[:3, 3] = [200, 150, 450]
    
    # 固定右臂位置
    right_angles = [0, -np.pi/6, np.pi/6, 0, 0, 0]
    
    print("规划左臂运动轨迹...")
    path = model.plan_collision_free_motion(
        start_angles, target_pose, 'left', right_angles
    )
    
    if path:
        print(f"规划成功！轨迹包含 {len(path)} 个路径点")
        print("\n轨迹关键点:")
        print(f"起点关节角度: {[f'{a*180/np.pi:.1f}°' for a in path[0]]}")
        print(f"中点关节角度: {[f'{a*180/np.pi:.1f}°' for a in path[len(path)//2]]}")
        print(f"终点关节角度: {[f'{a*180/np.pi:.1f}°' for a in path[-1]]}")
        
        # 验证终点位置
        final_pose = model.forward_kinematics(path[-1], 'left')
        print(f"\n实际终点位置: {final_pose[:3, 3]}")
        print(f"目标位置: {target_pose[:3, 3]}")
        print(f"位置误差: {np.linalg.norm(final_pose[:3, 3] - target_pose[:3, 3]):.2f}mm")
    else:
        print("规划失败！可能原因：")
        print("- 目标位置不可达")
        print("- 路径上存在碰撞")
        print("- 超出关节限制")
    print()


def example_workspace_visualization():
    """工作空间可视化数据生成示例"""
    print("=== 工作空间边界数据生成 ===\n")
    
    model = DualArmSafetyModel()
    
    # 获取左右臂的工作空间边界
    left_boundary = model.get_workspace_boundary('left', height=0)
    right_boundary = model.get_workspace_boundary('right', height=0)
    
    print(f"左臂工作空间边界点数: {len(left_boundary)}")
    print(f"前5个边界点: {left_boundary[:5]}")
    
    print(f"\n右臂工作空间边界点数: {len(right_boundary)}")
    print(f"前5个边界点: {right_boundary[:5]}")
    
    # 计算重叠区域
    overlap_zone_x = model.base_distance / 2
    print(f"\n建议的安全分界线 X坐标: {overlap_zone_x}mm")
    print(f"左臂安全区域: X < {overlap_zone_x - model.safety_margin}mm")
    print(f"右臂安全区域: X > {overlap_zone_x + model.safety_margin}mm")
    print()


def example_real_time_monitoring():
    """实时监控示例"""
    print("=== 实时安全监控示例 ===\n")
    
    model = DualArmSafetyModel()
    
    # 模拟一系列运动状态
    time_steps = [
        # (时间, 左臂角度, 右臂角度)
        (0.0, [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]),
        (0.5, [0.1, -0.2, 0.1, 0, 0, 0], [0, -0.1, 0.1, 0, 0, 0]),
        (1.0, [0.3, -0.4, 0.3, 0, 0, 0], [-0.2, -0.3, 0.2, 0, 0, 0]),
        (1.5, [0.5, -0.5, 0.4, 0, 0, 0], [-0.4, -0.4, 0.3, 0, 0, 0]),
    ]
    
    for t, left_angles, right_angles in time_steps:
        print(f"时间 t={t}s:")
        
        # 检查自碰撞
        left_self_collision = model.check_self_collision(left_angles, 'left')
        right_self_collision = model.check_self_collision(right_angles, 'right')
        
        # 检查双臂碰撞
        dual_collision = model.check_dual_arm_collision(left_angles, right_angles)
        
        # 获取末端位置
        left_pose = model.forward_kinematics(left_angles, 'left')
        right_pose = model.forward_kinematics(right_angles, 'right')
        
        print(f"  左臂末端位置: {left_pose[:3, 3]}")
        print(f"  右臂末端位置: {right_pose[:3, 3]}")
        print(f"  左臂自碰撞: {'是' if left_self_collision else '否'}")
        print(f"  右臂自碰撞: {'是' if right_self_collision else '否'}")
        print(f"  双臂碰撞: {'是' if dual_collision else '否'}")
        
        # 计算两末端距离
        end_distance = np.linalg.norm(left_pose[:3, 3] - right_pose[:3, 3])
        print(f"  末端距离: {end_distance:.1f}mm")
        
        if dual_collision or left_self_collision or right_self_collision:
            print("  ⚠️ 警告: 检测到碰撞风险！")
        
        print()


def example_coordinated_motion():
    """协调运动示例"""
    print("=== 双臂协调运动示例 ===\n")
    
    model = DualArmSafetyModel()
    
    # 定义协调任务：两臂同时运动到指定位置
    print("任务：两臂协调抓取")
    
    # 初始位置（两臂分开）
    left_start = [0, -np.pi/6, np.pi/6, 0, 0, 0]
    right_start = [0, -np.pi/6, np.pi/6, 0, 0, 0]
    
    # 目标：两臂靠近但保持安全距离
    left_target_pose = np.eye(4)
    left_target_pose[:3, 3] = [150, 0, 400]  # 左臂向右移动
    
    right_target_pose = np.eye(4)
    right_target_pose[:3, 3] = [250, 0, 400]  # 右臂向左移动
    
    print("检查目标位置安全性...")
    
    # 求解目标关节角度
    left_target_angles = model.inverse_kinematics(left_target_pose, 'left', left_start)
    right_target_angles = model.inverse_kinematics(right_target_pose, 'right', right_start)
    
    if left_target_angles and right_target_angles:
        print("✓ 两臂目标位置均可达")
        
        # 检查目标状态的碰撞
        target_collision = model.check_dual_arm_collision(
            left_target_angles, right_target_angles
        )
        
        if not target_collision:
            print("✓ 目标状态无碰撞")
            
            # 计算目标状态的末端距离
            left_final = model.forward_kinematics(left_target_angles, 'left')
            right_final = model.forward_kinematics(right_target_angles, 'right')
            distance = np.linalg.norm(left_final[:3, 3] - right_final[:3, 3])
            
            print(f"✓ 末端距离: {distance:.1f}mm (安全阈值: {2*model.link_radius + model.safety_margin}mm)")
            
            # 生成插值路径
            steps = 10
            print(f"\n生成{steps}步插值路径...")
            
            safe_path = True
            for i in range(steps + 1):
                t = i / steps
                
                # 线性插值
                left_interp = [
                    (1-t)*left_start[j] + t*left_target_angles[j] 
                    for j in range(6)
                ]
                right_interp = [
                    (1-t)*right_start[j] + t*right_target_angles[j] 
                    for j in range(6)
                ]
                
                # 检查碰撞
                if model.check_dual_arm_collision(left_interp, right_interp):
                    print(f"  ✗ 第{i}步检测到碰撞")
                    safe_path = False
                    break
            
            if safe_path:
                print("✓ 整个路径安全无碰撞")
            else:
                print("✗ 路径存在碰撞，需要重新规划")
        else:
            print("✗ 目标状态存在碰撞风险")
    else:
        print("✗ 一个或两个目标位置不可达")
    print()


def example_safety_zone_definition():
    """安全区域定义示例"""
    print("=== 安全区域定义示例 ===\n")
    
    model = DualArmSafetyModel()
    
    # 定义一些测试位置
    test_positions = [
        ("左臂正常位置", [-200, 100, 400], 'left'),
        ("左臂边界位置", [180, 0, 400], 'left'),
        ("左臂越界位置", [250, 0, 400], 'left'),
        ("右臂正常位置", [600, -100, 400], 'right'),
        ("右臂边界位置", [220, 0, 400], 'right'),
        ("右臂越界位置", [150, 0, 400], 'right'),
    ]
    
    for name, pos, arm in test_positions:
        pose = np.eye(4)
        pose[:3, 3] = pos
        
        in_zone = model.check_safety_zone(pose, arm)
        print(f"{name}: {pos}")
        print(f"  {arm}臂安全区域: {'✓ 安全' if in_zone else '✗ 危险'}")
        
        # 计算到基座的距离
        base_pos = np.array([0, 0, 0]) if arm == 'left' else np.array([model.base_distance, 0, 0])
        distance = np.linalg.norm(np.array(pos) - base_pos)
        print(f"  到基座距离: {distance:.1f}mm")
        
        # 判断具体原因
        if not in_zone:
            if distance < model.min_reach:
                print(f"  原因: 太靠近基座 (最小距离: {model.min_reach}mm)")
            elif distance > model.max_reach:
                print(f"  原因: 超出最大臂展 (最大距离: {model.max_reach}mm)")
            else:
                print(f"  原因: 进入对侧工作空间")
        print()


if __name__ == "__main__":
    # 运行所有示例
    example_basic_safety_check()
    example_trajectory_planning()
    example_workspace_visualization()
    example_real_time_monitoring()
    example_coordinated_motion()
    example_safety_zone_definition()