# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:27:24 2023

@author: awer
"""
import paho.mqtt.client as mqtt
import threading
import time

MQTT_BROKER_IP = '192.168.0.105'  # replace with your actual MQTT broker's IP

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # subscribe to the topic on which the RPi is publishing the siko distance
    client.subscribe("rail/siko_distance")

def on_message(client, userdata, msg):
    # update the current siko distance and set the event to signal that the distance has been updated
    userdata['current_siko_distance'] = float(msg.payload.decode("utf-8"))
    userdata['distance_updated'].set()

def publish_target_position(client, target_distance):
    client.publish("rail/target_position", target_distance)

def get_siko_distance(target_distance, wait_time):
    userdata = {
        'current_siko_distance': None,
        'distance_updated': threading.Event(),
    }

    client = mqtt.Client(userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER_IP, 1883, 60)

    # start a separate thread to handle network events
    client_loop_thread = threading.Thread(target=client.loop_start)
    client_loop_thread.start()

    # publish the target distance and wait for the siko distance to be updated
    publish_target_position(client, target_distance)
    userdata['distance_updated'].wait(wait_time)

    # stop the client loop and return the current siko distance
    client.loop_stop()
    return userdata['current_siko_distance'] 



target_distance = 0  # replace with your actual target distance
wait_time = 5  # replace with your actual wait time (in seconds)

siko_distance = get_siko_distance(target_distance, wait_time)
print("Siko distance:", siko_distance) 
