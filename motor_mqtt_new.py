import paho.mqtt.client as mqtt
import threading
import time
from motor_control import linearMotor
from siko import siko_dist

COM_PORT = '/dev/serial/by-id/usb-FTDI_USB-RS485_Cable_FT0HBZB9-if00-port0'
ADDR = 3
MQTT_BROKER_IP = '192.168.0.105'

# Initialize motor, replace 'COM_PORT' with your actual COM port, and 'ADDR' with your device address       
motor = linearMotor(COM_PORT, ADDR)
TOLERANCE = 0.06  # Define a tolerance for considering the target reached

# Shared state
latest_command = {
    'type': None,
    'value': None
}
lock = threading.Lock()

# Simulated functions for motor control and sensor reading
def move_motor_by_distance(distance_to_move):
    # Simulate non-blocking motor movement
    print(f"Moving motor by {distance_to_move} units...")
    motor.goto(motor.current_pos() - distance_to_move)

def stop_motor():
    # Placeholder function to stop the motor
    print("Stopping the motor...")
    motor.stop()

def get_siko_distance():
    # Simulate reading the distance from the sensor
    return siko_dist()

def check_motor_stopped():
    # Simulate checking if the motor has stopped
    # This should return True if the motor has reached its target and stopped
    return motor.is_ready()  # Replace with actual logic to check motor status

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("rail/target_position")

def on_message(client, userdata, msg):
    global latest_command
    command = msg.payload.decode("utf-8")
    print(f"Received command: {command}")

    with lock:
        if command == "STOP":
            latest_command['type'] = "STOP"
            latest_command['value'] = None
        else:
            latest_command['type'] = "MOVE"
            latest_command['value'] = float(command)

def handle_motor_movement(client):
    global latest_command

    current_target = None

    while True:
        with lock:
            command_type = latest_command['type']
            command_value = latest_command['value']
            latest_command['type'] = None
            latest_command['value'] = None

        if command_type == "MOVE":
            current_target = command_value
            current_distance = get_siko_distance()
            distance_to_move = current_target - current_distance
            move_motor_by_distance(distance_to_move)

        elif command_type == "STOP":
            print("Received stop command. Stopping motor.")
            stop_motor()
            current_target = None

        if current_target is not None:
            # Periodically check if the motor has stopped
            if check_motor_stopped():
                # Get the updated siko distance
                siko_distance = get_siko_distance()
                # Publish the siko distance
                client.publish("rail/siko_distance", siko_distance)
                print(f"Published siko distance: {siko_distance}")

                if abs(siko_distance - current_target) <= TOLERANCE:
                    print("Motor has reached the target within tolerance.")
                    client.publish("rail/motor_status", "stopped")
                    current_target = None
                else:
                    # Adjust the motor position again if it's not within tolerance
                    distance_to_move = current_target - siko_distance
                    move_motor_by_distance(distance_to_move)

        time.sleep(0.1)  # Adjust sleep time as needed to avoid busy-waiting

def run_motor_control():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER_IP, 1883, 60)
    client.loop_start()

    # Start a thread to handle motor movement
    motor_thread = threading.Thread(target=handle_motor_movement, args=(client,))
    motor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    client.loop_stop()
    motor_thread.join()

if __name__ == "__main__":
    run_motor_control()