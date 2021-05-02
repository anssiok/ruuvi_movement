#!/usr/bin/python3
from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
import requests

tags = [
    { 'mac': 'FA:E0:D7:09:77:42', 'name': 'Aquarium' },
    { 'mac': 'F5:A2:32:52:CC:7F', 'name': 'GreenTag' },
    { 'mac': 'C5:75:90:8A:30:9F', 'name': 'tag01' },
    { 'mac': 'C7:91:70:43:5B:52', 'name': 'tag02' },
    { 'mac': 'FB:D8:55:BE:DC:9A', 'name': 'tag03' },
    { 'mac': 'DD:E5:D1:E6:2F:74', 'name': 'tag04' },
    { 'mac': 'CD:04:2A:92:2A:DD', 'name': 'tag05' },
    { 'mac': 'EE:7B:38:67:AE:6B', 'name': 'tag06' },
    { 'mac': 'F5:54:58:2D:F0:13', 'name': 'tag07' }
]

counter = 10
move_count = -1
# RunFlag for stopping execution at desired time
run_flag = RunFlag()

def get_tag(tag_name_or_mac):
    for index, item in enumerate(tags):
        if item['name'] == tag_name_or_mac or item['mac'] == tag_name_or_mac:
            return item

def handle_data(found_data):
    global move_count, counter
    found_mac = found_data[0]
    found_name = get_tag(found_mac)['name']
    if move_count != -1 and move_count != found_data[1]["movement_counter"]:
        msg = found_name + ' liikkuu!'
        print(msg)
        response = requests.post(
            'https://hooks.slack.com/services/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',
            headers={'Content-type': 'application/json'},
            data='{"text":\''+msg+'\'}'
        )
    move_count = found_data[1]["movement_counter"]
    print('MAC ' + found_mac)
    print('acceleration:' + str(found_data[1]["acceleration"]))
    print('movement_counter:' + str(found_data[1]["movement_counter"]))

    counter = counter - 1
    if counter < 0:
        run_flag.running = False

# List of macs of sensors which will execute callback function
listen_macs = [get_tag('tag01')['mac']]

RuuviTagSensor.get_datas(handle_data, listen_macs, run_flag)
