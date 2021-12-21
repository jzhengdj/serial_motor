#%%

# motor_port = '/dev/serial/by-id/usb-FTDI_USB-RS485_Cable_FT0HBZB9-if00-port0'
motor_port = 'COM6'

import motor
import math
import time

# rail distance/pulse
PULSE_RATION_RAIL = 1000/(37.5*math.pi)
# turning motor ration degree/pulse
PULSE_RATIO_TURN = 100



m = motor.Motor(motor_port, PULSE_RATIO_TURN, 8)

# m.zhome()
# m.wait_ready()

print(m.get_pos())
# m.fwd(45)
m.wait_ready()
# print(m.get_pos())

m.pos(0)
m.wait_ready()
print(m.get_pos())
time.sleep(1)

# m.fwd(-10)
m.pos(-30)
m.wait_ready()
time.sleep(1)
# m.fwd(45)
# m.wait_ready()
m.pos(0)
m.wait_ready()
print(m.get_pos())

del(m)

# %%
