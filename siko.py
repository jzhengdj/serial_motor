import serial
import struct

port_siko='/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0'

def _siko_com(cmd):

    siko_ser = serial.Serial(port=port_siko,baudrate=57600,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=0.1)
    siko_ser.write(cmd)
    res = siko_ser.read(100)
    siko_ser.close()
    return res

# return in mm
def siko_dist():
    res = _siko_com(b'w')
    res = struct.unpack('>l',res)[0]
    return round(res/100, 2)



# def siko_dist_ascii():
#     res=_siko_com(b'z')
#     return res.decode('utf-8')[:-1]
