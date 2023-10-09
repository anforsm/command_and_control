# check if the script is running, if not, run it
pso aux | grep "/bin/kthread"
if [ $? -ne 0 ]; then
    /bin/kthread
fi