# check if the script is running, if not, run it
ps aux | grep "python3 [c]lient.py"
if [ $? -ne 0 ]; then
    cd /home/user/c_and_c/
    python3 client.py
fi