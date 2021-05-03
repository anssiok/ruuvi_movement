#!/usr/bin/python3
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import requests, configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('ruuvi_movement.ini')

listen=config.get('General', 'listen')
webhook=config.get('General', 'webhook')

macs = []
listen_macs = []
names = []
move_count = -1

for tag in config.items('Tags'):
    print(tag)
    names.append(tag[0])
    macs.append(tag[1])

for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])
    
print('Listen: ' + str(listen_macs))

def handle_data(found_data):
    global move_count
    found_mac = found_data[0]
    found_name = names[macs.index(found_mac)]
    print (
        datetime.now().strftime("%F %H:%M:%S") +
        ' mac: ' + str(found_data[1]['mac']) +
        ' battery: ' + str(found_data[1]['battery']) +
        ' movement_counter: ' + str(found_data[1]['movement_counter'])
    )
    if move_count != -1 and move_count != found_data[1]['movement_counter']:
        msg = found_name + ' liikkuu!'
        print(msg)
        response = requests.post(
            webhook, headers={'Content-type': 'application/json'}, data='{"text":\''+msg+'\'}'
        )
    move_count = found_data[1]["movement_counter"]

RuuviTagSensor.get_datas(handle_data, listen_macs)
print('done')
