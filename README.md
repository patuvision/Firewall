# Firewall

بسته‌ها را قبل از رسیدن به سرویس بررسی می‌کند و طبق Ruleها اجازه می‌دهد، محدود می‌کند یا Drop می‌کند.

```text
   UP Network Dev
         |
     Attachment -> Monitor -> Firewall Algorithm -> Log <-----|
                      |                |              _______ Drop
                      |                ------Rule--->|_______ Accept -> Forward
              All Network Protocol
```

## Rule

* Add rate limiting for excessive incoming traffic.
* Limit new TCP connections per source IP.
* Drop invalid and malformed packets.
* Add basic SYN flood protection.
* Rate-limit ICMP/ping requests.
* Block unnecessary ports and allow only required services.
* Add temporary blocking for IPs that exceed defined limits.
* Keep established and related connections allowed.

### Current Simulation Rule

در نسخه فعلی پروژه، Rule پیاده‌سازی‌شده:

```text
Maximum 5 ICMP requests
within 5 seconds
per source IP
```

مثال:

```text
Packet 1 → PASS
Packet 2 → PASS
Packet 3 → PASS
Packet 4 → PASS
Packet 5 → PASS
Packet 6 → DROP
Packet 7 → DROP
```

## Log

* Test the rules to avoid blocking legitimate users.
* Log suspicious or dropped traffic without flooding the logs.

نمونه Log:

```text
PASS | 192.168.1.100 | ICMP
PASS | 192.168.1.100 | ICMP
DROP | 192.168.1.100 | ICMP rate limit exceeded
```

DROPها در `firewall.log` ذخیره می‌شوند تا ترمینال با پیام‌های تکراری پر نشود.

## Used Packages

در نسخه فعلی پروژه از کتابخانه‌های استاندارد Python استفاده شده است:

* `queue`
* `threading`
* `logging`
* `time`

> `Scapy` در نسخه فعلی استفاده نشده است، زیرا این پروژه به‌صورت Symbolic/Simulation اجرا می‌شود و ترافیک واقعی شبکه را دریافت نمی‌کند.

## Project Structure

```text
Firewall/
│
├── attacker.py
├── firewall.py
├── server.py
├── user.py
└── firewall.log
```

### `attacker.py`

ترافیک ICMP را به‌صورت Symbolic شبیه‌سازی می‌کند.

### `firewall.py`

بسته‌ها را بررسی کرده و Rule مربوط به Rate Limiting را اعمال می‌کند.

### `server.py`

بسته‌هایی را که Firewall اجازه داده است دریافت می‌کند.

### `user.py`

اطلاعات کاربر مانند Username و IP را نگهداری می‌کند.

### `firewall.log`

رویدادهای Firewall را ذخیره می‌کند.

## Schematic

```text
                         ┌──────────────────┐
                         │    attacker.py   │
                         │                  │
                         │  Simulated ICMP  │
                         │     Packets      │
                         └────────┬─────────┘
                                  │
                                  │ Queue
                                  ▼
                         ┌──────────────────┐
                         │    firewall.py   │
                         │                  │
                         │  ICMP Rate Limit │
                         │     5 / 5 sec    │
                         └───────┬──────┬───┘
                                 │      │
                              PASS      DROP
                                 │      │
                                 ▼      ▼
                       ┌────────────┐  ┌──────────────┐
                       │ server.py  │  │firewall.log  │
                       │            │  │              │
                       │  Receive   │  │ PASS / DROP  │
                       │  Packets   │  │    Logs      │
                       └────────────┘  └──────────────┘
                              ▲
                              │
                       ┌────────────┐
                       │  user.py   │
                       │            │
                       │ Username   │
                       │ IP Address │
                       │ Status     │
                       └────────────┘
```

## Packet Flow

```text
┌───────────┐
│ Attacker  │
└─────┬─────┘
      │
      │ ICMP Packet
      ▼
┌───────────┐
│ Firewall  │
└─────┬─────┘
      │
      ├───────────────┐
      │               │
      │ PASS          │ DROP
      ▼               ▼
┌───────────┐    ┌─────────────┐
│  Server   │    │ firewall.log│
└───────────┘    └─────────────┘
```

## Command Line

نمونه خروجی محیط شبکه:

```text
==> ip -br link

lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
eno1             DOWN           bc:fc:e7:3a:be:99 <NO-CARRIER,BROADCAST,MULTICAST,UP>
wlp0s20f3        UP             30:e3:a4:34:45:18 <BROADCAST,MULTICAST,UP,LOWER_UP>
```

> این Command مربوط به Linux Network Interfaceها است و در نسخه فعلی Symbolic Firewall برای دریافت ترافیک واقعی استفاده نمی‌شود.

## Running

برای اجرای پروژه:

```bash
python attacker.py
```

پس از اجرا:

```text
Server is running...
User: Ali
IP: 192.168.1.100
Status: ONLINE

Firewall is running...
Rule: Maximum 5 ICMP requests per 5 seconds

Attacker started...

[ATTACKER] ICMP packet 1
[PASS] 192.168.1.100 -> SERVER

[ATTACKER] ICMP packet 2
[PASS] 192.168.1.100 -> SERVER

[ATTACKER] ICMP packet 3
[PASS] 192.168.1.100 -> SERVER

[ATTACKER] ICMP packet 4
[PASS] 192.168.1.100 -> SERVER

[ATTACKER] ICMP packet 5
[PASS] 192.168.1.100 -> SERVER

[ATTACKER] ICMP packet 6
[BLOCKING] 192.168.1.100 exceeded ICMP rate limit
```

## Packet Format

بسته‌ها در این پروژه به‌صورت Python Dictionary شبیه‌سازی می‌شوند:

```python
packet = {
    "src": "192.168.1.100",
    "type": "ICMP"
}
```

`src` آدرس IP مبدأ را نشان می‌دهد و `type` نوع Packet را مشخص می‌کند.

## Communication

ارتباط داخلی اجزای پروژه با `Queue` انجام می‌شود:

```text
attacker.py
     │
     │ attacker_to_firewall
     ▼
firewall.py
     │
     │ firewall_to_server
     ▼
server.py
```

هیچ فایل JSON و هیچ Network Socket برای ارتباط داخلی پروژه استفاده نمی‌شود.

## Limitations

این پروژه یک **Symbolic Firewall Simulation** است.

بنابراین:

* ترافیک واقعی شبکه را دریافت نمی‌کند.
* Packet واقعی از Network Interface دریافت نمی‌کند.
* ترافیک واقعی را Block نمی‌کند.
* Windows Firewall را تغییر نمی‌دهد.
* `iptables` را تغییر نمی‌دهد.
* `nftables` را تغییر نمی‌دهد.
* از Scapy برای دریافت Packet واقعی استفاده نمی‌کند.
* از WinDivert استفاده نمی‌کند.
* Packetها فقط به‌صورت Objectهای Python شبیه‌سازی می‌شوند.
