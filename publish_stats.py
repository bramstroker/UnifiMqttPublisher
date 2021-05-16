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

POLL_FREQUENCY = os.getenv('POLL_FREQUENCY', 30)

class UnifiMqttPublisher:
    def __init__(self):
        self.mqttClient = mqtt.Client()
        self.mqttClient.username_pw_set(username=MQTT_USER, password=MQTT_PASS)
        self.mqttClient.connect(MQTT_HOST, 1883, 60)

        self.unifiClient = UnifiClient(host=UNIFI_HOST,username=UNIFI_USER,password=UNIFI_PASS,site=UNIFI_SITE,port=UNIFI_PORT)

    def run(self):
        while (True):
            print('Publishing..')
            self.publishControllerStats()
            self.publishDeviceStats()
            time.sleep(POLL_FREQUENCY)

    def publishDeviceStats(self):
        devs = self.unifiClient.list_devices()
        i = 0
        for dev in devs:
            fieldsToInclude = set([
                'ip',
                'type',
                'model',
                'uptime',
                'tx_bytes',
                'rx_bytes',
                'state',
                'satisfaction',
                'system-stats',
                'radio_table_stats'
            ])
            payload = {k: dev[k] for k in dev.keys() & fieldsToInclude}
            #print(payload)
            self.mqttClient.publish('unifi/stats/ap' + str(i), payload=json.dumps(payload))
            self.mqttClient.publish('unifi/availability/ap' + str(i), payload=dev['state'])
            i = i + 1

    def publishControllerStats(self):
        clients = self.unifiClient.list_clients()
        sysinfo = self.unifiClient.stat_sysinfo()
        health = self.unifiClient.list_health()

        controllerStats = sysinfo[0]
        fieldsToInclude = set([
            'version',
            'update_available',
            'name'
        ])
        payload = {k: controllerStats[k] for k in controllerStats.keys() & fieldsToInclude}
        payload['num_clients'] = len(clients)

        wlanHealth = next((x for x in health if x['subsystem'] == 'wlan'), None)
        if (wlanHealth):
            payload['wlan_clients'] = wlanHealth['num_user']
            payload['wlan_guests'] = wlanHealth['num_guest']
            payload['wlan_status'] = wlanHealth['status']
            payload['num_ap'] = wlanHealth['num_ap']

        #print(payload)
        self.mqttClient.publish('unifi/stats/controller', payload=json.dumps(payload))

mqttPublisher = UnifiMqttPublisher()
mqttPublisher.run()
