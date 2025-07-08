# 3D模型准备指南 - 从SolidWorks到运动仿真

## 问题说明

要实现机械臂的运动仿真，需要：
1. **分离的部件**：每个可动部件必须是独立的模型
2. **关节层次**：定义部件之间的父子关系
3. **关节轴**：定义每个关节的旋转轴

## 从SolidWorks准备模型

### 方法1：导出分离的STL文件（推荐）

1. **打开装配体文件**（.sldasm）

2. **识别需要分离的部件**：
   - 基座（Base）
   - 连杆1（Link1）
   - 连杆2（Link2）
   - 连杆3（Link3）
   - 连杆4（Link4）
   - 连杆5（Link5）
   - 连杆6（Link6）
   - 末端执行器（End Effector）

3. **逐个导出STL**：
   - 在装配体中右键点击部件
   - 选择"另存为"
   - 选择STL格式
   - 重要：**坐标系选择"装配体原点"**

4. **命名规范**：
   ```
   fr3_base.stl
   fr3_link1.stl
   fr3_link2.stl
   fr3_link3.stl
   fr3_link4.stl
   fr3_link5.stl
   fr3_link6.stl
   fr3_gripper.stl
   ```

### 方法2：使用SolidWorks的运动学信息

1. **导出URDF**（如果有SolidWorks to URDF插件）：
   - 安装SW2URDF插件
   - 定义关节和连杆
   - 直接导出URDF + STL文件

2. **手动记录关节信息**：
   - 记录每个关节的位置
   - 记录旋转轴方向
   - 记录关节限位

### 方法3：使用其他格式

1. **STEP文件**（保留装配信息）：
   - 导出为STEP
   - 使用FreeCAD等软件分离部件
   - 再导出各个STL

2. **Collada(.dae)格式**：
   - 支持关节和动画
   - 可以直接包含运动学信息

## 在程序中使用分离的模型

### 1. 创建模型目录结构
```
models/
├── fr3_left/
│   ├── base.stl
│   ├── link1.stl
│   ├── link2.stl
│   └── ...
└── fr3_right/
    ├── base.stl
    ├── link1.stl
    └── ...
```

### 2. 加载模型的代码示例

```python
class FR3Robot3D:
    def __init__(self, robot_3d_widget, side="left"):
        self.widget = robot_3d_widget
        self.side = side
        self.parts = {}
        
    def load_robot_parts(self, model_dir):
        """加载机器人各部件"""
        part_names = [
            "base", "link1", "link2", "link3", 
            "link4", "link5", "link6", "gripper"
        ]
        
        for part in part_names:
            stl_file = os.path.join(model_dir, f"{part}.stl")
            if os.path.exists(stl_file):
                actor = self.widget.load_stl_model(stl_file, f"{self.side}_{part}")
                self.parts[part] = actor
                
    def setup_joint_hierarchy(self):
        """设置关节层次关系"""
        # 定义关节位置（相对于父部件）
        self.joint_positions = {
            "joint1": [0, 0, 147],      # 基座到J1
            "joint2": [0, 0, 0],        # J1到J2
            "joint3": [0, 0, 280],      # J2到J3
            "joint4": [0, 0, 0],        # J3到J4
            "joint5": [0, 0, 240],      # J4到J5
            "joint6": [0, 0, 0],        # J5到J6
        }
        
    def update_joint_angles(self, angles):
        """更新关节角度"""
        # 基座不动
        base_transform = vtk.vtkTransform()
        base_transform.Identity()
        
        # J1旋转（绕Z轴）
        j1_transform = vtk.vtkTransform()
        j1_transform.SetInput(base_transform)
        j1_transform.Translate(*self.joint_positions["joint1"])
        j1_transform.RotateZ(angles[0])
        
        if "link1" in self.parts:
            self.parts["link1"].SetUserTransform(j1_transform)
            
        # J2旋转（绕Y轴）
        j2_transform = vtk.vtkTransform()
        j2_transform.SetInput(j1_transform)
        j2_transform.Translate(*self.joint_positions["joint2"])
        j2_transform.RotateY(angles[1])
        
        # 继续其他关节...
```

## 临时解决方案（无STL文件时）

如果暂时没有分离的STL文件，可以：

1. **使用简化的几何体**：
```python
def create_simplified_fr3(self):
    """创建简化的FR3模型"""
    # 基座 - 圆柱体
    base = self.create_cylinder(60, 100, "base")
    base.GetProperty().SetColor(0.5, 0.5, 0.5)
    
    # 连杆1 - 长方体
    link1 = self.create_box(80, 80, 140, "link1")
    link1.GetProperty().SetColor(0.6, 0.6, 0.8)
    
    # 连杆2 - 长方体
    link2 = self.create_box(60, 60, 280, "link2")
    link2.GetProperty().SetColor(0.7, 0.7, 0.8)
    
    # ... 继续创建其他连杆
```

2. **使用线框模型**：
   - 只显示关节连线
   - 快速验证运动学

3. **使用占位符**：
   - 用简单形状代表各部件
   - 主要关注运动学验证

## 推荐工作流程

1. **短期**：使用简化几何体验证运动学
2. **中期**：从SolidWorks导出分离的STL
3. **长期**：建立完整的URDF模型

## 工具推荐

1. **MeshLab**：查看和处理STL文件
2. **FreeCAD**：分离STEP文件中的部件
3. **Blender**：高级模型处理和简化
4. **SW2URDF**：SolidWorks插件，直接生成URDF

## 注意事项

1. **坐标系一致性**：确保所有部件使用相同的坐标系
2. **单位一致性**：STL默认单位是mm
3. **模型简化**：过于复杂的模型会影响性能
4. **关节原点**：每个部件的原点应该在关节轴上