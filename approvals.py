#!/usr/bin/env python
# A quick script to automate approval file wrangling
import fnmatch
import os
import subprocess

pending_approvals = []
for root, dirnames, filenames in os.walk('sana_pchr'):
    for filename in fnmatch.filter(filenames, '*.received.*'):
        pending_approvals.append(os.path.join(root, filename))

for pending_approval_path in pending_approvals:
    received_path = pending_approval_path
    approved_path = pending_approval_path.replace(".received.", ".approved.")

    print(os.path.basename(pending_approval_path))
    if os.path.exists(approved_path):
        subprocess.call(["diff", approved_path, received_path])
    else:
        try:
            print(open(received_path, "r").read())
        except UnicodeDecodeError:
            print("Binary file")

    res = input("Approve? (y/n):")
    if res == 'y':
        if os.path.exists(approved_path):
            os.remove(approved_path)
        os.rename(received_path, approved_path)
