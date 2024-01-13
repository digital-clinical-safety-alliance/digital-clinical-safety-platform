from cryptography.fernet import Fernet
import os

# key = Fernet.generate_key()
key = os.environ.get("ENCRYPTION_KEY").encode()
print(f"Key is: { key }")
cipher_suite = Fernet(key)

print(cipher_suite)

value = "Hello there"
encypted = cipher_suite.encrypt(value.encode()).decode()
print(f"Encrypted password:\n{ encypted }")
print(cipher_suite.decrypt(encypted).decode())
