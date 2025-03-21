from cryptography.fernet import Fernet

# Generate a key for encryption and decryption
# This should be done only once and the key should be kept safe
def generate_key():
    return Fernet.generate_key()

# Load the key
def load_key():
    return b'TYf25jwwZXsa37g2AnApLouFkiWLLEoLItRucOEOpiM='  # Replace with your actual key

# Encrypt a message
def encrypt_password(password: str) -> str:
    key = load_key()
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password.decode()

# Decrypt a message
def decrypt_password(encrypted_password: str) -> str:
    key = load_key()
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password.encode())
    return decrypted_password.decode()
