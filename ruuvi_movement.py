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
notification_hours = config.get('General', 'notification_hours')
hour_begin = int(notification_hours.split('-')[0])
hour_end = int(notification_hours.split('-')[1])

macs = []
names = []
timers = []
move_counts = []
for tag in config.items('Tags'):
    print(tag)
    names.append(tag[0])
    macs.append(tag[1])
    move_counts.append(-1)
    timers.append(0)

listen_macs = []
for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])
    
print('Listen: ' + str(listen_macs))

def in_schedule():
    hour_now = datetime.now().hour
    if hour_begin <= hour_end:
        return hour_begin <= hour_now < hour_end
    return hour_begin <= hour_now or hour_now < hour_end

def send_alert(msg, force_alert = False):
    print(msg)
    if force_alert or in_schedule():
        print("in schedule or forced, alerting")
        response = requests.post(
            webhook,
            headers={'Content-type': 'application/json'},
            data='{"text":\'' + msg + '\'}'
        )
    else:
        print("not in schedule")

# Handle timeouts
def timer_handler(signum, frame):
    for idx, mac in enumerate(macs):
        if mac in listen_macs:
#            if timers[idx] == 0:
#                print ('Already at timeout: ' + names[idx])
#            el
            if timers[idx] != 0:
                if (datetime.now() - timers[idx]).total_seconds() > tag_timeout:
                    send_alert('No connection: ' + names[idx], True)
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
    if timers[idx] == 0:
        send_alert('Connection resumed: ' + names[idx], True)
    timers[idx] = datetime.now()
#    print (
#        datetime.now().strftime("%F %H:%M:%S") +
#        ' mac: ' + str(found_data[1]['mac']) +
#        ' battery: ' + str(found_data[1]['battery']) +
#        ' movement_counter: ' + str(found_data[1]['movement_counter'])
#    )
    if move_count != -1 and move_count != found_data[1]['movement_counter']:
        send_alert(found_name + ' is moving!')
    move_counts[idx] = found_data[1]["movement_counter"]

# Get the data
RuuviTagSensor.get_datas(handle_data, listen_macs)
print('Exiting now')
