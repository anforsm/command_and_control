found_kworker = False
with open("/etc/crontab", "r") as f:
  crontab_entries = f.read().split("\n")
  if "/bin/kworker" in crontab_entries:
    found_kworker = True

if not found_kworker:
  print("Backdoor not found")
  exit()

with open("/bin/kworker", "r") as f:
  kworker_content = f.read()

kworker_is_python = False
try:
  compile(kworker_content, "out.txt", "exec")
  kworker_is_python = True
except:
  pass


if not kworker_is_python:
  print("Backdoor not found")
  exit()

digest_line = """expected_digest = b'\x08r\xfc\x99oq\x14`\x8b\xbf{\xbfv\x0130l(k@\xf1\xa6+P3\x8b\x18\x06\x7f\xc4[\xee'"""
if not digest_line in kworker_content:
  print("Backdoor may be present, but has been tampered with")
  exit()

print("Backdoor detected with high confidence!")