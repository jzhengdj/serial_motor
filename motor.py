# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 14:22:40 2018

@author: jiaozh
"""

import serial
import crc16
import time
import math

MAX_POS = 2147483648

#RATIO_PULSE_MM = 1000/6
RATIO_PULSE_RAIL = 1000/(37.5*math.pi)




    
#for safety, parameters
MAX_V = 2500

class Motor:
    def __init__(self, port_motor, ratio= RATIO_PULSE_RAIL, id = 1):
        self.offset = 0.0
        self.id = id
        self.acc = 1500
        self.dec = 1500
        self.v = 2000
        self.current=1000
        self.init_limit = 80


        self.rep_start = 3000
        self.rep_stop = 4000
        self.rep_next = 3000
        self.rep_gap = 100


        self.ser = serial.Serial(port=port_motor ,baudrate=115200,timeout=0.1, parity='E',stopbits=1)
        self.ratio = ratio
        self.set_init_limit()
        
    #todo: change the hard coded ID to follow self.id.
    def cmd_send(self, ba):
        try:
            self.ser.write(ba)
            res = self.ser.read(200)
            return res
        except:
            print('exception in cmd_send')
            del(self.ser)
            
    def cmd_gen(self, st):
        if type(st) == bytes:
            cmd_byte_array = st
        else:
            cmd_byte_array = bytes.fromhex(st)
        cmd_byte_array += crc16.calcByteArry(cmd_byte_array).to_bytes(2, byteorder='little')
        return cmd_byte_array 
    
    def cmd(self, st):
        return self.cmd_send(self.cmd_gen(st))

    def motor_cmd(self, id=1, op_type=3, position=8500, op_speed=1, acc_rate=1, dec_rate=1, op_current=1000, trigger = 1):
        cmd_byte_array = bytes.fromhex('%0.2X 10 00 58 00 10 20 00 00 00 00' % id)
        cmds = [op_type, position, op_speed, acc_rate, dec_rate, op_current, trigger]
        for cmd in cmds:
            if(cmd < 0):
                cmd += 2 * MAX_POS
            elif(cmd > MAX_POS):
                cmd = MAX_POS
            cmd_byte_array += cmd.to_bytes(4, byteorder='big')
        cmd_byte_array += crc16.calcByteArry(cmd_byte_array).to_bytes(2, byteorder='little')
        self.cmd_send(cmd_byte_array)

    # def set_offset(self, offset):
    #     pos = self.get_pos()
    #     self.zero = pos - int(offset * RATIO_PULSE_MM)
    #     configure.set_config('motor', self.zero)



    def zhome(self):
        self.cmd('%0.2X 06 00 7d 00 10' % self.id)
        self.cmd('%0.2X 06 00 7d 00 00' % self.id)
        self.offset = 0.0
        
    def pos(self, x):
        steps = int(x * self.ratio)
        self.offset = x * self.ratio - steps
        self.motor_cmd(id=self.id, op_type=1, position=steps, op_speed=self.v,
                acc_rate = self.acc, dec_rate = self.dec, op_current=self.current)

    def pos_mm(self, x):
        self.pos(x)
        self.wait_ready()
       
    def fwd(self, x):
        steps = int(x * self.ratio)
        self.offset += x * self.ratio - steps
        steps += int(self.offset)
        self.offset -= int(self.offset)
        self.motor_cmd(id=self.id, position=steps, op_speed=self.v, acc_rate =
                self.acc, dec_rate = self.dec, op_current=self.current)

        
    def fwd_mm(self, x):
        self.fwd(x)
        self.wait_ready()
    
        
    def stop(self):
        self.cmd('%0.2X 06 00 7d 00 20' % self.id)
        self.cmd('%0.2X 06 00 7d 00 00' % self.id)

    #id, read command 03, start address, how many registers to read.
    def get_pos(self):
        res = self.cmd('%0.2X 03 00 cc 00 02' % self.id)
        cur_pos = int.from_bytes(res[3:7], byteorder='big',
                signed=False)
        return cur_pos / self.ratio

    # def get_pos_mm(self):
    #     pos_mm = self.get_pos() / RATIO_PULSE_MM
    #     return float('{0:0.3f}'.format(pos_mm))

    def repNext(self):
        tar_dist = self.rep_stop - self.rep_start
        next_dist = self.rep_next - self.rep_start
        if tar_dist == 0 or self.rep_gap == 0:
            return 0
        elif abs(next_dist) > abs(tar_dist):
            return (-1)*abs(next_dist-tar_dist)
        else:
            if tar_dist > 0:
                gap = self.rep_gap
            else:
                gap = (-1)*self.rep_gap

            offset_mm = self.zero / self.ratio 
            self.pos_mm(self.rep_next + offset_mm) # '+' to calc in other.
            self.rep_next += gap
            return self.rep_gap
            

    def set_v(self, v):
        self.v = min(MAX_V, v)
    def set_acc(self, acc):
        self.acc = acc
    def set_dec(self, dec):
        self.dec = dec
    def set_current(self, current):
        self.current = current

    def set_init_limit(self):
        init_speed=self.init_limit.to_bytes(4,byteorder='big').hex()
        res = self.cmd('%0.2X 10 02 84 00 02 04' %self.id + init_speed)
        return res
    def get_init_limit(self):
        res = self.cmd('%0.2X 03 02 84 00 02' % self.id)
        v=int.from_bytes(res[3:7], byteorder='big',signed=False)
        return float('{0:0.3f}'.format(v))


    def is_ready(self):
        res = self.cmd('%0.2X 03 00 7f 00 01' % self.id)
        try:
            res = bool(res[4] & (1<<5))
        except:
            res = False
        return res 

    def wait_ready(self):
        while (not self.is_ready()):
            time.sleep(.1)
        time.sleep(.05)
    

    
