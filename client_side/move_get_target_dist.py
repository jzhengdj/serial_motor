import paho.mqtt.client as mqtt
import threading
import time

MQTT_BROKER_IP = '192.168.0.105'  # replace with your actual MQTT broker's IP

# Define the MQTT client and related functions
class MQTTClientWrapper:
    def __init__(self, broker_ip):
        self.userdata = {
            'current_siko_distance': None,
            'distance_updated': threading.Event(),
            'motor_status': None,
            'motor_stopped': threading.Event()
        }

        self.client = mqtt.Client(userdata=self.userdata)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(broker_ip, 1883, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("rail/siko_distance")
        client.subscribe("rail/motor_status")

    def on_message(self, client, userdata, msg):
        if msg.topic == "rail/siko_distance":
            userdata['current_siko_distance'] = float(msg.payload.decode("utf-8"))
            userdata['distance_updated'].set()
        elif msg.topic == "rail/motor_status":
            userdata['motor_status'] = msg.payload.decode("utf-8")
            if userdata['motor_status'] == "stopped":
                userdata['motor_stopped'].set()

    def publish_target_position(self, target_distance):
        self.client.publish("rail/target_position", target_distance)

    def wait_for_siko_distance(self, wait_time):
        # Wait for the motor to stop
        motor_stopped = self.userdata['motor_stopped'].wait(wait_time)

        if not motor_stopped:
            print("Motor did not stop within the timeout period.")
            return None

        # Wait for the sensor to stabilize
        sensor_stabilized = self.userdata['distance_updated'].wait(wait_time)
        return self.userdata['current_siko_distance'] if sensor_stabilized else None

# Instantiate the MQTT client wrapper
mqtt_client = MQTTClientWrapper(MQTT_BROKER_IP)

# Example usage
target_distance = 200  # replace with your actual target distance
wait_time = 5  # replace with your actual wait time (in seconds)

# Publish the target position
mqtt_client.publish_target_position(target_distance)

# Call the wait_for_siko_distance function to get the siko distance
for _ in range(5):
    siko_distance = mqtt_client.wait_for_siko_distance(wait_time)
    print("Siko distance:", siko_distance)
    time.sleep(2)  # Adjust sleep time as needed