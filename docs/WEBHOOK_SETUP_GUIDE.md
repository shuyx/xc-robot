# XC-ROBOT Webhook自动通知系统使用指南

## 📋 关键词配置清单

在您的webhook机器人中设置关键词即可启用自动通知：

### 🔑 统一关键词

| 关键词 | 触发场景 | 说明 |
|--------|----------|------|
| `infobot` | 所有事件 | 文件操作、调试成功、Git提交、测试完成、错误警告等所有事件 |

## 🚀 快速开始

### 1. 配置Webhook URL

编辑 `config/webhook_config.yaml` 文件：

```yaml
webhook:
  enabled: true
  url: "你的实际webhook地址"  # 替换这里
```

### 2. 启动监控服务

```bash
# 启动后台监控服务
python apps/launchers/start_webhook_monitor.py --daemon

# 测试webhook发送
python apps/launchers/start_webhook_monitor.py --test

# 检查配置状态
python apps/launchers/start_webhook_monitor.py --config-check
```

### 3. 验证功能

- ✅ 创建或修改代码文件 → 自动发送 `code_file` 通知
- ✅ 运行测试并成功 → 自动发送 `debug_success` 通知  
- ✅ 执行git commit → 自动发送 `commit` 通知

## 🎯 自动监控功能

### 文件监控
- 监控 `.py`, `.js`, `.html`, `.css`, `.md` 等文件
- 自动识别文件功能并生成描述
- 防抖动机制避免重复通知

### 调试监控
- 监控日志文件中的成功标识
- 自动识别测试结果
- 支持JSON格式测试报告

### Git集成
- 自动安装git hooks
- 捕获commit信息
- 统计变更文件数量

## 📄 消息格式示例

### 代码文件通知
```
📄 代码文件创建

infobot **文件**: webhook_service.py
**功能**: 包含类和方法定义
**时间**: 2025-01-27 10:30:45
**项目**: XC-ROBOT
```

### 调试成功通知
```
✅ 调试成功

infobot **调试内容**: 系统启动测试
**结果**: 所有模块加载成功
**时间**: 2025-01-27 10:31:12
**项目**: XC-ROBOT
```

### Git提交通知
```
📦 代码提交

infobot **提交信息**: feat: 添加webhook自动通知系统
**文件数量**: 5
**作者**: Claude
**时间**: 2025-01-27 10:32:00
**项目**: XC-ROBOT
```

## ⚙️ 高级配置

### 自定义监控模式

在 `config/webhook_config.yaml` 中配置：

```yaml
monitoring:
  file_watch:
    enabled: true
    patterns: ["*.py", "*.js", "*.html"]  # 监控文件类型
    exclude_dirs: ["__pycache__", ".git"] # 排除目录
    debounce_seconds: 2                   # 防抖动时间
    
  debug_watch:
    enabled: true
    success_patterns:                     # 成功标识
      - "Test passed"
      - "SUCCESS"
      - "完成"
    log_files: ["logs/*.log"]            # 监控日志文件
    
  git_watch:
    enabled: true
    hook_types: ["post-commit"]          # Git钩子类型
```

### 消息格式自定义

```yaml
templates:
  file_created:
    keyword: "code_file"
    title: "📄 代码文件创建"
    format: |
      **文件**: {filename}
      **功能**: {description}
      **时间**: {timestamp}
```

## 🔧 故障排除

### 常见问题

1. **Webhook发送失败**
   - 检查URL配置是否正确
   - 确认网络连接正常
   - 查看日志文件 `logs/webhook_daemon.log`

2. **文件监控不工作**
   - 确认 `enabled: true`
   - 检查文件类型是否在监控范围内
   - 安装watchdog库：`pip install watchdog`

3. **Git钩子未触发**
   - 确认在Git仓库中运行
   - 检查 `.git/hooks/` 目录权限
   - 手动重新安装钩子

### 手动测试

```bash
# 测试配置
python -c "from services.webhook import get_webhook_notifier; print(get_webhook_notifier().config)"

# 手动发送通知
python -c "from services.webhook import notify_debug_success; notify_debug_success('测试', '成功')"
```

## 📊 监控状态查看

```bash
# 查看服务状态
python apps/launchers/start_webhook_monitor.py --config-check

# 查看Git钩子状态  
python -c "from services.webhook.git_hooks import GitHookManager; print(GitHookManager().check_hooks_status())"
```

---

**🎉 完成配置后，您的XC-ROBOT将具备完全自动化的webhook通知能力！**