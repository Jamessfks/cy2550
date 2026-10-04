1.1 Encrypt and Decrypt a File – 5 Points

Basically, -pbkdf2 tells OpenSSL to turn the passphrase into a key and IV(Initialization Vector) using PBKDF2 (Password-Based Key Derivation Function 2).

It matters because OpenSSL uses the legacy EVP_BytesToKey, which hashes only once. But -pbkdf2 by default hashes 10,000 times, which is better.


1.2 Encrypt the Same File Twice – 5 Points

Because -salt generates a new random salt byte, not the same.

If they are the same, that would be deterministic encryption, and it leaks information. Then, an attacker can tell that two encrypted files contain the same data and without decrypting anything.

1.3 Watching ECB Leak Information – 10 Points

Q1:How many distinct blocks does each encryption produce, and how many times does the most common ECB block repeat?

ECB: 3 distinct blocks. The most common one repeats 24 times, and that is the A-block. The next repeats 12 times, the B-blocks, and 1 is the padding block.
CBC: 37 distinct blocks. Each appearing once.

Q2:AES-256 is not broken, and your passphrase was not weak. What exactly did ECB leak? To an attacker who never learns your key, what information is that worth?

It leaks that identical plaintext blocks always produce identical ciphertext blocks. Because attackers can tell the frequency of repetition and which blocks are equal and where they appear.

For example, they can tell which database records share the same password or same age; they see duplicates, and they can use it for frequency analysis.

Q3: You are told a system encrypts database records with AES. What is one question you would ask before believing the records are protected?

Which mode of operation is used, and does each record get a unique, random initialization vector to ensure randomness?



2.2 Keyed Hashing – 6 Points

Explain precisely:

Why the SHA-256 hash does not protect your colleague.
A SHA-256 hash has no secret, and anyone can compute it. The attacker changes the file, computes a new hash for it, and sends both. So the colleague might receive someone else's file without identifying who the sender is.

What changes when you use an HMAC instead?

HMAC mixes a secret key into the hash, so only people who know the key can produce a valid tag. The key must be shared before the exchange. It is never sent alongside the file. Now if the attacker changes the file, they can not make a matching tag, so the colleague's check fails.

What the attacker can and cannot do in each situation (SHA-256 and HMAC).

In SHA-256, they can read and modify the file and trick the colleague. But they can not make a different file that produces the same hash as your original

In HMAC, they can read and modify the file. Also, they can block or delete the file. But can not fool the colleague and forge a valid hash tag.


3.3 Fingerprints – 5 Points
The keyserver would not publish your email address until you clicked a verification link sent by email. What does this check prove? What does it not prove?

It proves that whoever uploaded the key could read emails sent to that address. But It doesn't prove that the uploader is the real person named on the key, and anyone can type any name.
That the email account wasn't hacked or shared.






You downloaded a public key claiming to belong to a classmate. The fingerprint is 40 hexadecimal characters. Describe a procedure for checking that the key really belongs to your classmate in a way that would defeat an attacker who controls the network between you. Explain why your procedure works.


Run gpg --fingerprint <classmate's email> on the downloaded key
Meet my classmate in person, and make sure they aren't wearing any fake customs.
Have them read their fingerprint from their own computer, not from anything you sent them
Compare all 40 characters. If they match, the key is theirs

It works. The fingerprint is a hash of the public key. An attacker can not make a fake key with the same fingerprint. This is because SHA-1 attacks are still infeasible in practice.
Obviously, the attacker can't know the face-to-face conversation. So the fingerprint arrives through a channel they can't touch.


4.2 Find the Hybrid Encryption – 7 Points

What is contained in each packet?


pubkey enc packet: version 3, algo 1, keyid 0998100E9441EE2C
	data: [4093 bits]
# off=527 ctb=d2 tag=18 hlen=2 plen=90 new-ctb
:encrypted data packet:
	length: 90
	mdc_method: 2
So pubkey enc packet contains: A random session key and a RSA public key.
Encrypted data packet contains: my actual message,encrypted with the session key using a symmetric cipher.




Why does GPG use this approach instead of encrypting the entire message with RSA?


Because it is faster. RSA is very slow. While symmetric ciphers like AES are thousands of times faster. Also, because of the size limit. RSA-4096 can encrypt only about 500 bytes at once, so large files won't fit. And it requires even more time to perform another one.
What is this construction called?
Hybrid encryption


4.3 Sign, Verify, and Break – 8 Points

Written Answer
Which key is used for signing?
Signer's private key
Which key is used for verifying?
Signer's public RSA key
Which key is used for encryption?
Recipient’s public key
Which key is used for decryption?
Recipient’s private key
What is one security property provided by signing that encryption does not include?
Verify the authentication

Part 5: SSH Keys – 5 Points

Your GPG key is RSA-4096, while your SSH key is Ed25519, which is roughly a 256-bit elliptic curve key. Explain in two sentences why the much smaller Ed25519 key is not necessarily the weaker key.

Because  Ed25519 is generally much faster than RSA at key generation and signing. Also, the Ed25519 has randomness and avoids the risky prime-number generation flaws that affect RSA. Lastly, Elliptic curves, the one Ed25519 uses, have no such shortcut, so a 256-bit Ed25519 key gives about 128-bit security.


7.1
prompt: "Write me a Python function that encrypts a file with AES"

Model: Claude Opus 5.5 High


7.2 Critique the AI Code – 8 Points

First, ciphertext isn't bound to its context. The associated data is None, so nothing ties an encrypted file to its filename or version. What an attacker can do is to Swap secret.enc with another file encrypted with the same key, or replace it with an older version. The Concept violated: Integrity and authenticity are incomplete. This is the problem from HMAC Part 2.2.

Secondly, the plaintext length is revealed. The GCM doesn't pad, so the ciphertext size is the plaintext size plus 28 bytes. This will lead to learning the exact file size without the key. This can reveal content. For example, telling "yes" from "no".The Concept violated: Information leakage without breaking AES. ECB in Part 1.3.

Lastly, unsafe key handling is left to the user. The code creates a raw key with only limited guidance. The provided decrypt line also has no error handling for a failed authentication check. If the user stores the key next to the encrypted file or in source code. The the attacker can decrypt everything. Concept violated: Key management; Kerckhoffs's principle: security must rest on the key staying secret.


7.3 explanation
I added the filename as associated data. The ciphertext is tied to its filename. Therefore, the attacker can not swap in a different encrypted file. This fixes Defect 1.
Then I padded the plaintext to a multiple of 1024 bytes, with the real length stored inside the encryption, which fixes Defect 2, the length leak. 
Lastly, derived the key from a password using PBKDF2 with a random salt. Thus ,the user no longer has to store a raw key file. Eventually, fixes defect 3.


Basically, -pbkdf2 tells OpenSSL to turn the passphrase into a key and IV(Initialization Vector) using PBKDF2 (Password-Based Key Derivation Function 2).

It matters because OpenSSL uses the legacy EVP_BytesToKey, which hashes only once. But -pbkdf2 by default hashes 10,000 times, which is better.


1.2 Encrypt the Same File Twice – 5 Points

Because -salt generates a new random salt byte, not the same.

If they are the same, that would be deterministic encryption, and it leaks information. Then, an attacker can tell that two encrypted files contain the same data and without decrypting anything.

1.3 Watching ECB Leak Information – 10 Points

Q1:How many distinct blocks does each encryption produce, and how many times does the most common ECB block repeat?

ECB: 3 distinct blocks. The most common one repeats 24 times, and that is the A-block. The next repeats 12 times, the B-blocks, and 1 is the padding block.
CBC: 37 distinct blocks. Each appearing once.

Q2:AES-256 is not broken, and your passphrase was not weak. What exactly did ECB leak? To an attacker who never learns your key, what information is that worth?

It leaks that identical plaintext blocks always produce identical ciphertext blocks. Because attackers can tell the frequency of repetition and which blocks are equal and where they appear.

For example, they can tell which database records share the same password or same age; they see duplicates, and they can use it for frequency analysis.

Q3: You are told a system encrypts database records with AES. What is one question you would ask before believing the records are protected?

Which mode of operation is used, and does each record get a unique, random initialization vector to ensure randomness?



2.2 Keyed Hashing – 6 Points

Explain precisely:

Why the SHA-256 hash does not protect your colleague.
A SHA-256 hash has no secret, and anyone can compute it. The attacker changes the file, computes a new hash for it, and sends both. So the colleague might receive someone else's file without identifying who the sender is.

What changes when you use an HMAC instead?

HMAC mixes a secret key into the hash, so only people who know the key can produce a valid tag. The key must be shared before the exchange. It is never sent alongside the file. Now if the attacker changes the file, they can not make a matching tag, so the colleague's check fails.

What the attacker can and cannot do in each situation (SHA-256 and HMAC).

In SHA-256, they can read and modify the file and trick the colleague. But they can not make a different file that produces the same hash as your original

In HMAC, they can read and modify the file. Also, they can block or delete the file. But can not fool the colleague and forge a valid hash tag.


3.3 Fingerprints – 5 Points
The keyserver would not publish your email address until you clicked a verification link sent by email. What does this check prove? What does it not prove?

It proves that whoever uploaded the key could read emails sent to that address. But It doesn't prove that the uploader is the real person named on the key, and anyone can type any name.
That the email account wasn't hacked or shared.






You downloaded a public key claiming to belong to a classmate. The fingerprint is 40 hexadecimal characters. Describe a procedure for checking that the key really belongs to your classmate in a way that would defeat an attacker who controls the network between you. Explain why your procedure works.


Run gpg --fingerprint <classmate's email> on the downloaded key
Meet my classmate in person, and make sure they aren't wearing any fake customs.
Have them read their fingerprint from their own computer, not from anything you sent them
Compare all 40 characters. If they match, the key is theirs

It works. The fingerprint is a hash of the public key. An attacker can not make a fake key with the same fingerprint. This is because SHA-1 attacks are still infeasible in practice.
Obviously, the attacker can't know the face-to-face conversation. So the fingerprint arrives through a channel they can't touch.


4.2 Find the Hybrid Encryption – 7 Points

What is contained in each packet?


pubkey enc packet: version 3, algo 1, keyid 0998100E9441EE2C
	data: [4093 bits]
# off=527 ctb=d2 tag=18 hlen=2 plen=90 new-ctb
:encrypted data packet:
	length: 90
	mdc_method: 2
So pubkey enc packet contains: A random session key and a RSA public key.
encrypted data packet contains: my actual message, encrypted with the session key.




Why does GPG use this approach instead of encrypting the entire message with RSA?


Because it is faster. RSA is very slow. While symmetric ciphers like AES are thousands of times faster. Also, because of the size limit. RSA-4096 can encrypt only about 500 bytes at once, so large files won't fit. And it requires even more time to perform another one.
What is this construction called?
Hybrid encryption


4.3 Sign, Verify, and Break – 8 Points

Written Answer
Which key is used for signing?
Signer's private key
Which key is used for verifying?
Signer's public RSA key
Which key is used for encryption?
Recipient’s public key
Which key is used for decryption?
Recipient’s private key
What is one security property provided by signing that encryption does not include?
Verify the authentication

Part 5: SSH Keys – 5 Points

Your GPG key is RSA-4096, while your SSH key is Ed25519, which is roughly a 256-bit elliptic curve key. Explain in two sentences why the much smaller Ed25519 key is not necessarily the weaker key.

Because  Ed25519 is generally much faster than RSA at key generation and signing. Also, the Ed25519 has randomness and avoids the risky prime-number generation flaws that affect RSA.




7.2 Critique the AI Code – 8 Points

First, ciphertext isn't bound to its context. The associated data is None, so nothing ties an encrypted file to its filename or version. What an attacker can do is to Swap secret.enc with another file encrypted with the same key, or replace it with an older version. The Concept violated: Integrity/authenticity is incomplete. This is the problem from HMAC Part 2.2.

Secondly, the plaintext length is revealed. The GCM doesn't pad, so the ciphertext size is the plaintext size plus 28 bytes. This will lead to learning the exact file size without the key. This can reveal content. For example, telling "yes" from "no".The Concept violated: Information leakage without breaking AES. ECB in Part 1.3.

Lastly, unsafe key handling is left to the user. The code creates a raw key with only limited guidance. The provided decrypt line also has no error handling for a failed authentication check. If the user stores the key next to the encrypted file or in source code. The the attacker can decrypt everything. Concept violated: Key management; Kerckhoffs's principle: security must rest on the key staying secret.


7.3 explanation
I added the filename as associated data. The ciphertext is tied to its filename. Therefore, the attacker can not swap in a different encrypted file. This fixes Defect 1.
Then I padded the plaintext to a multiple of 1024 bytes, with the real length stored inside the encryption, which fixes Defect 2, the length leak. 
Lastly, derived the key from a password using PBKDF2 with a random salt. Thus ,the user no longer has to store a raw key file. Eventually, fixes defect 3

Demonstration on my VM:
```
$ python3 -c "import fixed_crypto as f; ..." && diff secret.txt demo_out.txt && echo "ROUND TRIP OK"
ROUND TRIP OK
```
