import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class SecurityManager:
    def __init__(self):
        self.fernet_key = self._load_or_create_fernet_key()
        self.fernet = Fernet(self.fernet_key)
        self.private_key = self._load_or_create_private_key()
        self.public_key = self.private_key.public_key()

    # --- SYMMETRIC ENCRYPTION ---
    def _load_or_create_fernet_key(self):
        key_path = "secret.key"
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return f.read()
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
        return key

    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        return self.fernet.decrypt(encrypted_data).decode()

    # --- ASYMMETRIC (RSA) SIGNATURES ---
    def _load_or_create_private_key(self):
        key_path = "private_key.pem"
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        return private_key

    def sign(self, data: str) -> bytes:
        return self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify(self, data: str, signature: bytes) -> bool:
        try:
            self.public_key.verify(
                signature,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def get_public_key_pem(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

# Test block (optional)
if __name__ == "__main__":
    sm = SecurityManager()
    msg = "Test message"
    enc = sm.encrypt(msg)
    print("Encrypted:", enc)
    print("Decrypted:", sm.decrypt(enc))
    sig = sm.sign(msg)
    print("Signature valid?", sm.verify(msg, sig))
