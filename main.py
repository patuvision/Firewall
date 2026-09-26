import json
import time
import os
import logging

INPUT = "attacker_to_firewall.json"
OUTPUT = "firewall_to_server.json"

LIMIT = 5
WINDOW = 5

requests = {}

logging.basicConfig(
    filename="firewall.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

print("Firewall is running...")
print("Rule: 5 ICMP / 5 seconds")

while True:
    if os.path.exists(INPUT):
        try:
            with open(INPUT, "r") as file:
                packets = json.load(file)

            if packets:
                packet = packets.pop(0)

                with open(INPUT, "w") as file:
                    json.dump(packets, file)

                ip = packet["src"]
                now = time.time()

                if ip not in requests:
                    requests[ip] = []

                requests[ip] = [
                    t for t in requests[ip]
                    if now - t < WINDOW
                ]

                if len(requests[ip]) >= LIMIT:

                    logging.warning(
                        f"DROP | {ip} | ICMP rate limit exceeded"
                    )

                    if len(requests[ip]) == LIMIT:
                        print(
                            f"[BLOCKING] {ip} "
                            f"exceeded ICMP limit"
                        )

                else:
                    requests[ip].append(now)

                    logging.info(
                        f"PASS | {ip} | ICMP"
                    )

                    if os.path.exists(OUTPUT):
                        with open(OUTPUT, "r") as file:
                            server_packets = json.load(file)
                    else:
                        server_packets = []

                    server_packets.append(packet)

                    with open(OUTPUT, "w") as file:
                        json.dump(server_packets, file)

                    print(f"[PASS] {ip} -> SERVER")

        except (json.JSONDecodeError, PermissionError):
            pass

    time.sleep(0.1)
