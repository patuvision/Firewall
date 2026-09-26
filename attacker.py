import json
import time
import os

QUEUE = "attacker_to_firewall.json"

packet = {
    "src": "192.168.1.100",
    "type": "ICMP"
}

if not os.path.exists(QUEUE):
    with open(QUEUE, "w") as file:
        json.dump([], file)

print("Attacker started...")

for i in range(15):

    with open(QUEUE, "r") as file:
        packets = json.load(file)

    packets.append(packet)

    with open(QUEUE, "w") as file:
        json.dump(packets, file)

    print(f"[ATTACKER] Packet {i + 1}")

    time.sleep(0.2)

print("Attack finished.")
