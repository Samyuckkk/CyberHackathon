import base64, os, hashlib, time
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------------- MOCK KYBER (uses ECC under the hood) ---------------- #
class MockKyber:
    def generate_keypair(self):
        priv = x25519.X25519PrivateKey.generate()
        pub = priv.public_key()
        pub_b = pub.public_bytes()
        priv_b = priv.private_bytes()
        return base64.b64encode(pub_b).decode(), base64.b64encode(priv_b).decode()

    def encap(self, server_pub_b64):
        server_pub = x25519.X25519PublicKey.from_public_bytes(base64.b64decode(server_pub_b64))
        eph_priv = x25519.X25519PrivateKey.generate()
        eph_pub_b = eph_priv.public_key().public_bytes()
        shared = eph_priv.exchange(server_pub)
        return base64.b64encode(eph_pub_b).decode(), base64.b64encode(shared).decode()

    def decap(self, eph_pub_b64, server_priv_b64):
        eph_pub = x25519.X25519PublicKey.from_public_bytes(base64.b64decode(eph_pub_b64))
        server_priv = x25519.X25519PrivateKey.from_private_bytes(base64.b64decode(server_priv_b64))
        shared = server_priv.exchange(eph_pub)
        return base64.b64encode(shared).decode()

# ---------------- MOCK DILITHIUM (SHA256-HMAC style) ---------------- #
class MockDilithium:
    @staticmethod
    def generate_keypair():
        secret = os.urandom(32)
        return base64.b64encode(secret).decode(), base64.b64encode(secret).decode()

    @staticmethod
    def sign(msg_bytes, priv_b64):
        priv = base64.b64decode(priv_b64)
        return base64.b64encode(hashlib.sha256(priv + msg_bytes).digest()).decode()

    @staticmethod
    def verify(msg_bytes, sig_b64, pub_b64):
        pub = base64.b64decode(pub_b64)
        expected = hashlib.sha256(pub + msg_bytes).digest()
        return base64.b64encode(expected).decode() == sig_b64

# ---------------- HKDF helper ---------------- #
def hkdf_derive(secret_bytes, length=32):
    hk = HKDF(algorithm=hashes.SHA256(), length=length, salt=None, info=b"hybrid-pqc")
    return hk.derive(secret_bytes)
