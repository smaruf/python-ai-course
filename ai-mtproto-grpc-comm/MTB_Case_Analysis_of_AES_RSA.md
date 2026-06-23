What you built for Mercantile Bank is a classic implementation of **Application-Layer Encryption (ALE)** running over an existing transport security layer (HTTPS). Essentially, you recreated a localized TLS handshaking behavior inside the application space itself to protect high-stakes banking payloads.

Here is an analysis of the architectural benefits and the hidden cryptographic vulnerabilities of wrapping an AES key in RSA inside a React-to-Spring pipeline.

---

## The Architectural Benefits

### 1. Defense-in-Depth Against TLS Termination & Interception

In corporate or banking environments, infrastructure often relies on reverse proxies, load balancers, or API gateways (like F5, NGINX, or AWS ALB) to terminate HTTPS traffic before routing it inside the internal network via plain HTTP.

* **The Benefit:** By encrypting the payload *inside* the React code, the data remains a blind string of ciphertext even if the outer HTTPS is stripped by a network gateway. This protects banking data from internal bad actors or misconfigured cloud logging tools that print JSON bodies to plain text files.

### 2. Resistance to Reverse-Proxy Decryption (Mitmproxy/Burp Suite)

Tech-savvy users or attackers often install custom root certificates on devices to monitor REST API payloads via tools like Burp Suite.

* **The Benefit:** Because you used Application-Layer Encryption, an attacker intercepting the data at the device level still only sees the custom-encrypted string, frustrating basic API reverse-engineering attempts.

### 3. Cryptographic Efficiency (Hybrid Encryption)

You leveraged the optimal architectural approach for data sizes: **RSA** is computationally heavy and cannot encrypt large payloads, while **AES** is blazing fast but needs a safe key transport mechanism. Using RSA solely to wrap a lightweight 256-bit AES key, then switching to AES for the `POST` request body, minimized the client-side CPU strain in React.

---

## Structural Vulnerabilities & Implementation Pitfalls

While the conceptual math is sound, implementing this manually outside the browser's native Web Crypto API structures opens up several classic vulnerabilities:

### 1. The Key Distribution & Authentication Flaw (Man-in-the-Middle)

How did the React frontend get the server's RSA Public Key?

* **The Risk:** If the client simply made an API fetch request like `GET /api/auth/public-key` over HTTPS, it relies entirely on HTTPS security. If an attacker successfully compromises the HTTPS layer (e.g., via a compromised corporate CA certificate), they can intercept that `GET` request and substitute *their own* fake RSA public key.
* **The Exploit:** React encrypts the AES key using the attacker's fake RSA key. The attacker decrypts it, steals the AES key, re-encrypts it with the bank's true public key, and forwards it. The handshake is entirely compromised.

### 2. Lack of Perfect Forward Secrecy (PFS)

If the backend Java server uses a **static** RSA Private Key to decrypt the incoming AES keys from all users:

* **The Risk:** If that single server-side RSA private key is ever leaked, stolen, or compromised by an intruder months later, an attacker who silently recorded past encrypted network traffic can decrypt *every single AES key* transmitted by every user historically.
* **The Fix:** Modern handshakes use **Diffie-Hellman (ECDHE)** for key exchange instead of RSA key wrapping, ensuring that the compromised master keys cannot unlock historical data.

### 3. Cross-Site Scripting (XSS) Memory Extraction

Because this key management occurs inside the JavaScript runtime environment of React:

* **The Risk:** If your application is vulnerable to a basic Cross-Site Scripting (XSS) attack (e.g., through a dirty third-party npm package or unsanitized user inputs), malicious JavaScript can scan the browser's memory heap.
* **The Exploit:** The script can pull the raw, unencrypted AES session key straight out of your React state/context or hijack the custom encryption function entirely. Native HTTPS handles keys outside the reach of JavaScript execution entirely.

### 4. Implementation Bugs: Padding & Replay Attacks

* **RSA Padding Vulnerabilities:** If the Java backend used standard `Cipher.getInstance("RSA")` without explicitly specifying secure padding like **OAEP** (e.g., `RSA/ECB/OAEPWithSHA-256AndMGF1Padding`), it defaults to `PKCS1v1.5`, which is highly vulnerable to classic decryption padding oracle attacks.
* **Replay Attacks:** If the custom-encrypted `POST` payload does not include a high-entropy server-provided cryptographic **nonce** or a strict timestamp, an attacker could capture a valid encrypted payload (e.g., an encrypted "Transfer 5000 BDT" payload) and replay it to the backend server multiple times. The server would decrypt it perfectly every time and duplicate the transfer.

---

## Verdict: Was it worth it?

**Yes, but with caveats.** It is a solid compliance and defense-in-depth measure that satisfies strict banking security audits regarding end-to-end payload visibility.

However, it should never be seen as a replacement for transport security. To maximize this setup, the RSA public key should be securely pinned or signed, modern padding frameworks must be enforced in Java, and a strict request nonce must be bundled into the AES-encrypted payload to avoid replay exploits.
