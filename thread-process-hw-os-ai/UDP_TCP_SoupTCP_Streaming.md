Since you're interested in market data protocols (FAST, ITCH, FIX, Kafka), understanding **UDP, TCP, SoupTCP, and Streaming** is extremely important because exchanges use different transport mechanisms for different purposes.

# 1. UDP (User Datagram Protocol)

UDP is the simplest transport protocol.

```text
Application
    |
    V
UDP
    |
    V
IP
```

No connection.

No handshake.

No guarantee.

No retransmission.

---

## Example

You send:

```text
Packet #1
Packet #2
Packet #3
Packet #4
```

Network may deliver:

```text
Packet #1
Packet #3
Packet #4
```

Packet #2 lost forever.

Or:

```text
Packet #3
Packet #1
Packet #4
Packet #2
```

Out of order.

UDP doesn't care.

---

## UDP Header

Very small:

```text
+----------------+
| Source Port    |
+----------------+
| Dest Port      |
+----------------+
| Length         |
+----------------+
| Checksum       |
+----------------+
```

Only 8 bytes.

Very fast.

---

## Why Exchanges Use UDP

Market data must be fast.

Example:

```text
NASDAQ
   |
UDP Multicast
   |
Thousands of Traders
```

Sending one packet:

```text
AAPL = 220.50
```

reaches everyone simultaneously.

---

## Advantages

```text
Fast
Low latency
Low overhead
Supports multicast
```

---

## Problems

```text
Packet loss
No ordering
No recovery
```

---

# 2. TCP (Transmission Control Protocol)

TCP prioritizes reliability.

Before sending data:

```text
Client ------ SYN ------>
Server <----- SYN ACK ---
Client ------ ACK ------>
```

Connection established.

---

## TCP Guarantees

### Delivery

If packet lost:

```text
Packet #1
Packet #2
Packet #3
```

Packet #2 lost.

Receiver says:

```text
Need Packet #2
```

TCP retransmits.

---

### Ordering

Even if received:

```text
#3
#1
#2
```

TCP delivers:

```text
#1
#2
#3
```

to application.

---

## Why TCP is Slower

Extra work:

```text
ACKs
Retransmissions
Flow control
Congestion control
Buffers
```

---

# TCP Example

```text
Browser
   |
TCP
   |
HTTPS
   |
Google
```

Every webpage uses TCP.

---

# UDP vs TCP

| Feature        | UDP    | TCP         |
| -------------- | ------ | ----------- |
| Reliable       | No     | Yes         |
| Ordered        | No     | Yes         |
| Handshake      | No     | Yes         |
| Retransmission | No     | Yes         |
| Speed          | Faster | Slower      |
| Multicast      | Yes    | No          |
| Market Data    | Common | Less common |
| Web Traffic    | No     | Yes         |

---

# 3. What is SoupTCP?

SoupTCP was created for financial exchanges.

Widely used by:

* NASDAQ
* OMX
* Many market data feeds

Purpose:

```text
Reliable TCP delivery
+
Simple recovery mechanism
```

---

## Why Not Pure UDP?

Suppose exchange sends:

```text
Seq 1001
Seq 1002
Seq 1003
Seq 1004
```

You miss:

```text
1003
```

Your order book becomes wrong.

Dangerous.

---

## Solution

Use UDP for speed.

Use SoupTCP for recovery.

---

# Typical Exchange Architecture

```text
             UDP Multicast
                  |
                  V

         +----------------+
         | Trading Client |
         +----------------+
                  |
         Lost Message?
                  |
                 Yes
                  |
                  V

            SoupTCP
                  |
                  V

       Missing Messages
```

---

## SoupTCP Sequence Numbers

Every message:

```text
1001
1002
1003
1004
1005
```

Client tracks:

```text
Expected = 1003
Received = 1004
```

Gap detected.

---

Client requests:

```text
Please resend
1003
```

Exchange replies:

```text
1003
```

Gap repaired.

---

## SoupTCP Message Format

Very simple.

```text
+--------+
| Length |
+--------+
| Type   |
+--------+
| Data   |
+--------+
```

---

Common types:

```text
Login
Heartbeat
Sequenced Data
Recovery Data
Logout
```

---

# Real Exchange Architecture

Most exchanges:

```text
                    Exchange

                 +----------+
                 | Matching |
                 | Engine   |
                 +----------+
                       |
        +--------------+-------------+
        |                            |
        V                            V

 UDP Multicast                 SoupTCP
 Market Feed                   Recovery

        |                            |
        +------------+---------------+
                     |
                     V

                Trading Firm
```

---

# 4. What is Streaming?

Streaming means:

```text
Continuous flow of data
```

instead of:

```text
Request
Response
Done
```

---

## Non-Streaming

Browser:

```text
GET page
Receive page
Finished
```

---

## Streaming

Exchange:

```text
Price update
Price update
Price update
Price update
Price update
...
```

Never stops.

---

# Market Data Stream

```text
09:30:00
AAPL 220.50

09:30:00.001
AAPL 220.51

09:30:00.002
AAPL 220.49

09:30:00.003
AAPL 220.52
```

Continuous stream.

---

# Streaming Architectures

## TCP Streaming

```text
Client
   |
 TCP Connection
   |
Server
```

Continuous bytes.

Examples:

```text
FIX
SoupTCP
WebSocket
```

---

## UDP Streaming

```text
Exchange
   |
UDP Multicast
   |
Thousands of Clients
```

Examples:

```text
ITCH
FAST
MoldUDP64
```

---

# Streaming in Exchanges

Typical design:

```text
                Exchange

                     |
         +-----------+-----------+
         |                       |

         V                       V

   UDP Streaming          TCP Streaming
   (FAST/ITCH)            (SoupTCP/FIX)

   Fastest Feed           Recovery/Orders
```

---

# Financial Protocol Stack

```text
Application
--------------------------------
ITCH
FAST
FIX
OUCH
Soup Messages

Transport
--------------------------------
UDP
TCP
SoupTCP

Network
--------------------------------
IP

Data Link
--------------------------------
Ethernet

Physical
--------------------------------
Fiber
```

---

# Simple Mental Model

Think of television:

### UDP

```text
Live TV Broadcast

Miss a frame?
Too bad.
Continue watching.
```

### TCP

```text
Netflix Download

Missing data?
Pause and recover.
```

### SoupTCP

```text
Live TV
+
Ability to request
missed scenes
```

### Streaming

```text
Data never ends

Price
Price
Price
Price
Price
...
```

For stock exchanges, the common pattern is:

```text
Market Data      -> UDP Streaming (ITCH, FAST, MoldUDP64)
Gap Recovery     -> SoupTCP
Orders           -> TCP (OUCH, FIX)
Internal Pipelines -> Kafka Streams
```

This architecture gives the best balance between **speed (UDP)** and **correctness (TCP/SoupTCP recovery)**.
