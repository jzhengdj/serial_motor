from re import X
import minimalmodbus
import time
import math

# linear motor
# RATIO_PULSE_MM = 1000/6
# rail
RATIO_PULSE_MM = 1000/(37.5*math.pi)
def dWord2List(val):
    return [(val&0xffff0000)>>16, val&0xffff]

class linearMotor:

#    def setting(self, port, addr):
#        self.instrument = minimalmodbus.Instrument(port, addr)
#        self.instrument.serial.baudrate = 115200
#        self.instrument.serial.parity = 'E'
#        self.instrument.serial.timeout = 0.1
#        self.velocity = 1000
#        self.acceleration = 2000
#        self.deceleration = 2000
#        self.operatingCurrent = 60
#

    def __init__(self, port, addr):
        self.instrument = minimalmodbus.Instrument(port, addr)
        self.instrument.serial.baudrate = 115200
        self.instrument.serial.parity = 'E'
        self.instrument.serial.timeout = 0.1
        self.velocity = 2500
        self.acceleration = 1000
        self.deceleration = 1000
        self.operatingCurrent = 60
        self.init_limit = 200
        self.set_init_limit()

    def home(self):
        self.instrument.write_register(0x7d, 0x10)
        self.instrument.write_register(0x7d,0)

    def stop(self):
        self.instrument.write_register(0x7d, 0x20)
        self.instrument.write_register(0x7d,0)

    def error(self):
        return self.instrument.read_register(0x80)

    def goto(self, pos):
        position = round(pos*RATIO_PULSE_MM)
        cmd = [0,0,0,1]
        cmd += dWord2List(position)
        cmd += dWord2List(self.velocity)
        cmd += dWord2List(self.acceleration)
        cmd += dWord2List(self.deceleration)
        cmd += dWord2List(self.operatingCurrent*10)
        cmd += dWord2List(1) #Trigger save all
        time.sleep(0.1)
        self.instrument.write_registers(0x58,cmd)

    def goto2(self, pos):
        self.goto(pos)
        self.get_status()
        while not self.inPos:
            self.get_status()

    def current_pos(self):
        high = self.instrument.read_register(0xcc)
        low = self.instrument.read_register(0xcd)
        self.pos = round((high<<16|low)/RATIO_PULSE_MM,2)
        return self.pos

    def reset_alarm(self):
        self.instrument.write_register(0x7d,0x80)
        self.instrument.write_registeR(0x7d,0)

    #Free Motor
    def motor_offline(self):
        self.instrument.write_register(0x7d, 0x40)

    #Resume Motor
    def motor_online(self):
        self.instrument.write_register(0x7d,0)

    def get_status(self):
        time.sleep(0.1)
        status = self.instrument.read_register(0x7f)
        self.home_end = (status & 0x10) == 0x10
        self.ready = (status & 0x20) == 0x20
        self.alarm = (status & 0x80) == 0x80
        self.moving = (status & 0x2000) == 0x2000
        self.inPos = (status & 0x4000) == 0x4000
        time.sleep(0.1)
        self.pos = self.current_pos()

    def is_ready(self):
        self.get_status()
        return self.ready

    def set_init_limit(self):
        self.instrument.write_registers(0x0284, [0, 0, 0, 30])

    def get_init_limit(self):
        #not working
        init_speed = self.instrument.read_registers(0x0284,4)
        print(init_speed)
        # return float('{0:0.3f}'.format(init_speed))

##Prerequisite
# python.exe -m pip install minimalmodbus

# ##Example
#import azd_cd as LM
#
#x_axis = LM.linearMotor("COM8", 1)
#y_axis = LM.linearMotor("COM8", 2)
#
#
#def move_xy(x,y):
#    x_axis.goto(x)
#    y_axis.goto(y)
#    moving = True
#    while (moving):
#        x_axis.get_status()
#        y_axis.get_status()
#        moving = not(x_axis.inPos and y_axis.inPos)
#
# #To set velocity/acceleration, this reflect upon next goto
#x_axis.acceleration = 1000
#x_axis.velocity = 500
#x_axis.deceleration = 1000
#
#
#
#
#print('connected succesfully')
#
##move_xy(30, 120)
#