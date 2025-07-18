# XC-ROBOT 数据监控模块设计方案

**版本**: 1.0  
**日期**: 2025-07-18  
**作者**: Claude & XC-ROBOT Development Team  
**项目**: XC-ROBOT 轮式双臂类人形机器人控制系统

---

## 1. 概述

XC-ROBOT 控制系统基于XC-OS架构，采用Web混合GUI（PyQt5 + QWebEngineView）模式，集成了FR3双机械臂、Hermes移动底盘、Gemini335相机阵列等核心硬件。为确保机器人高效稳定运行，本模块旨在提供一个全面、实时、用户友好的数据监控界面。

**核心需求包括：**
*   **实时性**：硬件状态数据需高频更新（10-20Hz），确保操作员能即时掌握设备状况。
*   **数据多样性**：覆盖硬件状态、系统运行、AI计算及网络通信等多个维度的数据。
*   **用户友好性**：提供直观的可视化界面，便于操作员快速识别异常和进行决策。
*   **系统集成**：与现有Web GUI系统无缝融合，提供统一的操作体验。

本设计方案将详细阐述数据监控模块的页面布局、UI元素以及前后端的技术实现细节，以确保模块的实用性、可扩展性和性能。

---

## 2. 功能页面布局与细节规划

数据监控模块作为一级菜单，下设"硬件监控"、"系统监控"、"AI监控"和"综合仪表板"四个二级菜单，采用选项卡式布局支持快速切换。

### 2.1 硬件监控

**目标说明**: 实时监控FR3双机械臂、Hermes移动底盘和Gemini335相机阵列的运行状态、关键参数和健康状况。

**页面布局**:
硬件监控页面采用灵活的网格布局（CSS Grid），根据屏幕尺寸自适应调整，可同时展示多个硬件组件的监控面板。

*   **机械臂监控面板**:
    *   **左侧区域 (状态总览)**: 展示左右机械臂的摘要状态卡片。每张卡片包含：
        *   **关节角度**: 6个关节的实时角度值（例如：`J1: 0.0°`），通过数值和圆形仪表盘（或滑块）直观显示。
        *   **TCP位姿**: 实时位置（X, Y, Z）和姿态（Rx, Ry, Rz）坐标。
        *   **机器人状态**: 如"运行中"、"停止"、"错误"等。
    *   **右侧区域 (3D可视化与轨迹)**: 一个大型Canvas区域 (`arm-canvas`)，用于：
        *   **3D坐标系可视化**: 实时渲染机械臂的TCP位姿，辅助理解其空间位置和姿态。
        *   **运动轨迹记录**: 实时绘制机械臂TCP的运动路径，便于回溯和分析。

*   **底盘监控面板**:
    *   **顶部区域 (位姿与导航)**:
        *   **坐标显示**: 实时显示底盘的位姿坐标（X, Y, θ），例如：`X: 0.00 m`, `Y: 0.00 m`, `θ: 0.0°`。
        *   **2D地图视图**: 一个Canvas区域 (`chassis-map`)，用于在2D地图上实时显示底盘当前位置和历史运动轨迹。
    *   **底部区域 (电源与运动状态)**:
        *   **电池状态**: 进度条显示电池电量百分比（例如：`电池: 85%`）和充电状态。
        *   **运动参数**: 显示当前速度、角速度等运动参数。

*   **传感器监控面板**:
    *   **主内容区域 (相机网格)**: 采用网格布局展示多个相机设备的状态卡片 (`camera-card`)。每个卡片包含：
        *   **相机名称**: 例如"ToF相机1"。
        *   **连接状态指示器**: 绿色（活跃）、灰色（离线）等。
        *   **实时帧率 (FPS)**: 例如：`FPS: 30`。
        *   **图像质量评估**: 如"良好"、"一般"、"差"。

**具体UI元素**:
*   数值显示、文本标签
*   圆形仪表盘、进度条
*   Canvas（用于3D机械臂可视化、2D地图和运动轨迹）
*   状态指示灯（颜色区分连接/错误状态）
*   卡片式布局（`arm-status-cards`, `camera-card`）

### 2.2 系统监控

**目标说明**: 监控系统层面的运行健康度，包括网络连接、任务执行情况及日志信息。

**页面布局**:
系统监控页面分为网络状态、任务管理和日志分析三个主要区域。

*   **网络状态面板**:
    *   **顶部区域 (设备连接网格)**: `device-grid`展示16个关键设备的连接状态卡片。每张卡片包含：
        *   **设备名称**: 例如"FR3左臂"。
        *   **连接状态**: "已连接"、"断开连接"。
        *   **网络延迟**: 例如：`延迟: 12ms`。
        *   **IP地址**: 设备IP。
    *   **底部区域 (网络统计与趋势)**:
        *   **整体健康度**: 显示网络整体健康百分比和错误率。
        *   **网络延迟图表**: 使用Chart.js绘制条形图或折线图，展示各设备或整体网络的延迟趋势。

*   **任务管理面板**:
    *   **左侧区域 (当前任务)**:
        *   **任务名称**: 显示当前正在执行的任务名称（例如"抓取操作"）。
        *   **进度条**: 直观展示任务执行进度。
        *   **任务状态**: "执行中"、"暂停"、"完成"等。
    *   **右侧区域 (任务队列)**:
        *   **任务列表**: 显示等待执行的任务队列，每个任务包含名称和等待状态。
        *   **性能指标**: 如平均任务耗时、成功率等统计数据。

*   **日志分析面板**:
    *   **主日志显示区域**: 一个可滚动的实时日志显示框，支持分级（INFO, WARN, ERROR）显示，并可进行过滤。
    *   **统计图表区域**:
        *   **错误统计**: 饼图或柱状图展示不同错误类型的发生频率。
        *   **事件时间线**: 折线图或散点图展示关键事件的发生时间分布。

**具体UI元素**:
*   设备卡片、状态标签
*   进度条
*   实时文本显示区域（日志）
*   Chart.js图表（条形图、折线图、饼图）
*   过滤/搜索输入框（日志）

### 2.3 AI监控

**目标说明**: 监控机器人AI大模型和视觉算法的运行状态、性能指标及资源消耗。

**页面布局**:
AI监控页面分为大模型状态和视觉算法性能两个主要部分。

*   **大模型状态面板**:
    *   **左侧区域 (模型状态卡片)**: 展示多个AI模型的卡片 (`model-card`)。每张卡片包含：
        *   **模型名称**: 例如"GPT-4"。
        *   **状态**: "活跃"、"休眠"、"错误"。
        *   **平均响应时间**: 例如：`响应时间: 1.2s`。
        *   **资源使用率**: CPU、GPU、内存使用百分比。
    *   **右侧区域 (性能趋势图)**: `performance-charts`区域，使用Chart.js绘制：
        *   **推理性能趋势**: 例如每秒推理次数 (TPS) 或延迟趋势。
        *   **资源消耗趋势**: CPU/内存/GPU使用率随时间变化的折线图。

*   **视觉算法面板**:
    *   **算法执行状态**: 显示当前正在运行的视觉算法名称和其执行状态。
    *   **检测结果质量**: 例如目标检测的置信度、识别准确率等指标。
    *   **计算资源占用**: 视觉算法运行时对CPU、GPU的实时占用情况。
    *   **结果预览**: 针对关键视觉算法，可提供小窗显示处理后的图像或检测框预览。

**具体UI元素**:
*   模型卡片、状态指示器
*   数值显示、百分比显示
*   Chart.js图表（折线图）
*   图像/视频预览区域（可选）

### 2.4 综合仪表板

**目标说明**: 提供系统整体健康状况的宏观视图，汇总关键指标，并突出显示警报和性能趋势。

**页面布局**:
综合仪表板采用多区域布局，旨在提供一目了然的系统概览。

*   **顶部区域 (系统总览)**: `system-overview`面板，包含：
    *   **系统状态指示器**: 大型显示当前系统状态（"正常运行"、"警告"、"错误"），通过颜色区分。
    *   **健康度评分**: 一个综合性的百分比健康分数（例如：`健康度: 98%`）。
*   **中部区域 (关键指标汇总)**: `key-metrics`区域，以卡片形式 (`metric-card`) 汇总最关键的性能指标，例如：
    *   **电池电量**: `85%`。
    *   **任务成功率**: `96%`。
    *   **网络质量**: "优秀"、"良好"、"一般"。
    *   **机械臂连接**: "已连接"/"断开"。
*   **底部区域 (性能趋势与警报)**:
    *   **性能趋势图表**: `trend-charts`区域，使用Chart.js绘制多条折线图，展示CPU使用率、内存使用率等核心系统资源的长期趋势。
    *   **警报与异常列表**: 显示当前活动的或最近发生的警报信息，包括时间、类型、设备和严重程度。

**具体UI元素**:
*   大型状态指示器（文字+颜色）
*   关键指标卡片（标题、大数值、单位）
*   Chart.js折线图
*   警报列表（表格或卡片形式）

---

## 3. 技术路线与实现方案

本模块的实现将充分利用XC-ROBOT项目现有的PyQt5 + QWebEngineView + QWebChannel混合架构，确保前后端数据的高效实时通信。

### 3.1 后端实现 (Python)

后端主要负责数据采集、聚合、优化、存储以及通过QWebChannel将数据推送到前端。

*   **数据聚合服务 (`MonitoringService`)**:
    *   **职责**: 作为核心服务，协调所有数据采集器，聚合多源数据，并通过独立线程 (`_monitoring_loop`) 以固定频率（例如10Hz）循环收集数据。
    *   **实现细节**:
        *   初始化时加载各种 `DataCollector` 实例。
        *   `start_monitoring()` 方法启动后台线程。
        *   `_monitoring_loop()` 方法在循环中调用 `_collect_all_data()` 获取最新数据，然后通过 `self.web_bridge.push_monitoring_data()` 推送给前端。
        *   `_collect_all_data()` 方法并行调用各个数据采集器的 `get_data()` 方法，将结果整合成一个统一的字典结构。
        ```python
        class MonitoringService:
            def __init__(self):
                self.data_collectors = {
                    'arms': ArmDataCollector(),
                    'chassis': ChassisDataCollector(),
                    'sensors': SensorDataCollector(),
                    'system': SystemDataCollector(),
                    'ai': AIDataCollector()
                }
                self.update_thread = None
                self.is_running = False
                self.web_bridge = None
            
            def start_monitoring(self):
                self.is_running = True
                self.update_thread = threading.Thread(target=self._monitoring_loop)
                self.update_thread.start()
            
            def _monitoring_loop(self):
                while self.is_running:
                    aggregated_data = self._collect_all_data()
                    self.web_bridge.push_monitoring_data(aggregated_data)
                    time.sleep(0.1)  # 10Hz更新频率
        ```

*   **数据采集器 (`ArmDataCollector`, `ChassisDataCollector` 等)**:
    *   **职责**: 封装与特定硬件或系统服务交互的逻辑，获取原始监控数据。
    *   **实现细节**:
        *   `ArmDataCollector`: 使用 `Robot.RPC` 接口调用FR3机械臂SDK，获取关节角度、TCP位姿、机器人状态等。
        ```python
        class ArmDataCollector:
            def __init__(self):
                self.left_arm = Robot.RPC("192.168.58.3")
                self.right_arm = Robot.RPC("192.168.58.2")
            
            def get_data(self):
                return {
                    'left_arm': self._get_arm_data(self.left_arm),
                    'right_arm': self._get_arm_data(self.right_arm)
                }
            
            def _get_arm_data(self, robot):
                try:
                    err1, joints = robot.GetActualJointPosDegree()
                    err2, tcp_pose = robot.GetActualTCPPose()
                    err3, state = robot.GetRobotState()
                    
                    return {
                        'joints': joints if err1 == 0 else None,
                        'tcp_pose': tcp_pose if err2 == 0 else None,
                        'state': state if err3 == 0 else None,
                        'connected': err1 == 0
                    }
                except Exception as e:
                    return {'error': str(e), 'connected': False}
        ```
        *   `ChassisDataCollector`: 使用 `requests.Session` 调用Hermes底盘的RESTful API，获取位姿、电源状态、运动状态等。
        ```python
        class ChassisDataCollector:
            def __init__(self):
                self.base_url = "http://192.168.31.211:1448"
                self.session = requests.Session()
            
            def get_data(self):
                try:
                    pose_response = self.session.get(
                        f"{self.base_url}/api/core/motion/v1/odometer", timeout=2)
                    power_response = self.session.get(
                        f"{self.base_url}/api/core/system/v1/power/status", timeout=2)
                    
                    return {
                        'pose': pose_response.json(),
                        'power': power_response.json(),
                        'connected': True
                    }
                except Exception as e:
                    return {'error': str(e), 'connected': False}
        ```

*   **QWebChannel桥接 (`MonitoringWebBridge`)**:
    *   **职责**: 作为Python与JavaScript之间的通信桥梁，定义信号和槽，实现数据的双向传输。
    *   **实现细节**:
        ```python
        class MonitoringWebBridge(QObject):
            monitoringDataUpdated = pyqtSignal(str)
            
            def __init__(self):
                super().__init__()
                self.monitoring_service = MonitoringService()
                self.monitoring_service.set_data_callback(self.on_data_updated)
            
            def on_data_updated(self, data):
                json_data = json.dumps(data, ensure_ascii=False)
                self.monitoringDataUpdated.emit(json_data)
            
            @pyqtSlot(result=str)
            def get_initial_data(self):
                return json.dumps(self.monitoring_service.get_current_data())
            
            @pyqtSlot()
            def start_monitoring(self):
                self.monitoring_service.start_monitoring()
            
            @pyqtSlot()
            def stop_monitoring(self):
                self.monitoring_service.stop_monitoring()
        ```

### 3.2 前端实现 (HTML/CSS/JavaScript)

前端主要负责接收后端推送的数据，进行实时渲染、图表绘制和用户交互。

*   **数据接收与处理 (`MonitoringClient`)**:
    *   **职责**: 接收来自QWebChannel的数据，并高效地更新UI。
    *   **实现细节**:
        ```javascript
        class MonitoringClient {
            constructor() {
                this.latestData = null;
                this.isUpdateScheduled = false;
                this.charts = {};
                this.initializeComponents();
            }
            
            onMonitoringDataReceived(data) {
                this.latestData = data;
                if (!this.isUpdateScheduled) {
                    this.isUpdateScheduled = true;
                    requestAnimationFrame(() => this.updateUI());
                }
            }
            
            updateUI() {
                if (!this.latestData) return;
                
                this.updateArmStatus(this.latestData.arms);
                this.updateChassisStatus(this.latestData.chassis);
                this.updateSensorStatus(this.latestData.sensors);
                this.updateSystemStatus(this.latestData.system);
                this.updateAIStatus(this.latestData.ai);
                
                this.isUpdateScheduled = false;
            }
            
            updateArmStatus(armData) {
                if (armData.left_arm && armData.left_arm.joints) {
                    armData.left_arm.joints.forEach((angle, index) => {
                        document.getElementById(`left-j${index + 1}`).textContent = 
                            `J${index + 1}: ${angle.toFixed(1)}°`;
                    });
                }
            }
        }
        ```

*   **图表可视化 (`ChartManager`)**:
    *   **职责**: 管理页面中的所有Chart.js图表。
    *   **实现细节**:
        ```javascript
        class ChartManager {
            constructor() {
                this.charts = {};
                this.initializeCharts();
            }
            
            initializeCharts() {
                this.charts.systemTrend = new Chart(
                    document.getElementById('system-trend-chart'),
                    {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'CPU使用率',
                                data: [],
                                borderColor: '#2ECC71',
                                tension: 0.1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: { beginAtZero: true, max: 100 }
                            }
                        }
                    }
                );
            }
            
            updateCharts(data) {
                const now = new Date().toLocaleTimeString();
                this.charts.systemTrend.data.labels.push(now);
                this.charts.systemTrend.data.datasets[0].data.push(data.system.cpu_usage || 0);
                
                if (this.charts.systemTrend.data.labels.length > 20) {
                    this.charts.systemTrend.data.labels.shift();
                    this.charts.systemTrend.data.datasets[0].data.shift();
                }
                
                this.charts.systemTrend.update('none');
            }
        }
        ```

*   **QWebChannel桥接 (`MonitoringBridge`)**:
    *   **职责**: 前端JavaScript与Python后端QWebChannel的连接点。
    *   **实现细节**:
        ```javascript
        class MonitoringBridge {
            constructor() {
                this.bridge = null;
                this.client = new MonitoringClient();
                this.initializeBridge();
            }
            
            initializeBridge() {
                if (typeof qt !== 'undefined' && qt.webChannelTransport) {
                    new QWebChannel(qt.webChannelTransport, (channel) => {
                        this.bridge = channel.objects.monitoring_bridge;
                        this.setupSignalHandlers();
                        this.loadInitialData();
                    });
                }
            }
            
            setupSignalHandlers() {
                this.bridge.monitoringDataUpdated.connect((jsonData) => {
                    const data = JSON.parse(jsonData);
                    this.client.onMonitoringDataReceived(data);
                });
            }
            
            startMonitoring() {
                if (this.bridge) {
                    this.bridge.start_monitoring();
                }
            }
        }
        ```

### 3.3 系统集成与路由

*   **Web GUI集成**: 在现有的页面路由系统中添加监控页面：
    ```javascript
    const pages = {
        'data-monitoring': {
            icon: '📊',
            title: '数据监控',
            description: '实时监控系统运行状态、硬件参数和AI计算性能',
            isMonitoring: true
        }
    };
    
    function updatePageContent(pageId) {
        const pageData = getPageData(pageId);
        if (pageData && pageData.isMonitoring) {
            showMonitoringPage();
            return;
        }
    }
    ```

*   **配色系统集成**: 使用项目现有配色方案：
    ```css
    .monitoring-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
    }
    
    .status-indicator.active { background: #2ECC71; }
    .status-indicator.warning { background: #F39C12; }
    .status-indicator.error { background: #E74C3C; }
    ```

---

## 4. 总结

本数据监控模块设计方案遵循XC-ROBOT项目的技术架构和设计理念，提供了一个完整、实用的实时监控解决方案。通过清晰的页面布局、高效的数据传输机制和优化的前端渲染，确保操作员能够实时、准确地监控机器人系统的各项状态，为系统的稳定运行和故障排查提供强有力的支持。

**关键特性总结**:
- **实时性**: 10-20Hz高频数据更新，确保状态信息的及时性
- **完整性**: 涵盖硬件、系统、AI三个层面的全面监控
- **用户友好**: 直观的可视化界面和响应式设计
- **技术先进**: 基于现代Web技术栈，性能优化到位
- **可扩展**: 插件化架构支持功能扩展

该方案为XC-ROBOT系统的监控需求提供了坚实的技术基础和实现路径。