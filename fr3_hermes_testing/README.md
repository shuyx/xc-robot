# FR3-Hermes 测试系统

本目录包含XC-ROBOT项目的系统化测试框架，用于测试FR3双机械臂和Hermes底盘的各项功能。

## 目录结构

```
fr3_hermes_testing/
├── README.md                        # 本文档
├── TEST_IMPLEMENTATION_GUIDE.md     # 详细测试实施指南
├── single_arm_connection_test.py    # 单臂连接测试示例
├── logs/                           # 测试日志目录
├── data/                          # 测试数据目录
│   ├── trajectories/              # 轨迹数据
│   ├── measurements/              # 测量数据
│   └── reports/                   # 测试报告
└── configs/                       # 测试配置文件
```

## 快速开始

### 1. 第一个测试

```bash
# 激活虚拟环境
source ../venv/bin/activate

# 创建必要目录
mkdir -p logs data/trajectories data/measurements data/reports

# 运行单臂连接测试
python single_arm_connection_test.py --arm right --ip 192.168.58.2
```

### 2. 查看测试结果

测试完成后，可在以下位置查看结果：
- 控制台输出：实时测试进度
- 日志文件：`logs/SAT-001_right_YYYYMMDD_HHMMSS.log`
- 测试报告：`logs/SAT-001_right_report_YYYYMMDD_HHMMSS.json`

## 测试级别

### Level 1: 组件测试
- 单臂连接测试 (SAT-001) ✓
- 单臂运动测试 (SAT-002) 
- 底盘连接测试 (CHT-001)
- 底盘移动测试 (CHT-002)

### Level 2: 集成测试
- 双臂同步测试 (DAT-001)
- 安全距离测试 (DAT-002)
- 底盘臂联动测试 (CAI-001)

### Level 3: 场景测试
- 抓取放置测试 (SCN-001)
- 协作装配测试 (SCN-002)
- 移动巡检测试 (SCN-003)

## 安全须知

⚠️ **重要安全提示**：

1. **测试前检查**
   - 确保工作区域已清空
   - 急停按钮就位
   - 了解紧急停止方法

2. **紧急停止方法**
   - 物理急停按钮（最快）
   - 键盘 Space 键
   - Ctrl+C 中断程序

3. **测试原则**
   - 先仿真，后实机
   - 先低速，后高速
   - 先单臂，后双臂

## 主要特性

### 1. 安全优先
- 所有运动测试都需要用户确认
- 内置紧急停止机制
- 实时安全距离监控

### 2. 数据记录
- 自动生成测试日志
- JSON格式测试报告
- 轨迹数据保存

### 3. 渐进式测试
- 从基础到复杂
- 从静态到动态
- 从单一到集成

## 开发新测试

参考 `single_arm_connection_test.py` 模板，新测试应包含：

```python
class NewTest:
    def __init__(self):
        # 初始化
        
    def setup_logging(self):
        # 配置日志
        
    def safety_check(self):
        # 安全检查
        
    def run_test(self):
        # 执行测试
        
    def generate_report(self):
        # 生成报告
```

## 常用命令

```bash
# 查看测试日志
tail -f logs/latest.log

# 统计测试结果
grep "PASSED\|FAILED" logs/*.log | wc -l

# 清理旧日志（保留7天）
find logs -name "*.log" -mtime +7 -delete
```

## 相关文档

- [项目技术概览](../PROJECT_TECHNICAL_OVERVIEW.md)
- [机器人测试规划](../ROBOT_TESTING_PLAN.md)
- [测试实施指南](TEST_IMPLEMENTATION_GUIDE.md)

## 问题反馈

如遇到问题，请：
1. 查看日志文件
2. 参考实施指南的故障排除章节
3. 记录问题现象和错误信息
4. 联系技术支持

---

**版本**: v1.0  
**更新日期**: 2025-01-15  
**维护团队**: XC-ROBOT测试组