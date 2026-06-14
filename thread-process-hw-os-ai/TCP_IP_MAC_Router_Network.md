# Complete Journey: Application → Presentation → Packet → IP → MAC → Internet → Remote Server

Let's assume you open **[https://www.google.com](https://www.google.com)** from your laptop.

---

# 1. Application Layer (Layer 7)

You type:

```http
https://www.google.com
```

The browser creates an HTTP request:

```http
GET / HTTP/1.1
Host: www.google.com
```

```text
+-------------------+
| Chrome / Firefox  |
| HTTP Request      |
+-------------------+
```

At this point:

* No IP address yet
* No MAC address yet
* Only application data

---

# 2. Presentation Layer (Layer 6)

Since HTTPS is used:

* TLS/SSL encryption starts
* Certificates are verified
* Data is encrypted

```text
+-------------------+
| HTTP Request      |
+-------------------+
          |
          V
+-------------------+
| TLS Encryption    |
+-------------------+
```

Result:

```text
Encrypted HTTPS Data
```

---

# 3. Session Layer (Layer 5)

TLS session is established.

```text
Client ---------------- Server

TLS Handshake
Certificate Exchange
Session Key Creation
```

After handshake:

```text
Encrypted Session Active
```

---

# 4. Transport Layer (Layer 4)

TCP is used.

Example:

```text
Source Port      = 52341
Destination Port = 443
```

TCP Header added:

```text
+-------------+
| TCP Header  |
+-------------+
| HTTPS Data  |
+-------------+
```

Now it becomes a:

```text
TCP Segment
```

---

# 5. Network Layer (Layer 3)

The system must find Google's IP.

Browser asks DNS:

```text
www.google.com ?
```

DNS replies:

```text
142.250.190.78
```

Now IP Header added:

```text
Source IP      = 192.168.1.100
Destination IP = 142.250.190.78
```

Packet:

```text
+------------+
| IP Header  |
+------------+
| TCP Header |
+------------+
| HTTPS Data |
+------------+
```

Now it becomes:

```text
IP Packet
```

---

# But How Does It Find MAC Address?

Important:

IP works globally.

MAC works only inside the current local network.

Suppose:

```text
PC IP      = 192.168.1.100
Router IP  = 192.168.1.1
Google IP  = 142.250.190.78
```

Google is NOT in local subnet.

Therefore:

```text
Destination MAC = Router MAC
```

Not Google's MAC.

---

# 6. ARP Resolution

PC checks ARP Cache:

```text
192.168.1.1 ?
```

Not found.

PC broadcasts:

```text
Who has 192.168.1.1 ?
Tell 192.168.1.100
```

Broadcast MAC:

```text
FF:FF:FF:FF:FF:FF
```

Diagram:

```text
                 Broadcast
PC ------------------------------------>
           Who has 192.168.1.1?
```

Router replies:

```text
192.168.1.1 is
AA:BB:CC:DD:EE:FF
```

ARP Table:

```text
192.168.1.1
AA:BB:CC:DD:EE:FF
```

---

# 7. Data Link Layer (Layer 2)

Ethernet Header added:

```text
Destination MAC
AA:BB:CC:DD:EE:FF

Source MAC
11:22:33:44:55:66
```

Frame:

```text
+-------------------+
| Ethernet Header   |
+-------------------+
| IP Header         |
+-------------------+
| TCP Header        |
+-------------------+
| HTTPS Data        |
+-------------------+
```

Now it becomes:

```text
Ethernet Frame
```

---

# 8. Physical Layer (Layer 1)

Frame converted to bits:

```text
101101010101001010101
```

Sent through:

* WiFi radio
* Ethernet cable
* Fiber

```text
PC
 |
 | Bits
 |
 V
Router
```

---

# Complete Encapsulation

```text
Application Layer
----------------------------------
HTTP Request

Presentation Layer
----------------------------------
TLS Encryption

Transport Layer
----------------------------------
[TCP Header][Data]

Network Layer
----------------------------------
[IP Header][TCP Header][Data]

Data Link Layer
----------------------------------
[MAC Header][IP Header][TCP Header][Data]

Physical Layer
----------------------------------
010101010101010101010
```

---

# What Happens at the Router?

Router receives:

```text
Destination MAC
AA:BB:CC:DD:EE:FF
```

Matches its own MAC.

Router removes Ethernet Header.

Now router sees:

```text
Destination IP
142.250.190.78
```

Routing Table:

```text
142.250.190.78
→ ISP Gateway
```

Router creates NEW frame:

```text
Source MAC      = Router MAC
Destination MAC = ISP MAC
```

Important:

```text
MAC changes at every hop
IP remains the same
```

---

# Global Internet Journey

```text
PC
192.168.1.100
MAC A
     |
     V
Router
192.168.1.1
MAC B
     |
     V
ISP Router
MAC C
     |
     V
Core Router
MAC D
     |
     V
Google Edge Router
MAC E
     |
     V
Google Server
142.250.190.78
MAC F
```

At every hop:

```text
New MAC Header
Same IP Packet
```

Example:

```text
Hop 1:
MAC A -> MAC B

Hop 2:
MAC B -> MAC C

Hop 3:
MAC C -> MAC D

Hop 4:
MAC D -> MAC E
```

IP remains:

```text
192.168.1.100
       →
142.250.190.78
```

---

# Why Can't We Resolve Google's MAC Address?

Many beginners think:

```text
Need Google's MAC
```

Wrong.

ARP works only inside a LAN.

ARP request:

```text
Who has 142.250.190.78?
```

would never cross the Internet.

Therefore:

```text
PC only learns:

Router MAC
```

Router learns:

```text
ISP MAC
```

ISP learns:

```text
Next Hop MAC
```

And so on.

---

# End-to-End Diagram

```text
+-----------+
| Browser   |
| HTTP GET  |
+-----------+
      |
      V
+-----------+
| TLS       |
| Encrypt   |
+-----------+
      |
      V
+-----------+
| TCP       |
| Port 443  |
+-----------+
      |
      V
+-----------+
| IP Packet |
| Dest:     |
| Google IP |
+-----------+
      |
      V
+-----------+
| ARP       |
| Router    |
| MAC       |
+-----------+
      |
      V
+-----------+
| Ethernet  |
| Frame     |
+-----------+
      |
      V
+-----------+
| Physical  |
| Bits      |
+-----------+
      |
      V
+-----------+
| Router    |
+-----------+
      |
      V
+-----------+
| ISP       |
+-----------+
      |
      V
+-----------+
| Internet  |
+-----------+
      |
      V
+-----------+
| Google    |
+-----------+
```

## Key Rules to Remember

| Item                  | Scope                         |
| --------------------- | ----------------------------- |
| MAC Address           | Local Network (LAN)           |
| IP Address            | Global Internet               |
| ARP                   | Resolves IP → MAC in same LAN |
| DNS                   | Resolves Name → IP            |
| TCP                   | End-to-End transport          |
| TLS                   | Encryption                    |
| Router                | Rewrites MAC headers          |
| Internet              | Routes based on IP            |
| MAC Changes           | Every hop                     |
| IP Usually Stays Same | End-to-End                    |

**One-line summary:**

**DNS finds the destination IP, ARP finds the next-hop MAC, Ethernet delivers locally, routers keep changing MAC addresses hop-by-hop, and the IP packet travels end-to-end across the Internet.**
