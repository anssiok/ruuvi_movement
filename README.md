# ruuvi_movement
Simple movement detector using Ruuvitags and ruuvitag_sensor Python package.
## Installation example for Debian Linux / Raspberry Pi
### Python packages 
```
sudo apt-get install python3-pip
sudo pip3 install ruuvitag_sensor requests configparser datetime
```
### ruuvi_movement
```
sudo mkdir /opt/ruuvi
sudo cp ruuvi_movement.py /opt/ruuvi/
sudo cp ruuvi_movement.ini.sample /opt/ruuvi/ruuvi_movement.ini
sudo cp ruuvi_movement.service /etc/systemd/system/
```
Edit /opt/ruuvi/ruuvi_movement.ini to suit yuor needs.
### System service
```
sudo systemctl daemon-reload
sudo systemctl start ruuvi_movement
sudo systemctl enable ruuvi_movement
```
