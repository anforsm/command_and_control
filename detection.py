found_kworker = False
try:
  with open("/var/spool/cron/root", "r") as f:
    crontab_entries = f.read()
    if "/bin/kworker" in crontab_entries:
      found_kworker = True
except:
  print("Could not find crontab file. Exiting...")
  exit()

if not found_kworker:
  print("Backdoor not found")
  exit()

try:
  with open("/bin/kthread", "r") as f:
    kthread_content = f.read()
except:
  print("Backdoor may be present, but has been tampered with")
  exit()


digest_line = r"""expected_digest = b'\x08r\xfc\x99oq\x14`\x8b\xbf{\xbfv\x0130l(k@\xf1\xa6+P3\x8b\x18\x06\x7f\xc4[\xee'"""
if not digest_line in kthread_content:
  print("Backdoor may be present, but has been tampered with")
  exit()

print("Backdoor detected with high confidence!")