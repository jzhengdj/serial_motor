import paho.mqtt.client as mqtt
from motor_control import linearMotor
from siko import siko_dist
import time
import threading

COM_PORT = '/dev/serial/by-id/usb-FTDI_USB-RS485_Cable_FT0HBZB9-if00-port0'
ADDR = 3
MQTT_BROKER_IP = '192.168.0.105'

# Initialize motor, replace 'COM_PORT' with your actual COM port, and 'ADDR' with your device address       
motor = linearMotor(COM_PORT, ADDR)

# Create a lock for both motor and siko
motor_siko_lock = threading.Lock()

def move_to_target(target_position, tolerance=0.06):
    while True:
        with motor_siko_lock:
            diff = target_position - siko_dist()

        if abs(diff) <= tolerance:
            break

        with motor_siko_lock:
            motor.goto2(motor.current_pos() - diff)

    print("Current siko position: ", siko_dist())
    return siko_dist()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("rail/target_position")

def on_message(client, userdata, msg):
    target_position = float(msg.payload.decode("utf-8"))
    print("Received target_position:", target_position)
    Current_pos = move_to_target(target_position)

    return Current_pos

def publish_motor_status(client, interval=1):
    while True:
        time.sleep(interval)

        with motor_siko_lock:
            is_ready = motor.is_ready()
            current_siko_distance = siko_dist()

        if is_ready:
            status = "stopped"
            client.publish("rail/motor_status", status)
            client.publish("rail/siko_distance", current_siko_distance)

        else:
            status = "moving"
            client.publish("rail/motor_status", status)





client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Replace 'MQTT_BROKER_IP' with your actual MQTT broker's IP address or hostname
client.connect(MQTT_BROKER_IP, 1883, 60)

# Start a separate thread to publish motor status and siko distance
motor_status_thread = threading.Thread(target=publish_motor_status, args=(client,))
motor_status_thread.start()

client.loop_forever()