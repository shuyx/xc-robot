<template>
  <div id="app" class="w-full h-[calc(100vh-100px)] overflow-auto bg-gray-100">
    <div id="content-container" class="p-6">
      <!-- Page Header -->
      <div id="page-header" class="mb-6">
        <h1 class="text-2xl font-bold text-secondary">系统参数配置</h1>
        <p class="text-gray-600">机器人系统全局参数配置与管理</p>
      </div>

      <div class="grid grid-cols-12 gap-6">
        <!-- Left Column: Config Categories -->
        <div id="config-categories" class="col-span-4 bg-white rounded-lg shadow-sm p-4">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold flex items-center">
              <i class="fa-solid fa-folder text-info mr-2"></i>配置分类
            </h2>
            <div class="flex space-x-2">
              <button 
                class="text-xs text-primary hover:text-blue-600"
                @click="expandAllCategories"
              >
                <i class="fa-solid fa-expand mr-1"></i>全部展开
              </button>
              <button 
                class="text-xs text-primary hover:text-blue-600"
                @click="searchConfig"
              >
                <i class="fa-solid fa-search mr-1"></i>搜索配置
              </button>
            </div>
          </div>

          <!-- Hardware Config -->
          <div id="hardware-config" class="mb-4">
            <div 
              class="flex items-center text-secondary font-medium mb-2 cursor-pointer"
              @click="toggleCategory('hardware')"
            >
              <i class="fa-solid fa-wrench text-info mr-2"></i>硬件配置
              <i :class="['fa-solid ml-auto text-gray-400', expandedCategories.hardware ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
            </div>
            <ul v-show="expandedCategories.hardware" class="pl-6 space-y-2">
              <li 
                :class="[
                  'flex items-center py-1 px-2 rounded cursor-pointer',
                  activeConfig === 'robot-arm' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
                ]"
                @click="setActiveConfig('robot-arm')"
              >
                <i class="fa-solid fa-robot mr-2"></i>机械臂参数
                <span v-if="activeConfig === 'robot-arm'" class="ml-auto flex h-2 w-2 rounded-full bg-primary"></span>
              </li>
              <li 
                :class="[
                  'flex items-center py-1 px-2 rounded cursor-pointer',
                  activeConfig === 'chassis' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
                ]"
                @click="setActiveConfig('chassis')"
              >
                <i class="fa-solid fa-truck mr-2"></i>底盘参数
              </li>
              <li 
                :class="[
                  'flex items-center py-1 px-2 rounded cursor-pointer',
                  activeConfig === 'camera' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
                ]"
                @click="setActiveConfig('camera')"
              >
                <i class="fa-solid fa-camera mr-2"></i>相机参数
              </li>
              <li 
                :class="[
                  'flex items-center py-1 px-2 rounded cursor-pointer',
                  activeConfig === 'sensor' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
                ]"
                @click="setActiveConfig('sensor')"
              >
                <i class="fa-solid fa-plug mr-2"></i>传感器参数
              </li>
            </ul>
          </div>

          <!-- Motion Config -->
          <div id="motion-config" class="mb-4">
            <div 
              class="flex items-center text-secondary font-medium mb-2 cursor-pointer"
              @click="toggleCategory('motion')"
            >
              <i class="fa-solid fa-bullseye text-info mr-2"></i>运动配置
              <i :class="['fa-solid ml-auto text-gray-400', expandedCategories.motion ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
            </div>
            <ul v-show="expandedCategories.motion" class="pl-6 space-y-2">
              <li 
                :class="[
                  'flex items-center py-1 px-2 rounded cursor-pointer',
                  activeConfig === 'speed-limit' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
                ]"
                @click="setActiveConfig('speed-limit')"
              >
                <i class="fa-solid fa-bolt mr-2"></i>速度限制
              </li>
              <li 
                :class="[
                  'flex items-center py-1 px-2 rounded cursor-pointer',
                  activeConfig === 'precision' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
                ]"
                @click="setActiveConfig('precision')"
              >
                <i class="fa-solid fa-crosshairs mr-2"></i>精度设置
              </li>
              <li 
                :class="[
                  'flex items-center py-1 px-2 rounded cursor-pointer',
                  activeConfig === 'safety-zone' ? 'bg-primary bg-opacity-10 text-primary' : 'hover:bg-gray-100'
                ]"
                @click="setActiveConfig('safety-zone')"
              >
                <i class="fa-solid fa-shield-alt mr-2"></i>安全区域
              </li>
            </ul>
          </div>

          <!-- Vision Config -->
          <div id="vision-config" class="mb-4">
            <div 
              class="flex items-center text-secondary font-medium mb-2 cursor-pointer"
              @click="toggleCategory('vision')"
            >
              <i class="fa-solid fa-eye text-info mr-2"></i>视觉配置
              <i :class="['fa-solid ml-auto text-gray-400', expandedCategories.vision ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
            </div>
          </div>

          <!-- Safety Config -->
          <div id="safety-config" class="mb-4">
            <div 
              class="flex items-center text-secondary font-medium mb-2 cursor-pointer"
              @click="toggleCategory('safety')"
            >
              <i class="fa-solid fa-shield-alt text-info mr-2"></i>安全配置
              <i :class="['fa-solid ml-auto text-gray-400', expandedCategories.safety ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
            </div>
          </div>

          <!-- Communication Config -->
          <div id="comm-config" class="mb-4">
            <div 
              class="flex items-center text-secondary font-medium mb-2 cursor-pointer"
              @click="toggleCategory('communication')"
            >
              <i class="fa-solid fa-globe text-info mr-2"></i>通信配置
              <i :class="['fa-solid ml-auto text-gray-400', expandedCategories.communication ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
            </div>
          </div>

          <!-- System Config -->
          <div id="system-config" class="mb-4">
            <div 
              class="flex items-center text-secondary font-medium mb-2 cursor-pointer"
              @click="toggleCategory('system')"
            >
              <i class="fa-solid fa-desktop text-info mr-2"></i>系统配置
              <i :class="['fa-solid ml-auto text-gray-400', expandedCategories.system ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
            </div>
          </div>
        </div>

        <!-- Middle Column: Parameter Settings -->
        <div id="parameter-settings" class="col-span-8 space-y-6">
          <!-- Parameter Settings Card -->
          <div id="param-settings-card" class="bg-white rounded-lg shadow-sm p-4">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold flex items-center">
                <i class="fa-solid fa-robot text-primary mr-2"></i>机械臂参数配置
              </h2>
              <div class="flex space-x-2">
                <button 
                  class="text-xs text-gray-500 hover:text-gray-700"
                  @click="showHelp"
                >
                  <i class="fa-solid fa-question-circle mr-1"></i>帮助
                </button>
                <button 
                  class="text-xs text-gray-500 hover:text-gray-700"
                  @click="toggleFullscreen"
                >
                  <i class="fa-solid fa-expand mr-1"></i>全屏
                </button>
              </div>
            </div>

            <!-- Basic Parameters -->
            <div class="mb-6">
              <h3 class="text-md font-medium mb-3 text-secondary flex items-center">
                <span class="h-2 w-2 rounded-full bg-primary mr-2"></span>基础参数
              </h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="flex items-center">
                  <label class="w-32 text-sm">工作空间半径:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.basic.workspaceRadius"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">mm</span>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">最大速度:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.basic.maxSpeed"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">m/s</span>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">最大加速度:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.basic.maxAcceleration"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">m/s²</span>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">负载能力:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.basic.payload"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">kg</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Safety Parameters -->
            <div class="mb-6">
              <h3 class="text-md font-medium mb-3 text-secondary flex items-center">
                <span class="h-2 w-2 rounded-full bg-danger mr-2"></span>安全参数
              </h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="flex items-center">
                  <label class="w-32 text-sm">安全半径:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.safety.safetyRadius"
                      type="text" 
                      class="w-24 border border-danger rounded px-2 py-1 focus:border-danger focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">mm</span>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">碰撞阈值:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.safety.collisionThreshold"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">N</span>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">急停延时:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.safety.emergencyStopDelay"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">ms</span>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">软限位:</label>
                  <div class="flex-1 flex items-center">
                    <label class="inline-flex items-center">
                      <input 
                        v-model="robotConfig.safety.softLimitEnabled"
                        type="checkbox" 
                        class="form-checkbox h-4 w-4 text-primary"
                      >
                      <span class="ml-2 text-sm">启用</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Control Parameters -->
            <div class="mb-6">
              <h3 class="text-md font-medium mb-3 text-secondary flex items-center">
                <span class="h-2 w-2 rounded-full bg-primary mr-2"></span>控制参数
              </h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="flex items-center">
                  <label class="w-32 text-sm">PID增益:</label>
                  <div class="flex-1 flex items-center space-x-2">
                    <div class="flex items-center">
                      <span class="text-xs mr-1">P</span>
                      <input 
                        v-model="robotConfig.control.pidGains.p"
                        type="text" 
                        class="w-12 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                      >
                    </div>
                    <div class="flex items-center">
                      <span class="text-xs mr-1">I</span>
                      <input 
                        v-model="robotConfig.control.pidGains.i"
                        type="text" 
                        class="w-12 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                      >
                    </div>
                    <div class="flex items-center">
                      <span class="text-xs mr-1">D</span>
                      <input 
                        v-model="robotConfig.control.pidGains.d"
                        type="text" 
                        class="w-12 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                      >
                    </div>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">滤波频率:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.control.filterFrequency"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">Hz</span>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">控制周期:</label>
                  <div class="flex-1 flex items-center">
                    <input 
                      v-model="robotConfig.control.controlCycle"
                      type="text" 
                      class="w-24 border border-gray-300 rounded px-2 py-1 focus:border-primary focus:outline-none"
                    >
                    <span class="ml-2 text-sm text-gray-600">ms</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Advanced Parameters -->
            <div class="mb-6">
              <h3 class="text-md font-medium mb-3 text-secondary flex items-center">
                <span class="h-2 w-2 rounded-full bg-primary mr-2"></span>高级参数
              </h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="flex items-center">
                  <label class="w-32 text-sm">动力学参数:</label>
                  <div class="flex-1">
                    <button 
                      class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                      @click="editDynamics"
                    >
                      编辑
                    </button>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">标定数据:</label>
                  <div class="flex-1">
                    <button 
                      class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                      @click="recalibrate"
                    >
                      重新标定
                    </button>
                  </div>
                </div>
                <div class="flex items-center">
                  <label class="w-32 text-sm">补偿矩阵:</label>
                  <div class="flex-1">
                    <button 
                      class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                      @click="updateCompensation"
                    >
                      更新
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end space-x-3 mt-6">
              <button 
                class="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
                @click="resetDefaults"
              >
                重置默认
              </button>
              <button 
                class="px-4 py-2 bg-primary text-white rounded text-sm hover:bg-blue-600"
                @click="applyConfig"
              >
                应用
              </button>
              <button 
                class="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
                @click="testConfig"
              >
                测试
              </button>
            </div>
          </div>

          <!-- Parameter Validation Card -->
          <div id="param-validation-card" class="bg-white rounded-lg shadow-sm p-4">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold flex items-center">
                <i class="fa-solid fa-chart-bar text-primary mr-2"></i>参数验证
              </h2>
            </div>
            <div class="space-y-3">
              <div class="flex items-center text-success">
                <i class="fa-solid fa-check-circle mr-2"></i>
                <span>参数范围检查</span>
              </div>
              <div class="flex items-center text-success">
                <i class="fa-solid fa-check-circle mr-2"></i>
                <span>依赖关系验证</span>
              </div>
              <div class="flex items-center text-warning">
                <i class="fa-solid fa-exclamation-triangle mr-2"></i>
                <span>建议优化项: {{ optimizationSuggestions }}个</span>
                <button 
                  class="ml-2 text-xs underline text-primary"
                  @click="viewOptimizationDetails"
                >
                  查看详情
                </button>
              </div>
            </div>
          </div>

          <!-- Bottom Grid: 2x2 -->
          <div class="grid grid-cols-2 gap-6">
            <!-- Config Operations -->
            <div id="config-operations" class="bg-white rounded-lg shadow-sm p-4">
              <h2 class="text-lg font-semibold flex items-center mb-4">
                <i class="fa-solid fa-clipboard-list text-primary mr-2"></i>配置操作
              </h2>
              
              <!-- Save Config -->
              <div class="mb-4">
                <h3 class="text-md font-medium mb-2 flex items-center">
                  <i class="fa-solid fa-save text-primary mr-2"></i>保存配置:
                </h3>
                <div class="ml-6 space-y-2">
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.saveLocation" 
                      type="radio" 
                      value="local"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">保存到本地</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.saveLocation" 
                      type="radio" 
                      value="robot"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">保存到机器人</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.saveLocation" 
                      type="radio" 
                      value="both"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">同时保存</span>
                  </label>
                </div>
              </div>
              
              <!-- Import Config -->
              <div class="mb-4">
                <h3 class="text-md font-medium mb-2 flex items-center">
                  <i class="fa-solid fa-file-import text-primary mr-2"></i>配置导入:
                </h3>
                <div class="ml-6 space-y-2">
                  <div class="flex items-center mb-2">
                    <button 
                      class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                      @click="selectImportFile"
                    >
                      选择文件
                    </button>
                    <i class="fa-solid fa-folder ml-2 text-gray-500"></i>
                  </div>
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.importMethod" 
                      type="radio" 
                      value="overwrite"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">覆盖现有配置</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.importMethod" 
                      type="radio" 
                      value="merge"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">合并配置</span>
                  </label>
                </div>
              </div>
              
              <!-- Export Config -->
              <div class="mb-4">
                <h3 class="text-md font-medium mb-2 flex items-center">
                  <i class="fa-solid fa-file-export text-primary mr-2"></i>配置导出:
                </h3>
                <div class="ml-6 space-y-2">
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.exportScope" 
                      type="radio" 
                      value="all"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">导出全部配置</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.exportScope" 
                      type="radio" 
                      value="current"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">导出当前分类</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      v-model="configOptions.exportScope" 
                      type="radio" 
                      value="modified"
                      class="form-radio h-4 w-4 text-primary"
                    >
                    <span class="ml-2 text-sm">导出修改项</span>
                  </label>
                </div>
              </div>
              
              <!-- Action Buttons -->
              <div class="flex justify-end space-x-3 mt-4">
                <button 
                  class="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
                  @click="executeImport"
                >
                  执行导入
                </button>
                <button 
                  class="px-4 py-2 bg-primary text-white rounded text-sm hover:bg-blue-600"
                  @click="executeExport"
                >
                  执行导出
                </button>
              </div>
            </div>

            <!-- Config History -->
            <div id="config-history" class="bg-white rounded-lg shadow-sm p-4">
              <h2 class="text-lg font-semibold flex items-center mb-4">
                <i class="fa-solid fa-file-alt text-primary mr-2"></i>配置历史
              </h2>
              
              <h3 class="text-md font-medium mb-2 flex items-center">
                <i class="fa-solid fa-calendar-alt text-primary mr-2"></i>配置变更历史:
              </h3>
              
              <div class="space-y-4 mt-3">
                <div 
                  v-for="(change, index) in configHistory" 
                  :key="index"
                  :class="[
                    'border-l-2 pl-3 py-1',
                    index === 0 ? 'border-primary' : 'border-gray-300'
                  ]"
                >
                  <div class="text-sm font-medium">{{ change.timestamp }}</div>
                  <div class="text-sm">用户: <span :class="index === 0 ? 'text-primary' : 'text-gray-600'">{{ change.user }}</span></div>
                  <div class="text-sm">修改: {{ change.description }}</div>
                  <div class="text-sm">从 <span class="line-through">{{ change.oldValue }}</span> → <span class="font-medium">{{ change.newValue }}</span> {{ change.unit }}</div>
                </div>
              </div>
              
              <div class="flex justify-end space-x-3 mt-4">
                <button 
                  class="px-3 py-1 border border-gray-300 rounded text-xs hover:bg-gray-50"
                  @click="viewHistoryDetails"
                >
                  查看详情
                </button>
                <button 
                  class="px-3 py-1 border border-gray-300 rounded text-xs hover:bg-gray-50"
                  @click="rollbackConfig"
                >
                  回滚
                </button>
              </div>
              
              <h3 class="text-md font-medium mt-6 mb-2 flex items-center">
                <i class="fa-solid fa-lock text-primary mr-2"></i>配置权限
              </h3>
              
              <div class="mt-3 space-y-2">
                <div class="flex justify-between text-sm">
                  <span>当前用户:</span>
                  <span class="font-medium">{{ currentUser.name }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span>权限级别:</span>
                  <span class="font-medium text-success">{{ currentUser.role }}</span>
                </div>
                
                <div class="mt-3">
                  <div class="text-sm font-medium mb-2">修改权限:</div>
                  <div class="space-y-1 ml-2">
                    <label class="flex items-center">
                      <input 
                        v-model="userPermissions.hardwareConfig"
                        type="checkbox" 
                        class="form-checkbox h-4 w-4 text-primary"
                      >
                      <span class="ml-2 text-sm">硬件参数修改</span>
                    </label>
                    <label class="flex items-center">
                      <input 
                        v-model="userPermissions.safetyConfig"
                        type="checkbox" 
                        class="form-checkbox h-4 w-4 text-primary"
                      >
                      <span class="ml-2 text-sm">安全参数修改</span>
                    </label>
                    <label class="flex items-center">
                      <input 
                        v-model="userPermissions.systemConfig"
                        type="checkbox" 
                        class="form-checkbox h-4 w-4 text-primary"
                      >
                      <span class="ml-2 text-sm">系统配置修改</span>
                    </label>
                    <label class="flex items-center">
                      <input 
                        v-model="userPermissions.factoryReset"
                        type="checkbox" 
                        class="form-checkbox h-4 w-4 text-primary"
                      >
                      <span class="ml-2 text-sm">出厂设置重置</span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="flex justify-end space-x-3 mt-4">
                <button 
                  class="px-3 py-1 border border-gray-300 rounded text-xs hover:bg-gray-50"
                  @click="managePermissions"
                >
                  权限管理
                </button>
                <button 
                  class="px-3 py-1 border border-gray-300 rounded text-xs hover:bg-gray-50"
                  @click="viewAuditLog"
                >
                  审计日志
                </button>
              </div>
            </div>

            <!-- Important Reminder -->
            <div id="important-reminder" class="bg-white rounded-lg shadow-sm p-4">
              <h2 class="text-lg font-semibold flex items-center mb-4 text-danger">
                <i class="fa-solid fa-exclamation-triangle text-danger mr-2"></i>重要提醒
              </h2>
              
              <div class="bg-danger bg-opacity-10 p-3 rounded-md mb-4">
                <div class="flex items-start">
                  <i class="fa-solid fa-exclamation-triangle text-danger mt-0.5 mr-2"></i>
                  <div>
                    <p class="text-danger font-medium">配置修改后需要重启机器人服务才能生效</p>
                  </div>
                </div>
              </div>
              
              <div class="mb-4">
                <h3 class="text-md font-medium mb-2 flex items-center">
                  <i class="fa-solid fa-sync text-primary mr-2"></i>建议操作顺序:
                </h3>
                <ol class="list-decimal ml-8 space-y-1 text-sm">
                  <li>停止所有任务</li>
                  <li>应用新配置</li>
                  <li>重启机器人服务</li>
                  <li>验证配置生效</li>
                </ol>
              </div>
              
              <div class="flex justify-end space-x-3 mt-6">
                <button 
                  class="px-4 py-2 bg-danger text-white rounded text-sm hover:bg-red-700"
                  @click="oneClickRestart"
                >
                  一键重启
                </button>
                <button 
                  class="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
                  @click="skipRestart"
                >
                  跳过重启
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 当前活动配置项
const activeConfig = ref('robot-arm')

// 分类展开状态
const expandedCategories = reactive({
  hardware: true,
  motion: true,
  vision: false,
  safety: false,
  communication: false,
  system: false
})

// 机器人配置数据
const robotConfig = reactive({
  basic: {
    workspaceRadius: '800',
    maxSpeed: '1.5',
    maxAcceleration: '2.0',
    payload: '3'
  },
  safety: {
    safetyRadius: '50',
    collisionThreshold: '10',
    emergencyStopDelay: '5',
    softLimitEnabled: true
  },
  control: {
    pidGains: {
      p: '2.0',
      i: '0.1',
      d: '0.05'
    },
    filterFrequency: '100',
    controlCycle: '1'
  }
})

// 配置选项
const configOptions = reactive({
  saveLocation: 'robot',
  importMethod: 'merge',
  exportScope: 'current'
})

// 优化建议数量
const optimizationSuggestions = ref(2)

// 配置历史记录
const configHistory = ref([
  {
    timestamp: '2025-07-19 14:30',
    user: 'admin',
    description: '机械臂速度限制',
    oldValue: '1.2',
    newValue: '1.5',
    unit: 'm/s'
  },
  {
    timestamp: '2025-07-19 10:15',
    user: 'operator',
    description: '安全半径',
    oldValue: '30',
    newValue: '50',
    unit: 'mm'
  }
])

// 当前用户信息
const currentUser = reactive({
  name: 'admin',
  role: '管理员'
})

// 用户权限
const userPermissions = reactive({
  hardwareConfig: true,
  safetyConfig: true,
  systemConfig: true,
  factoryReset: false
})

// 切换分类展开状态
const toggleCategory = (category: string) => {
  expandedCategories[category] = !expandedCategories[category]
}

// 设置活动配置
const setActiveConfig = (config: string) => {
  activeConfig.value = config
}

// 展开所有分类
const expandAllCategories = () => {
  Object.keys(expandedCategories).forEach(key => {
    expandedCategories[key] = true
  })
  ElMessage.success('所有分类已展开')
}

// 搜索配置
const searchConfig = () => {
  ElMessage.info('搜索配置功能正在开发中')
}

// 显示帮助
const showHelp = () => {
  ElMessage.info('帮助文档正在开发中')
}

// 切换全屏
const toggleFullscreen = () => {
  ElMessage.info('全屏功能正在开发中')
}

// 编辑动力学参数
const editDynamics = () => {
  ElMessage.info('动力学参数编辑功能正在开发中')
}

// 重新标定
const recalibrate = () => {
  ElMessage.info('重新标定功能正在开发中')
}

// 更新补偿矩阵
const updateCompensation = () => {
  ElMessage.info('补偿矩阵更新功能正在开发中')
}

// 重置默认值
const resetDefaults = async () => {
  try {
    await ElMessageBox.confirm('确定要重置为默认配置吗？', '确认重置', {
      type: 'warning'
    })
    
    // 重置配置为默认值
    Object.assign(robotConfig.basic, {
      workspaceRadius: '800',
      maxSpeed: '1.5',
      maxAcceleration: '2.0',
      payload: '3'
    })
    
    Object.assign(robotConfig.safety, {
      safetyRadius: '50',
      collisionThreshold: '10',
      emergencyStopDelay: '5',
      softLimitEnabled: true
    })
    
    Object.assign(robotConfig.control, {
      pidGains: { p: '2.0', i: '0.1', d: '0.05' },
      filterFrequency: '100',
      controlCycle: '1'
    })
    
    ElMessage.success('配置已重置为默认值')
  } catch {
    // 用户取消
  }
}

// 应用配置
const applyConfig = () => {
  ElMessage.success('配置已应用')
  console.log('Applied config:', robotConfig)
}

// 测试配置
const testConfig = () => {
  ElMessage.info('配置测试功能正在开发中')
}

// 查看优化详情
const viewOptimizationDetails = () => {
  ElMessage.info('优化详情功能正在开发中')
}

// 选择导入文件
const selectImportFile = () => {
  ElMessage.info('文件选择功能正在开发中')
}

// 执行导入
const executeImport = () => {
  ElMessage.success('配置导入成功')
}

// 执行导出
const executeExport = () => {
  ElMessage.success('配置导出成功')
}

// 查看历史详情
const viewHistoryDetails = () => {
  ElMessage.info('历史详情功能正在开发中')
}

// 回滚配置
const rollbackConfig = () => {
  ElMessage.info('配置回滚功能正在开发中')
}

// 权限管理
const managePermissions = () => {
  ElMessage.info('权限管理功能正在开发中')
}

// 查看审计日志
const viewAuditLog = () => {
  ElMessage.info('审计日志功能正在开发中')
}

// 一键重启
const oneClickRestart = async () => {
  try {
    await ElMessageBox.confirm('确定要重启机器人服务吗？这将中断所有正在进行的操作。', '确认重启', {
      type: 'warning'
    })
    
    ElMessage.info('机器人服务正在重启，请稍候...')
  } catch {
    // 用户取消
  }
}

// 跳过重启
const skipRestart = () => {
  ElMessage.warning('配置可能需要重启后才能生效')
}

onMounted(() => {
  console.log('系统参数配置页面已加载')
})
</script>

<style scoped>
/* 颜色变量 */
.text-secondary {
  color: #2c3e50;
}

.text-info {
  color: #909399;
}

.text-primary {
  color: #409EFF;
}

.text-danger {
  color: #F56C6C;
}

.text-success {
  color: #00A870;
}

.text-warning {
  color: #E6A23C;
}

.bg-danger {
  background-color: #F56C6C;
}

.bg-primary {
  background-color: #409EFF;
}

.bg-success {
  background-color: #00A870;
}

.border-danger {
  border-color: #F56C6C;
}

.border-primary {
  border-color: #409EFF;
}

.hover\\:text-blue-600:hover {
  color: #1E90FF;
}

.hover\\:bg-blue-600:hover {
  background-color: #1E90FF;
}

.hover\\:bg-red-700:hover {
  background-color: #C53030;
}

.focus\\:border-primary:focus {
  border-color: #409EFF;
}

.focus\\:border-danger:focus {
  border-color: #F56C6C;
}

/* 确保字体一致性 */
* {
  font-family: 'Inter', sans-serif;
}

/* Form控件样式 */
.form-checkbox {
  appearance: none;
  border: 1px solid #D1D5DB;
  border-radius: 0.25rem;
  position: relative;
}

.form-checkbox:checked {
  background-color: #409EFF;
  border-color: #409EFF;
}

.form-checkbox:checked::before {
  content: '✓';
  color: white;
  font-size: 0.75rem;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.form-radio {
  appearance: none;
  border: 1px solid #D1D5DB;
  border-radius: 50%;
  position: relative;
}

.form-radio:checked {
  background-color: #409EFF;
  border-color: #409EFF;
}

.form-radio:checked::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: white;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .grid-cols-12 {
    grid-template-columns: 1fr;
  }
  
  .col-span-4,
  .col-span-8 {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .text-2xl {
    font-size: 1.5rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
}
</style>