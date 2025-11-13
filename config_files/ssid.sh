sudo nmcli connection add type wifi ifname wlan0 con-name evrenwireless24 ssid evrenwireless24
sudo nmcli connection modify evrenwireless24 wifi-sec.key-mgmt wpa-psk wifi-sec.psk Ek112122
sudo nmcli connection modify evrenwireless24 connection.autoconnect yes

sudo nmcli connection add type wifi ifname wlan0 con-name evrenwireless ssid evrenwireless
sudo nmcli connection modify evrenwireless wifi-sec.key-mgmt wpa-psk wifi-sec.psk Ek112122
sudo nmcli connection modify evrenwireless connection.autoconnect yes

sudo nmcli connection add type wifi ifname wlan0 con-name TRUSTBT ssid TRUSTBT
sudo nmcli connection modify TRUSTBT wifi-sec.key-mgmt wpa-psk wifi-sec.psk Trust@2021
sudo nmcli connection modify TRUSTBT connection.autoconnect yes


sudo nmcli connection add type wifi ifname wlan0 con-name SUPERBOX_Wi-Fi_7EBF ssid SUPERBOX_Wi-Fi_7EBF
sudo nmcli connection modify SUPERBOX_Wi-Fi_7EBF wifi-sec.key-mgmt wpa-psk wifi-sec.psk 9C4D935DBF
sudo nmcli connection modify SUPERBOX_Wi-Fi_7EBF connection.autoconnect yes

sudo nmcli connection add type wifi ifname wlan0 con-name Evrennnn ssid Evrennnn
sudo nmcli connection modify Evrennnn wifi-sec.key-mgmt wpa-psk wifi-sec.psk Ek112122
sudo nmcli connection modify Evrennnn connection.autoconnect yes
