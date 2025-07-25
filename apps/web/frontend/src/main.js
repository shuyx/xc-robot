// XC-ROBOT Web测试控制台主要JavaScript文件
// 实现前后端解耦的机器人控制界面

class XCRobotController {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.wsUrl = 'ws://localhost:8000/ws';
        this.websocket = null;
        this.robotStatus = {
            rightArm: { connected: false, status: '未连接' },
            leftArm: { connected: false, status: '未连接' },
            chassis: { connected: false, status: '未连接' }
        };
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.updateUI();
        this.logMessage('系统', 'XC-ROBOT控制器初始化完成');
    }
    
    // WebSocket连接管理
    connectWebSocket() {
        try {
            this.websocket = new WebSocket(`${this.wsUrl}/robot-status`);
            
            this.websocket.onopen = () => {
                this.logMessage('WebSocket', '实时状态连接已建立');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleStatusUpdate(data);
            };
            
            this.websocket.onclose = () => {
                this.logMessage('WebSocket', '连接已断开，尝试重连...');
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                this.logMessage('错误', `WebSocket连接错误: ${error.message}`);
            };
        } catch (error) {
            this.logMessage('错误', `WebSocket连接失败: ${error.message}`);
        }
    }
    
    // 处理状态更新
    handleStatusUpdate(data) {
        if (data.type === 'robot_status') {
            this.robotStatus = { ...this.robotStatus, ...data.status };
            this.updateUI();
        } else if (data.type === 'log_message') {
            this.logMessage(data.source, data.message);
        }
    }
    
    // API调用封装
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || `API调用失败: ${response.status}`);
            }
            
            return result;
        } catch (error) {
            this.logMessage('错误', `API调用失败: ${error.message}`);
            throw error;
        }
    }
    
    // 机器人连接控制
    async connectRightArm() {
        try {
            this.logMessage('右臂', '正在连接FR3右臂...');
            const result = await this.apiCall('/robots/connect', 'POST', {
                robot_type: 'fr3_right',
                ip_address: '192.168.58.2'
            });
            this.logMessage('右臂', '连接成功');
        } catch (error) {
            this.logMessage('错误', `右臂连接失败: ${error.message}`);
        }
    }
    
    async connectLeftArm() {
        try {
            this.logMessage('左臂', '正在连接FR3左臂...');
            const result = await this.apiCall('/robots/connect', 'POST', {
                robot_type: 'fr3_left',
                ip_address: '192.168.58.3'
            });
            this.logMessage('左臂', '连接成功');
        } catch (error) {
            this.logMessage('错误', `左臂连接失败: ${error.message}`);
        }
    }
    
    async connectChassis() {
        try {
            this.logMessage('底盘', '正在连接Hermes底盘...');
            const result = await this.apiCall('/robots/connect', 'POST', {
                robot_type: 'hermes',
                ip_address: '192.168.0.100'
            });
            this.logMessage('底盘', '连接成功');
        } catch (error) {
            this.logMessage('错误', `底盘连接失败: ${error.message}`);
        }
    }
    
    async disconnectRightArm() {
        try {
            await this.apiCall('/robots/disconnect', 'POST', { robot_type: 'fr3_right' });
            this.logMessage('右臂', '已断开连接');
        } catch (error) {
            this.logMessage('错误', `右臂断开失败: ${error.message}`);
        }
    }
    
    async disconnectLeftArm() {
        try {
            await this.apiCall('/robots/disconnect', 'POST', { robot_type: 'fr3_left' });
            this.logMessage('左臂', '已断开连接');
        } catch (error) {
            this.logMessage('错误', `左臂断开失败: ${error.message}`);
        }
    }
    
    async disconnectChassis() {
        try {
            await this.apiCall('/robots/disconnect', 'POST', { robot_type: 'hermes' });
            this.logMessage('底盘', '已断开连接');
        } catch (error) {
            this.logMessage('错误', `底盘断开失败: ${error.message}`);
        }
    }
    
    // 任务执行
    async executeTestTask() {
        try {
            this.logMessage('任务', '开始执行测试任务...');
            const result = await this.apiCall('/tasks/execute', 'POST', {
                task_type: 'test_workflow',
                parameters: {
                    workstation: 'station_a',
                    right_arm_action: 'pick_object',
                    left_arm_action: 'place_object'
                }
            });
            this.logMessage('任务', `任务已启动，ID: ${result.task_id}`);
        } catch (error) {
            this.logMessage('错误', `任务执行失败: ${error.message}`);
        }
    }
    
    async moveToHome() {
        try {
            this.logMessage('任务', '正在回到初始位置...');
            await this.apiCall('/tasks/execute', 'POST', {
                task_type: 'move_to_home'
            });
            this.logMessage('任务', '已回到初始位置');
        } catch (error) {
            this.logMessage('错误', `归位失败: ${error.message}`);
        }
    }
    
    async dualArmDemo() {
        try {
            this.logMessage('任务', '开始双臂协调演示...');
            await this.apiCall('/tasks/execute', 'POST', {
                task_type: 'dual_arm_demo',
                parameters: {
                    demo_type: 'coordinated_movement'
                }
            });
            this.logMessage('任务', '双臂协调演示已启动');
        } catch (error) {
            this.logMessage('错误', `双臂演示失败: ${error.message}`);
        }
    }
    
    async chassisNavigation() {
        try {
            this.logMessage('任务', '开始底盘导航测试...');
            await this.apiCall('/tasks/execute', 'POST', {
                task_type: 'chassis_navigation',
                parameters: {
                    target_position: { x: 1.0, y: 0.5, theta: 0 }
                }
            });
            this.logMessage('任务', '底盘导航测试已启动');
        } catch (error) {
            this.logMessage('错误', `导航测试失败: ${error.message}`);
        }
    }
    
    // 紧急停止
    async emergencyStop() {
        try {
            this.logMessage('紧急', '执行紧急停止...');
            await this.apiCall('/robots/emergency-stop', 'POST');
            this.logMessage('紧急', '所有机器人已紧急停止');
        } catch (error) {
            this.logMessage('错误', `紧急停止失败: ${error.message}`);
        }
    }
    
    // UI更新
    updateUI() {
        // 更新右臂状态
        const rightArmStatus = document.getElementById('right-arm-status');
        const rightArmIndicator = rightArmStatus.previousElementSibling;
        if (this.robotStatus.rightArm.connected) {
            rightArmStatus.textContent = this.robotStatus.rightArm.status;
            rightArmIndicator.className = 'status-indicator status-connected';
        } else {
            rightArmStatus.textContent = '未连接';
            rightArmIndicator.className = 'status-indicator status-disconnected';
        }
        
        // 更新左臂状态
        const leftArmStatus = document.getElementById('left-arm-status');
        const leftArmIndicator = leftArmStatus.previousElementSibling;
        if (this.robotStatus.leftArm.connected) {
            leftArmStatus.textContent = this.robotStatus.leftArm.status;
            leftArmIndicator.className = 'status-indicator status-connected';
        } else {
            leftArmStatus.textContent = '未连接';
            leftArmIndicator.className = 'status-indicator status-disconnected';
        }
        
        // 更新底盘状态
        const chassisStatus = document.getElementById('chassis-status');
        const chassisIndicator = chassisStatus.previousElementSibling;
        if (this.robotStatus.chassis.connected) {
            chassisStatus.textContent = this.robotStatus.chassis.status;
            chassisIndicator.className = 'status-indicator status-connected';
        } else {
            chassisStatus.textContent = '未连接';
            chassisIndicator.className = 'status-indicator status-disconnected';
        }
    }
    
    // 日志管理
    logMessage(source, message) {
        const logContainer = document.getElementById('log-container');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.innerHTML = `[${timestamp}] [${source}] ${message}`;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // 限制日志条数，避免内存过度使用
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
}

// 全局控制器实例
let robotController;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    robotController = new XCRobotController();
});

// 全局函数，供HTML按钮调用
function connectRightArm() { robotController.connectRightArm(); }
function connectLeftArm() { robotController.connectLeftArm(); }
function connectChassis() { robotController.connectChassis(); }
function disconnectRightArm() { robotController.disconnectRightArm(); }
function disconnectLeftArm() { robotController.disconnectLeftArm(); }
function disconnectChassis() { robotController.disconnectChassis(); }
function executeTestTask() { robotController.executeTestTask(); }
function moveToHome() { robotController.moveToHome(); }
function dualArmDemo() { robotController.dualArmDemo(); }
function chassisNavigation() { robotController.chassisNavigation(); }
function emergencyStop() { robotController.emergencyStop(); }