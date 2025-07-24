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

### 2.2 业务监控

**目标说明**: 监控机器人任务执行的业务层面状况，包括当前任务状态、历史任务统计分析，以及MES系统集成的生产环节数据展示。系统支持三个核心场景的自适应切换：办公室/实验室物品转运、装配线上下料/装配/分拣、中央仓储物品分拣/多层级转运。

**页面布局**:
业务监控页面采用四区域布局：顶部任务状态栏、左侧场景切换面板、中间数据可视化区域、右侧MES集成面板。

*   **顶部任务状态栏**:
    *   **当前任务概览**: 实时显示正在执行的任务信息
        *   **任务名称**: 例如"装配线零件抓取"、"办公室文件传递"。
        *   **任务进度**: 动态进度条显示完成百分比 `[████████░░] 75%`。
        *   **执行状态**: "执行中"、"暂停"、"等待"、"完成"状态指示。
        *   **预计完成时间**: 基于历史数据的智能预估 `预计还需: 2分30秒`。
        *   **当前场景**: 自动识别并显示当前场景类型 `场景: 装配线作业`。

*   **左侧场景切换面板**:
    *   **场景选择器**: 三个场景的切换按钮组
        *   **办公室/实验室场景**: 图标+文字按钮，显示该场景任务数量 `办公转运 (3)`。
        *   **装配线场景**: 显示当前生产线状态 `装配线 (运行中)`。
        *   **中央仓储场景**: 显示仓储区域状态 `仓储 (A区-忙碌)`。
    *   **任务队列管理**: 显示不同场景下的待执行任务列表
        *   **待执行任务**: 列表形式显示任务名称、优先级、预计开始时间。
        *   **任务统计**: 今日完成任务数、成功率、平均耗时等关键指标。

*   **中间数据可视化区域** (三选项卡式设计):
    *   **选项卡条设计**:
        *   **位置**: 位于中间区域顶部，占据整个区域宽度
        *   **选项卡标题**: 
            - 选项卡1: `办公室/实验室转运` 🏢
            - 选项卡2: `装配线作业` 🏭  
            - 选项卡3: `中央仓储分拣` 📦
        *   **交互设计**: 点击切换，当前选中选项卡高亮显示，支持平滑过渡动画
        *   **状态保持**: 切换选项卡时保持各选项卡内部的数据状态和筛选条件

    *   **选项卡1: 办公室/实验室物品转运场景**
        *   **顶部概览面板**: 
            - 活跃转运任务数 `当前: 3个任务`
            - 待处理请求数 `待处理: 7个`
            - 平均转运耗时 `平均: 5.2分钟 ↓`
            - 异常转运数 `异常: 0个`
        *   **左侧: 办公室/实验室平面图视图**:
            - 可缩放的区域平面图，高亮显示关键区域(取货点、送货点、充电站)
            - 机器人实时位置标记，显示编号和状态(移动中、待命中、充电中)
            - 物品位置标记，点击查看物品详情
            - 任务路径叠加，用不同颜色区分当前任务和历史路径
        *   **右侧: 任务详情与统计面板**:
            - 当前转运任务列表(表格形式): 任务ID、物品名称、起始点、目标点、状态、预计完成时间
            - 转运效率趋势图(折线图): 每日/每周平均转运时间、任务完成率趋势
            - 机器人利用率图(柱状图): 各机器人工作时长、空闲时长、充电时长比例
            - 异常类型分布图(饼图): 路径阻塞、物品丢失、机器人故障等异常占比

    *   **选项卡2: 装配线上下料/装配/分拣场景**
        *   **顶部生产线概览面板**:
            - 当前生产节拍 `节拍: 45s/件`
            - 物料库存预警 `库存: 正常 ✓`
            - 异常工位数量 `异常: 1个工位`
            - 总产量/目标产量 `完成: 85% (170/200件)`
        *   **中间: 生产线流程图**:
            - 生产线拓扑图，清晰展示各工位(上料、装配、分拣、下料)连接关系
            - 工位状态指示，不同颜色显示状态(正常运行、待料、故障、停机、堵塞)
            - 物料流向动画，直观展示瓶颈位置
            - AGV/机器人位置，显示执行物料配送、装配、分拣任务的机器人实时位置
        *   **右侧: 工位详情与性能分析**:
            - 工位状态列表(表格): 工位编号、当前状态、待处理任务数、最近异常时间
            - 生产效率趋势图(折线图): 每日/每班次生产节拍、合格率、OEE趋势
            - 物料消耗与补给图(柱状图): 关键工位物料消耗速率与补给情况
            - 瓶颈分析: 自动识别并高亮显示瓶颈工位，提供优化建议

    *   **选项卡3: 中央仓储物品分拣/多层级转运场景**
        *   **顶部仓储概览面板**:
            - 仓储利用率 `利用率: 78%`
            - 待分拣任务数 `待分拣: 45个`
            - 异常库存数 `异常: 3个`
            - 今日出入库量 `出库: 120件 | 入库: 98件`
        *   **左侧: 仓库三维/平面布局图**:
            - 可缩放旋转的仓库布局图，展示不同存储区域(高架库、平面库、分拣区、暂存区、发货区)
            - 库位状态，颜色区分占用状态(空闲、占用、预留、异常)
            - AGV/堆垛机/穿梭车实时位置，显示自动化设备位置及编号
            - 热力图，显示高频出入库区域或异常密集区域
        *   **右侧: 分拣/转运任务与库存分析**:
            - 当前分拣/转运任务列表(表格): 任务ID、物品信息、起始库位、目标库位、任务类型、状态、负责设备
            - 库存结构分析图(饼图): 不同品类物品库存占比、周转率
            - 分拣效率趋势图(折线图): 每日/每小时分拣完成量、平均分拣耗时
            - 多层级转运路径优化分析: 显示转运任务路径效率、拥堵点、优化建议
            - 异常库存报告(列表): 盘点差异、损坏、过期等异常状态物品，支持导出

*   **右侧MES集成面板**:
    *   **生产订单状态**: 
        *   **订单信息**: 当前关联的生产订单号、产品型号、数量。
        *   **订单进度**: 订单完成进度条和关键里程碑。
        *   **优先级管理**: 紧急订单标识和优先级调整。
    *   **质检数据统计**:
        *   **检测结果**: 实时质检数据、合格率统计。
        *   **质量趋势**: 质量指标随时间变化的趋势图。
        *   **异常预警**: 质量异常自动报警和处理建议。
    *   **仓储备料情况**:
        *   **库存状态**: 原材料库存水平、安全库存预警。
        *   **备料计划**: 基于生产计划的备料需求预测。
        *   **供应链状态**: 供应商交货状态、采购计划。
    *   **出货情况跟踪**:
        *   **出货统计**: 日出货量、出货进度、配送状态。
        *   **客户订单**: 客户订单状态、交货期预警。
        *   **物流追踪**: 物流配送状态、配送时效分析。

**具体UI元素**:
*   **选项卡系统**: 三个选项卡标题按钮、选项卡内容容器、选项卡切换动画
*   **顶部状态栏**: 任务状态卡片、实时数据指示器、动态进度条
*   **左侧导航**: 场景切换按钮组、任务队列列表、筛选控制器
*   **中间可视化区域**: 
    - 选项卡1: 平面图Canvas、任务表格、效率趋势图表
    - 选项卡2: 生产线流程图、工位状态表格、性能分析图表
    - 选项卡3: 仓库布局图、分拣任务表格、库存分析图表
*   **右侧MES面板**: MES数据集成面板、多维度数据表格、订单状态显示
*   **图表组件**: Chart.js图表（折线图、柱状图、饼图、散点图）
*   **交互组件**: 智能预警指示器、趋势分析图表、数据筛选器、导出功能按钮

### 2.3 综合仪表板

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

*   **业务数据采集器 (`TaskDataCollector`, `MESDataCollector` 等)**:
    *   **职责**: 封装与任务执行系统、MES系统交互的逻辑，获取业务层面的监控数据。
    *   **实现细节**:
        *   `TaskDataCollector`: 从任务管理系统获取任务执行状态、历史任务数据、场景识别等。
        ```python
        class TaskDataCollector:
            def __init__(self):
                self.task_manager = TaskManager()
                self.scene_detector = SceneDetector()
            
            def get_data(self):
                return {
                    'current_task': self._get_current_task(),
                    'task_queue': self._get_task_queue(),
                    'task_statistics': self._get_task_statistics(),
                    'current_scene': self._get_current_scene()
                }
            
            def _get_current_task(self):
                try:
                    current_task = self.task_manager.get_current_task()
                    if current_task:
                        return {
                            'task_id': current_task.id,
                            'task_name': current_task.name,
                            'progress': current_task.progress,
                            'status': current_task.status,
                            'start_time': current_task.start_time,
                            'estimated_completion': current_task.estimated_completion,
                            'scene_type': current_task.scene_type
                        }
                    return None
                except Exception as e:
                    return {'error': str(e)}
            
            def _get_current_scene(self):
                scene_info = self.scene_detector.detect_current_scene()
                return {
                    'scene_type': scene_info.get('type', 'unknown'),
                    'scene_confidence': scene_info.get('confidence', 0),
                    'scene_metrics': scene_info.get('metrics', {})
                }
        ```
        *   `MESDataCollector`: 连接MES系统，获取生产订单、质检数据、库存状态等业务数据。
        ```python
        class MESDataCollector:
            def __init__(self):
                self.mes_api_url = "http://mes.company.com/api/v1"
                self.session = requests.Session()
                self.session.headers.update({'Authorization': 'Bearer ' + MES_TOKEN})
            
            def get_data(self):
                try:
                    return {
                        'production_orders': self._get_production_orders(),
                        'quality_data': self._get_quality_data(),
                        'inventory_status': self._get_inventory_status(),
                        'shipping_status': self._get_shipping_status()
                    }
                except Exception as e:
                    return {'error': str(e), 'connected': False}
            
            def _get_production_orders(self):
                response = self.session.get(
                    f"{self.mes_api_url}/production-orders/active", timeout=5)
                return response.json() if response.status_code == 200 else []
            
            def _get_quality_data(self):
                response = self.session.get(
                    f"{self.mes_api_url}/quality/current", timeout=5)
                return response.json() if response.status_code == 200 else {}
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

*   **业务数据接收与处理 (`BusinessMonitoringClient`)**:
    *   **职责**: 接收来自QWebChannel的业务数据，并动态更新UI显示。
    *   **实现细节**:
        ```javascript
        class BusinessMonitoringClient {
            constructor() {
                this.latestData = null;
                this.isUpdateScheduled = false;
                this.charts = {};
                this.currentScene = 'office_transport';
                this.initializeComponents();
            }
            
            onBusinessDataReceived(data) {
                this.latestData = data;
                if (!this.isUpdateScheduled) {
                    this.isUpdateScheduled = true;
                    requestAnimationFrame(() => this.updateUI());
                }
            }
            
            updateUI() {
                if (!this.latestData) return;
                
                this.updateTaskStatus(this.latestData.current_task);
                this.updateSceneDisplay(this.latestData.current_scene);
                this.updateTaskQueue(this.latestData.task_queue);
                this.updateMESData(this.latestData.mes_data);
                this.updateSceneSpecificData(this.latestData.scene_data);
                
                this.isUpdateScheduled = false;
            }
            
            updateTaskStatus(taskData) {
                if (taskData) {
                    document.getElementById('current-task-name').textContent = 
                        taskData.task_name || '无任务';
                    document.getElementById('task-progress').style.width = 
                        `${taskData.progress || 0}%`;
                    document.getElementById('task-status').textContent = 
                        taskData.status || '待机';
                    document.getElementById('estimated-completion').textContent = 
                        taskData.estimated_completion || '未知';
                }
            }
            
            updateSceneDisplay(sceneData) {
                if (sceneData && sceneData.scene_type !== this.currentScene) {
                    this.currentScene = sceneData.scene_type;
                    this.switchSceneUI(this.currentScene);
                }
            }
            
            switchSceneUI(sceneType) {
                // 隐藏所有场景面板
                document.querySelectorAll('.scene-panel').forEach(panel => {
                    panel.style.display = 'none';
                });
                
                // 显示当前场景面板
                const currentPanel = document.getElementById(`scene-${sceneType}`);
                if (currentPanel) {
                    currentPanel.style.display = 'block';
                }
                
                // 更新场景指示器
                document.getElementById('current-scene-indicator').textContent = 
                    this.getSceneDisplayName(sceneType);
            }
            
            updateSceneSpecificData(sceneData) {
                // 更新选项卡内容，根据当前选中的选项卡显示对应数据
                this.updateTabContent('office_transport', sceneData.office_transport);
                this.updateTabContent('assembly_line', sceneData.assembly_line);
                this.updateTabContent('warehouse_sorting', sceneData.warehouse_sorting);
            }
            
            updateTabContent(tabType, data) {
                if (!data) return;
                
                switch(tabType) {
                    case 'office_transport':
                        this.updateOfficeTransportTab(data);
                        break;
                    case 'assembly_line':
                        this.updateAssemblyLineTab(data);
                        break;
                    case 'warehouse_sorting':
                        this.updateWarehouseSortingTab(data);
                        break;
                }
            }
            
            updateOfficeTransportTab(data) {
                // 更新顶部概览面板
                if (data.overview) {
                    document.getElementById('office-active-tasks').textContent = 
                        `当前: ${data.overview.active_tasks}个任务`;
                    document.getElementById('office-pending-requests').textContent = 
                        `待处理: ${data.overview.pending_requests}个`;
                    document.getElementById('office-avg-time').textContent = 
                        `平均: ${data.overview.avg_time}分钟`;
                    document.getElementById('office-exceptions').textContent = 
                        `异常: ${data.overview.exceptions}个`;
                }
                
                // 更新平面图视图
                if (data.floor_plan) {
                    this.updateFloorPlanView(data.floor_plan);
                }
                
                // 更新任务详情表格
                if (data.task_list) {
                    this.updateTaskListTable('office-task-table', data.task_list);
                }
                
                // 更新统计图表
                if (data.charts) {
                    this.charts.officeEfficiencyTrend.update(data.charts.efficiency_trend);
                    this.charts.robotUtilization.update(data.charts.robot_utilization);
                    this.charts.exceptionDistribution.update(data.charts.exception_distribution);
                }
            }
            
            updateAssemblyLineTab(data) {
                // 更新顶部生产线概览面板
                if (data.overview) {
                    document.getElementById('assembly-current-takt').textContent = 
                        `节拍: ${data.overview.takt_time}s/件`;
                    document.getElementById('assembly-material-status').textContent = 
                        `库存: ${data.overview.material_status}`;
                    document.getElementById('assembly-exception-stations').textContent = 
                        `异常: ${data.overview.exception_stations}个工位`;
                    document.getElementById('assembly-production-progress').textContent = 
                        `完成: ${data.overview.progress}% (${data.overview.completed}/${data.overview.target}件)`;
                }
                
                // 更新生产线流程图
                if (data.flow_diagram) {
                    this.updateProductionFlowDiagram(data.flow_diagram);
                }
                
                // 更新工位状态列表
                if (data.station_list) {
                    this.updateStationListTable('assembly-station-table', data.station_list);
                }
                
                // 更新性能分析图表
                if (data.charts) {
                    this.charts.productionEfficiencyTrend.update(data.charts.efficiency_trend);
                    this.charts.materialConsumption.update(data.charts.material_consumption);
                    this.charts.bottleneckAnalysis.update(data.charts.bottleneck_analysis);
                }
            }
            
            updateWarehouseSortingTab(data) {
                // 更新顶部仓储概览面板
                if (data.overview) {
                    document.getElementById('warehouse-utilization').textContent = 
                        `利用率: ${data.overview.utilization}%`;
                    document.getElementById('warehouse-sorting-tasks').textContent = 
                        `待分拣: ${data.overview.sorting_tasks}个`;
                    document.getElementById('warehouse-exceptions').textContent = 
                        `异常: ${data.overview.exceptions}个`;
                    document.getElementById('warehouse-in-out').textContent = 
                        `出库: ${data.overview.outbound}件 | 入库: ${data.overview.inbound}件`;
                }
                
                // 更新仓库布局图
                if (data.layout) {
                    this.updateWarehouseLayoutView(data.layout);
                }
                
                // 更新分拣/转运任务列表
                if (data.task_list) {
                    this.updateTaskListTable('warehouse-task-table', data.task_list);
                }
                
                // 更新库存分析图表
                if (data.charts) {
                    this.charts.inventoryStructure.update(data.charts.inventory_structure);
                    this.charts.sortingEfficiency.update(data.charts.sorting_efficiency);
                    this.charts.pathOptimization.update(data.charts.path_optimization);
                }
            }
            
            // 选项卡切换控制
            switchTab(tabType) {
                // 隐藏所有选项卡内容
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // 显示选中的选项卡
                document.getElementById(`tab-${tabType}`).classList.add('active');
                
                // 更新选项卡标题样式
                document.querySelectorAll('.tab-header').forEach(header => {
                    header.classList.remove('active');
                });
                document.getElementById(`tab-header-${tabType}`).classList.add('active');
                
                // 保存当前选中的选项卡
                this.currentTab = tabType;
                
                // 触发该选项卡的数据更新
                this.refreshTabData(tabType);
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

### 3.3 业务监控系统集成与路由

*   **Web GUI集成**: 在现有的页面路由系统中添加业务监控页面：
    ```javascript
    const pages = {
        'business-monitoring': {
            icon: '📊',
            title: '业务监控',
            description: '实时监控任务执行状态、场景数据和MES系统集成',
            isBusinessMonitoring: true
        }
    };
    
    function updatePageContent(pageId) {
        const pageData = getPageData(pageId);
        if (pageData && pageData.isBusinessMonitoring) {
            showBusinessMonitoringPage();
            return;
        }
    }
    
    function showBusinessMonitoringPage() {
        // 初始化业务监控客户端
        const businessClient = new BusinessMonitoringClient();
        
        // 启动MES数据同步
        businessClient.startMESSync();
        
        // 启动任务状态监控
        businessClient.startTaskMonitoring();
        
        // 场景自动检测
        businessClient.startSceneDetection();
    }
    ```

*   **场景切换系统**: 实现三个场景间的动态切换：
    ```javascript
    class SceneManager {
        constructor() {
            this.scenes = {
                'office_transport': {
                    name: '办公室/实验室转运',
                    metrics: ['transport_time', 'success_rate', 'item_integrity'],
                    charts: ['efficiency_trend', 'route_map', 'usage_heatmap']
                },
                'assembly_line': {
                    name: '装配线作业',
                    metrics: ['takt_time', 'quality_rate', 'throughput'],
                    charts: ['production_trend', 'quality_analysis', 'workflow_diagram']
                },
                'warehouse_sorting': {
                    name: '中央仓储分拣',
                    metrics: ['sorting_accuracy', 'storage_efficiency', 'cross_area_coord'],
                    charts: ['sorting_stats', 'inventory_flow', 'area_coordination']
                }
            };
            this.currentScene = 'office_transport';
        }
        
        switchScene(sceneType) {
            if (this.scenes[sceneType]) {
                this.currentScene = sceneType;
                this.updateSceneUI(sceneType);
                this.updateSceneMetrics(sceneType);
            }
        }
        
        updateSceneUI(sceneType) {
            // 更新场景指示器
            document.getElementById('scene-indicator').textContent = 
                this.scenes[sceneType].name;
            
            // 显示/隐藏相关图表
            this.scenes[sceneType].charts.forEach(chartId => {
                document.getElementById(chartId).style.display = 'block';
            });
        }
    }
    ```

*   **MES数据同步**: 实现与MES系统的实时数据同步：
    ```javascript
    class MESDataSync {
        constructor() {
            this.syncInterval = 5000; // 5秒同步一次
            this.isConnected = false;
            this.retryCount = 0;
            this.maxRetries = 3;
        }
        
        startSync() {
            setInterval(() => {
                this.syncMESData();
            }, this.syncInterval);
        }
        
        async syncMESData() {
            try {
                const response = await fetch('/api/mes/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        'sync_types': ['orders', 'quality', 'inventory', 'shipping']
                    })
                });
                
                if (response.ok) {
                    const mesData = await response.json();
                    this.updateMESDisplay(mesData);
                    this.isConnected = true;
                    this.retryCount = 0;
                } else {
                    this.handleSyncError();
                }
            } catch (error) {
                this.handleSyncError();
            }
        }
        
        updateMESDisplay(mesData) {
            // 更新生产订单状态
            if (mesData.production_orders) {
                this.updateProductionOrders(mesData.production_orders);
            }
            
            // 更新质检数据
            if (mesData.quality_data) {
                this.updateQualityData(mesData.quality_data);
            }
            
            // 更新库存状态
            if (mesData.inventory_status) {
                this.updateInventoryStatus(mesData.inventory_status);
            }
        }
    }
    ```

*   **配色系统集成**: 使用项目现有配色方案：
    ```css
    .business-monitoring-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
    }
    
    .task-status.running { background: #2ECC71; }
    .task-status.paused { background: #F39C12; }
    .task-status.error { background: #E74C3C; }
    .task-status.waiting { background: #95A5A6; }
    
    .scene-indicator.office { border-left: 4px solid #3498DB; }
    .scene-indicator.assembly { border-left: 4px solid #E67E22; }
    .scene-indicator.warehouse { border-left: 4px solid #9B59B6; }
    
    .mes-connected { color: #2ECC71; }
    .mes-disconnected { color: #E74C3C; }
    ```

---

## 4. 总结

本业务监控模块设计方案遵循XC-ROBOT项目的技术架构和设计理念，提供了一个完整、实用的业务层面监控解决方案。通过场景自适应的UI设计、高效的MES数据集成机制和智能化的任务状态分析，确保操作员能够实时、准确地监控机器人任务执行状况和业务流程数据，为生产运营和业务决策提供强有力的支持。

**关键特性总结**:
- **业务导向**: 从任务执行和业务流程角度提供监控视角，贴近实际应用需求
- **场景自适应**: 支持三个核心场景的智能切换，提供差异化的监控展示
- **MES深度集成**: 实时同步生产订单、质检数据、库存状态等关键业务数据
- **多维度分析**: 涵盖任务效率、质量指标、资源利用等多个维度的数据分析
- **用户友好**: 直观的可视化界面和响应式设计，便于操作员快速理解业务状况
- **技术先进**: 基于现代Web技术栈，支持事件驱动架构和实时数据流处理

**三个场景的针对性设计**:
- **办公室/实验室转运**: 重点关注转运效率、物品安全性和路径优化
- **装配线作业**: 重点关注生产节拍、质量控制和工艺流程管理
- **中央仓储分拣**: 重点关注分拣精度、存储优化和跨区域协调

该方案为XC-ROBOT系统的业务监控需求提供了坚实的技术基础和实现路径，真正实现了从技术监控向业务监控的转变。