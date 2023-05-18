#!/usr/bin/env python

from asyncio.tasks import sleep
from unificontrol import UnifiClient
import time
import paho.mqtt.client as mqtt
import json
import os

#### Env VARS ####
UNIFI_HOST = os.getenv('UNIFI_HOST')
UNIFI_USER = os.getenv('UNIFI_USER')
UNIFI_PASS = os.getenv('UNIFI_PASS')
UNIFI_SITE = os.getenv('UNIFI_SITE', 'default')
UNIFI_PORT = os.getenv('UNIFI_PORT', '8443')

MQTT_HOST = os.getenv('MQTT_HOST', 'hass.home')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')

POLL_FREQUENCY = int(os.getenv('POLL_FREQUENCY', 30))


class UnifiMqttPublisher:
    def __init__(self):
        self.mqttClient = mqtt.Client()
        self.mqttClient.username_pw_set(username=MQTT_USER, password=MQTT_PASS)
        self.mqttClient.connect(MQTT_HOST, 1883, 60)

        self.unifiClient = UnifiClient(host=UNIFI_HOST,username=UNIFI_USER,password=UNIFI_PASS,site=UNIFI_SITE,port=UNIFI_PORT)

    def run(self):
        while True:
            print('Publishing..')
            self.publish_controller_stats()
            self.publish_device_stats()
            time.sleep(POLL_FREQUENCY)

    def publish_device_stats(self) -> None:
        devs = self.unifiClient.list_devices()
        access_points = [dev for dev in devs if dev['type'] == 'uap']
        i = 0
        for ap in access_points:
            fields_to_include = {'ip', 'type', 'model', 'uptime', 'tx_bytes', 'rx_bytes', 'wan1', 'satisfaction',
                                 'system-stats', 'radio_table_stats'}
            payload = {k: ap[k] for k in ap.keys() & fields_to_include}
            payload['device_state'] = ap['state']
            self.mqttClient.publish('unifi/stats/ap' + str(i), payload=json.dumps(payload))
            self.mqttClient.publish('unifi/availability/ap' + str(i), payload=ap['state'])
            i = i + 1

    def publish_controller_stats(self) -> None:
        clients = self.unifiClient.list_clients()
        sysinfo = self.unifiClient.stat_sysinfo()
        health = self.unifiClient.list_health()

        controller_stats = sysinfo[0]
        fields_to_include = {'version', 'update_available', 'name'}
        payload = {k: controller_stats[k] for k in controller_stats.keys() & fields_to_include}
        payload['num_clients'] = len(clients)

        wlan_health = next((x for x in health if x['subsystem'] == 'wlan'), None)
        if wlan_health:
            payload['wlan_clients'] = wlan_health['num_user']
            payload['wlan_guests'] = wlan_health['num_guest']
            payload['wlan_status'] = wlan_health['status']
            payload['num_ap'] = wlan_health['num_ap']

        self.mqttClient.publish('unifi/stats/controller', payload=json.dumps(payload))


mqttPublisher = UnifiMqttPublisher()
mqttPublisher.run()
