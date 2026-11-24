
import serial
from datetime import datetime

# 1. 打开串口
ser = serial.Serial(
    port="COM3",
    baudrate=115200,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=1
)

print("串口连接成功，正在接收 STM32 数据...")

try:
    # 2. 循环接收数据
    while True:
        data = ser.readline()

        if data:
            text = data.decode("utf-8", errors="replace").strip()
            now = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            print(f"[{now}] {text}")

except KeyboardInterrupt:
    print("\n停止接收数据")

finally:
    # 3. 关闭串口
    ser.close()
    print("串口已关闭")
