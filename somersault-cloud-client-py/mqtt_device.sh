#!/bin/bash

SHELL_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Using SHELL_DIR= ${SHELL_DIR}"
BASE_DIR="$(cd "$SHELL_DIR/.." && pwd)"
echo "Using BASE_DIR= ${BASE_DIR}"

pip3 install -i https://mirrors.aliyun.com/pypi/simple paho.mqtt
pip3 install -i https://mirrors.aliyun.com/pypi/simple gpiozero

cd "${SHELL_DIR}"
echo "Startup mqtt_device.py ang log to mqtt_device.log..."
# python3 mqtt_device.py -s \[240e:330:132:fc00:6614:bb8a:17ec:264f\]:8888 -d WUGUI01
# python3 mqtt_device.py -s 192.168.1.200:48080 -d WUGUI01
nohup python3 -u mqtt_device.py -s 124.71.2.242:8888 -d WUGUI01 >> mqtt_device.log 2>&1 &
echo "Show logs using: tail -f mqtt_device.log"
tail -f mqtt_device.log