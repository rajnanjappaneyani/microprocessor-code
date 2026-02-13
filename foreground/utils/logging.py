# utils/logging.py
import sys
import time

user_input = input()  # waits for "start\n" from Rust
print(f"logging.py received input: {user_input}", flush=True)

for i in range(20):
    print(f"logging stream {i}", flush=True)
    time.sleep(0.35)
