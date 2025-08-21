from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def create_client(user_id: str) -> None:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with open(f'./keys/private/{user_id}.pem', 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    public_key = private_key.public_key()
    with open(f'./keys/public/{user_id}.pem', 'wb') as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

def send_message(message: str, user_id: str) -> tuple[bytes, bytes]:
    message = message.encode('utf-8')
    key = RSA.import_key(open(f'./keys/private/{user_id}.pem').read())
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    return message, signature


def validate_signature(message: bytes, signature: bytes, user_id: str) -> None:
    key = RSA.import_key(open(f'./keys/public/{user_id}.pem').read())
    h = SHA256.new(message)
    try:
        pkcs1_15.new(key).verify(h, signature)
        print("The signature is valid.")
    except (ValueError, TypeError):
        print("The signature is not valid.")


create_client("torts")
create_client("duds")

message, signature = send_message(message="To be signed",user_id="duds")

validate_signature(message, signature, user_id="duds")
validate_signature(message, signature, user_id="torts")



