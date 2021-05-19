#!/usr/bin/python3
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import requests, configparser, signal
from datetime import datetime

# read config
config = configparser.ConfigParser()
config.read(['ruuvi_movement.ini','/opt/ruuvi/ruuvi_movement.ini'])

listen = config.get('General', 'listen')
webhook = config.get('General', 'webhook')
tag_timeout = int(config.get('General', 'tag_timeout'))
timeout_check_interval = int(config.get('General', 'timeout_check_interval'))

macs = []
names = []
timers = []
move_counts = []
for tag in config.items('Tags'):
    print(tag)
    names.append(tag[0])
    macs.append(tag[1])
    move_counts.append(-1)
    timers.append(datetime.now())

listen_macs = []
for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])
    
print('Listen: ' + str(listen_macs))

# Handle timeouts
def timer_handler(signum, frame):
    for idx, mac in enumerate(macs):
        if mac in listen_macs:
#            if timers[idx] == 0:
#                print ('Already at timeout: ' + names[idx])
#            el
            if timers[idx] != 0:
                if (datetime.now() - timers[idx]).total_seconds() > tag_timeout:
                    msg = 'Ei yhteyttä: ' + names[idx]
                    print(msg)
                    response = requests.post(
                        webhook,
                        headers={'Content-type': 'application/json'},
                        data='{"text":\'' + msg + '\'}'
                    )
                    timers[idx] = 0
#                else:
#                    print('No timeout: ' + names[idx])
    signal.alarm(timeout_check_interval)

signal.signal(signal.SIGALRM, timer_handler)
signal.alarm(timeout_check_interval)

# Handle data reception
def handle_data(found_data):
    global move_counts
    found_mac = found_data[0]
    idx = macs.index(found_mac)
    found_name = names[idx]
    move_count = move_counts[idx]
#    print (
#        datetime.now().strftime("%F %H:%M:%S") +
#        ' mac: ' + str(found_data[1]['mac']) +
#        ' battery: ' + str(found_data[1]['battery']) +
#        ' movement_counter: ' + str(found_data[1]['movement_counter'])
#    )
    if move_count != -1 and move_count != found_data[1]['movement_counter']:
        msg = found_name + ' liikkuu!'
        print(msg)
        response = requests.post(
            webhook, headers={'Content-type': 'application/json'}, data='{"text":\''+msg+'\'}'
        )
    move_counts[idx] = found_data[1]["movement_counter"]
    timers[idx] = datetime.now()

# Get the data
RuuviTagSensor.get_datas(handle_data, listen_macs)
print('Exiting now')
