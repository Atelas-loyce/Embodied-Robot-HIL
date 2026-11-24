# 基于大语言模型与软硬件联合仿真的具身智能机器人系统设计与实现

《大模型原理与技术》2026 年方向 03 阶段进度 · V0.1

本阶段打通了从真实 STM32F103RCT6 到 Python 主机的串口遥测。固件用两个递增计数器观察 FreeRTOS 任务调度，通信任务把计数值作为一行文本发送给主机。

| 模块 | 当前状态 | 代码或验证依据 |
| --- | --- | --- |
| 周期任务 | 已实现 | `firmware/Core/Src/main.c` 中 MotorTask、SensorTask 每轮分别延时 10、100 个 tick。系统时基为 1 kHz。当前负载为计数。 |
| 串口上报 | 已实现 | StartCommunicationTask 发送 `Motor: <计数>, Sensor: <计数>`，随后延时 500 个 tick。主机逐行读取并添加本地时间戳。 |
| 硬件调试 | 作者已上板验证 | 使用 Fire-Debugger 和 OpenOCD 完成烧录及在线调试，Python 收到串口数据。此前观察到电机计数约 100 Hz、传感器计数约 10 Hz、通信约 2 Hz。 |
| 命令接收 | 开发中 | 已创建 128 字节队列、接收任务并配置 USART1 中断优先级 5。回调尝试入队和重挂接收，并记录失败次数。启动路径尚缺首次接收，UartRxTask 仅延时，待实现出队、解析和应答。 |
| PID、仿真与 Agent | 计划中 | 待实现控制闭环、ROS 2 串口桥、Gazebo 场景、多模态感知及 LLM 工具调用。 |

上述频率来自此前板上观察。相对延时还受任务执行和串口发送耗时影响，本版未测量抖动、截止期或导航成功率。

## 复现当前串口遥测

1. 准备 STM32F103RCT6 板、Fire-Debugger（CMSIS-DAP/SWD）、3.3 V USB 转串口或板载串口桥、STM32CubeIDE 及带 STM32F1 目标脚本的 OpenOCD。工程配置来自 STM32CubeMX 6.15.0，固件包为 STM32Cube FW_F1 V1.8.7。
2. 本仓库保留应用源码、工程描述和链接脚本。恢复 HAL、CMSIS、FreeRTOS 时，在临时目录 `firmware` 中复制一份 `firmware/firmware.ioc`，用上述 CubeMX 和固件包按 STM32CubeIDE 工程生成。将生成的 `Drivers` 和 `Middlewares` 两个目录复制到检出仓库的 `firmware/` 下。仓库内 `Core/` 含任务实现，应使用提交版本。
3. 在 STM32CubeIDE 通过 Existing Projects into Workspace 导入仓库的 `firmware` 工程，构建 Debug，目标为 `firmware/Debug/firmware.elf`。本地既有构建配置使用 GNU Tools for STM32 14.3.rel1。
4. 接好 SWD、参考电压和地，确认目标板后，在项目根目录执行下列命令烧录并复位。

   ```powershell
   openocd -f firmware/fire_dap.cfg -c "program firmware/Debug/firmware.elf verify reset exit"
   ```

5. 将 USART1 TX（PA9）接串口桥 RX，两端共地。当前上报只需此单向数据线。Windows 下在项目根目录运行以下命令。脚本默认 COM3，端口不同时先将 `host/serial_test.py` 中的 `port` 改为板子的实际端口。

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python -m pip install pyserial
   .\.venv\Scripts\python host/serial_test.py
   ```

主机按 115200、8N1 接收。观察连续多行的时间戳和两个计数值，以计数增量除以经过时间估算任务频率，以行间隔估算通信频率。Ctrl+C 结束并释放串口。

## 后续架构与验收

目标链路为自然语言指令 → LLM Agent 多步规划 → ROS 2 导航工具与串口桥 → STM32 实时控制 → Gazebo 机器人状态与多模态观测 → Agent 判断任务进度。

1. 补全双向协议，以命令、应答、超时和错误恢复验证上下行。
2. 建立 PID 回路和 ROS 2/Gazebo 桥接，用仿真反馈检验目标速度跟踪。
3. 采集合成导航轨迹，实现自然语言任务分解、导航工具调用与失败后重规划。
4. 在训练或调试场景之外测试新起点、目标及障碍布局，报告任务成功率、步骤效率与泛化结果，并录制模拟器任务视频。
