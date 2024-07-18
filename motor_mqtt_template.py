import paho.mqtt.client as mqtt
import time

MQTT_BROKER_IP = '192.168.0.105'  # replace with your actual MQTT broker's IP

# Simulated functions for motor control and sensor reading
def move_motor_to_position(target_distance):
    # Simulate motor movement time
    print(f"Moving motor to {target_distance}...")
    time.sleep(2)  # Simulate the time taken to move the motor

def get_siko_distance():
    # Simulate reading the distance from the sensor
    return 100.0  # Replace with actual sensor reading logic

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("rail/target_position")

def on_message(client, userdata, msg):
    target_distance = float(msg.payload.decode("utf-8"))
    print(f"Received target distance: {target_distance}")

    # Move the motor to the target position
    move_motor_to_position(target_distance)

    # Update motor status to "stopped"
    client.publish("rail/motor_status", "stopped")

    # Get the siko distance
    siko_distance = get_siko_distance()

    # Publish the siko distance
    client.publish("rail/siko_distance", siko_distance)
    print(f"Published siko distance: {siko_distance}")

def run_motor_control():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER_IP, 1883, 60)
    client.loop_forever()

if __name__ == "__main__":
    run_motor_control()
