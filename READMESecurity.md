# 🔐 SecurityManager: Python Encryption & Signing Utility

## 📖 Overview

**SecurityManager** is a Python class that provides a simple interface for:
- **Symmetric encryption/decryption** using the Fernet (AES) method.
- **Asymmetric signing/verification** using RSA digital signatures.

The class handles key generation and storage securely, allowing for encrypted data handling and integrity verification across multiple runs of your application.

---

## 🛠️ Features

- 🔒 AES-based symmetric encryption (Fernet)
- ✍️ RSA-based digital signature and verification
- 🧠 Automatic key generation and persistent storage:
  - `secret.key` for Fernet encryption
  - `private_key.pem` for RSA signing
- ✅ Easy-to-use API for encrypting, decrypting, signing, and verifying messages

---

## 📂 Files

- `security_manager.py` – Main class implementation
- `secret.key` – Symmetric key file (auto-generated)
- `private_key.pem` – RSA private key file (auto-generated)
- `README.md` – This file

---

## 📦 Requirements

Make sure you have Python 3.6+ installed.

Install required packages:

```bash
pip install cryptography
