import json
import time
import os

from user import User

QUEUE = "firewall_to_server.json"

user = User("Ali", "192.168.1.100")

print("Server is running...")
print(f"User: {user.username}")
print(f"IP: {user.ip}")
print(f"Status: {user.status}")

while True:
    if os.path.exists(QUEUE):
        try:
            with open(QUEUE, "r") as file:
                packets = json.load(file)

            if packets:
                packet = packets.pop(0)

                with open(QUEUE, "w") as file:
                    json.dump(packets, file)

                print(
                    f"[SERVER] Received "
                    f"{packet['type']} from {packet['src']}"
                )

        except (json.JSONDecodeError, PermissionError):
            pass

    time.sleep(0.1)