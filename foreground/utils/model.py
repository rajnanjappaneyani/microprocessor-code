# utils/model.py
import sys
import time

user_input = input()  # waits for "start\n" from Rust
print(f"model.py received input: {user_input}", flush=True)

for i in range(20):
    print(f"model stream {i}", flush=True)
    time.sleep(0.2)
