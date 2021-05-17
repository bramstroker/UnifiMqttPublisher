# UnifiMqttPublisher

This repository provides a docker image which publishes Unifi controller and access point statistics to a MQTT broker.
These messages can be picked up by home automation systems and allow you to present this information on you dashboard or make automations using this virtual sensor data.

## Prerequisites

You need the following:
- Working MQTT broker
- Unifi controller
- Some machine with docker installed (which is up 24/7)

## Installation

Go to the machine with docker where you want to run the publisher and make a new folder:

```sh
mkdir mqtt_unifi
cd mqtt_unifi
```

Copy the file `.env.example` to this directory and change the environment vars to match your situation.

Start the docker container:

`docker run -d --restart unless-stopped --env-file=.env bramgerritsen/unifi_mqtt_publisher:latest`

After the container is started you should see messages been published on topics `unifi/stats/controller` and `unifi/stats/ap0`. You can verify this by installing a MQTT client and subscribe to these topics.

## Example configuration Home Assistant

Add the following to you configuration yaml to get sensors in Home assistant
When you have multiple access points the topic is `unifi/stats/ap1` and for the third one `unifi/stats/ap2` vice versa. You can duplicate all entries for `unifi/stats/ap0` to also get these sensors.

```yaml
sensor:
  - platform: mqtt
    name: "Unifi controller"
    state_topic: "unifi/stats/controller"
    value_template: "{{ value_json.wlan_status }}"
    json_attributes_topic: "unifi/stats/controller"
  - platform: mqtt
    name: "Unifi controller - version"
    state_topic: "unifi/stats/controller"
    value_template: "{{ value_json.version }}"
  - platform: mqtt
    name: "Unifi controller - clients"
    state_topic: "unifi/stats/controller"
    value_template: "{{ value_json.num_clients }}"
  - platform: mqtt
    name: "Unifi controller - update available"
    state_topic: "unifi/stats/controller"
    value_template: "{{ value_json.update_available }}"
  - platform: mqtt
    name: "Unifi AP 1"
    state_topic: "unifi/stats/ap0"
    availability_topic: "unifi/availability/ap0"
    payload_available: "1"
    payload_not_available: "0"
    value_template: "{{ value_json.device_state }}"
    json_attributes_topic: "unifi/stats/ap0"
  - platform: mqtt
    name: "Unifi AP 1 - score"
    state_topic: "unifi/stats/ap0"
    value_template: "{{ value_json.satisfaction }}"
  - platform: mqtt
    name: "Unifi AP 1 - CPU"
    state_topic: "unifi/stats/ap0"
    value_template: "{{ value_json['system-stats']['cpu'] }}"
    icon: mdi:chip
  - platform: mqtt
    name: "Unifi AP 1 - RAM"
    state_topic: "unifi/stats/ap0"
    value_template: "{{ value_json['system-stats']['mem'] }}"
    icon: mdi:memory
  - platform: mqtt
    name: "Unifi AP 1 - uptime"
    state_topic: "unifi/stats/ap0"
    value_template: "{{ value_json['system-stats']['uptime'] }}"
    icon: mdi:clock-outline
```