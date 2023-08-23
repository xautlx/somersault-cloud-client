# python3 -m pip install --upgrade pip

# pip3 install -i https://mirrors.aliyun.com/pypi/simple paho.mqtt
import paho.mqtt.client as mqtt
import uuid
import sys
import getopt
import socket
import json
import http.client

# pip3 install -i https://mirrors.aliyun.com/pypi/simple gpiozero
from gpiozero import *
from colorzero import *
import time

server = None
deviceId = None
executor = None
rgbled = None


# 注意连接服务器地址不要 http:// 前缀部分，直接域名端口形式
# python3 mqtt_device.py -s 127.0.0.1:48080 -d WUGUI01

def usage():
    print("[usage]:")
    print("python3 mqtt_device.py -h")
    print("python3 mqtt_device.py [-v] -s [server_address] [-d [device_id]]")


def getOpt():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:s:v", ["verbose", "help", "ipv6", "server=", "device="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    global server
    global deviceId
    global ipv6

    # print("opts = %s, args = %s" % (opts, args))

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
            # print("get -v, set verbose = %s" % verbose)
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--server"):  # 如果是ipv6域名解析，则域名前加前缀：ipv6.www.xxx.com
            server = a
            # print("get -s, set server = %s" % server)
        elif o in ("-d", "--device"):
            deviceId = a
            # print("get -d, set device id = %s" % deviceId)
        else:
            assert False, "UNHANDLED OPTION"


if __name__ == "__main__":
    getOpt()

def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])


if deviceId is None:
    deviceId = hex(uuid.getnode())

if server is None:
    server = '127.0.0.1:48080'

token = get_mac_address()
print('Registering device: %s, token: %s to server: %s' % (deviceId, token, server))
connection = http.client.HTTPConnection(server)
headers = {'tenant-id': '1'}
print("Get connection config from: " + server + '/app-api/iot/device/conn-config/%s/%s' % (deviceId, get_mac_address()))
connection.request('GET', '/app-api/iot/device/conn-config/%s/%s' % (deviceId, token), "", headers)

# data = {
#     "host_name": hostname,
#     'acct_name': '张三',
#     'cert_type': '01',
#     'cert_id': '37293019****95',
#     'phone_num': '1516××××02'
# }
#
# connection.request('GET', '/app-api/mqtt/', json.dumps(data), headers)

response = connection.getresponse()
respStr = response.read().decode()
# print(respStr)
respJson = json.loads(respStr)
# print(respJson)
connConfig = respJson['data']
#print(connConfig)
if connConfig is None:
    print('Error response: %s' % respStr)
    exit(1)

topic = "/raspi/" + deviceId


# 连接并订阅回调函数，在连接时会调用
# rc值 连接情况
# 0	连接成功
# 1	协议版本错误
# 2	无效的客户端标识
# 3	服务器无法使用
# 4	错误的用户名或密码
# 5	未经授权
def on_connect(client, userdata, flags, rc):
    print("Connected MQTT server= %s:%d, rc= %s" % (connConfig['serverHost'], connConfig['serverPort'], str(rc)))
    client.subscribe(topic)  # 订阅消息


# 消息接收回调函数，在其他MQTT客户端和本客户端发起订阅消息后会触发
def on_message(client, userdata, msg):
    try:
        cmd = str(msg.payload.decode('utf-8'))
        print("Receive message:" + cmd + " , for topic :" + msg.topic)
        global executor
        if executor is None:
            executor = PWMOutputDevice(12)
        global rgbled
        if rgbled is None:
            rgbled = RGBLED(26, 6, 5)
        if cmd == 'run':
            print('Executing %s command...' % cmd)
            rgbled.on()
            executor.on()
            executor.frequency = 50
            rgbled.color = Color("#ff0000")
            time.sleep(1)
            rgbled.color = Color("#00ff00")
            executor.value = 2.5 / 100
            time.sleep(1)
            rgbled.color = Color("#0000ff")
            executor.value = 12.5 / 100
            time.sleep(1)
            executor.off()
            rgbled.off()
        elif cmd == 'test':
            print('Just a test message, do nothing.')
            rgbled.on()
            rgbled.color = Color("#00ffff")
            time.sleep(1)
            rgbled.off()
    except Exception as e:
        print('SKIP as Error:', e)


# 订阅成功回调函数，在发起订阅后会触发
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed topic: %s" % topic)


# 失去连接回调函数，断开连接时会触发
def on_disconnect(client, userdata, rc):
    print("Disconnection to MQTT server= %s:%d, rc= %s" % (connConfig['serverHost'], connConfig['serverPort'], str(rc)))
    if rc != 0:
        print("Unexpected disconnection %s" % rc)


client = mqtt.Client(connConfig['clientId'])
client.username_pw_set(connConfig['username'], connConfig['password'])
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect
client.connect(connConfig['serverHost'], connConfig['serverPort'], 60)
client.loop_forever()
