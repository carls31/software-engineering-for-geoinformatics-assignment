netsh interface ipv4 set address name="Wi-Fi" static 192.168.30.19 255.255.255.0 192.168.30.135
netsh interface ipv4 set dns name="Wi-Fi" static 192.168.30.135
netsh interface ipv4 set dns name="Wi-Fi" static 8.8.8.8 index=2


