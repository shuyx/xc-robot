# xc-robot
xc robot 的调试

## Code Reviews

- hermes_controller.py：控制hermes底盘，在几个点之间来回运行；
- hermes_test_connection.py：连接底盘hermes，测试hermes在wfi连接模式（STA模式）下的连接如何；
- fr3_simple_test.py：测试单个机械臂，为右臂，运动较为复杂，存在负载过重的问题（运动复杂但速度慢）
- fr3_safe_test.py：测试单个机械臂，可控运动下的行为（注意，要把当前状态的照片发过去进行分析，好让他们知道机械臂互相之间可能会打架）