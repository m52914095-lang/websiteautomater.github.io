"""
XOR Encryption Module for Detective Conan Automation
Handles encryption/decryption of Hard Sub links and password hashes
"""

import hashlib
from typing import Tuple


class XOREncryption:
    """XOR encryption utility for securing Hard Sub links"""
    
    def __init__(self, key: str):
        """
        Initialize XOR encryption with a key
        
        Args:
            key: Encryption key string
        """
        self.key = key
        self.key_bytes = key.encode('utf-8')
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using XOR with the configured key
        
        Args:
            plaintext: Text to encrypt (e.g., DoodStream link)
            
        Returns:
            Hex-encoded encrypted string
        """
        plaintext_bytes = plaintext.encode('utf-8')
        encrypted = bytearray()
        
        for i, byte in enumerate(plaintext_bytes):
            key_byte = self.key_bytes[i % len(self.key_bytes)]
            encrypted.append(byte ^ key_byte)
        
        return encrypted.hex()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext using XOR with the configured key
        
        Args:
            ciphertext: Hex-encoded encrypted string
            
        Returns:
            Decrypted plaintext
        """
        try:
            ciphertext_bytes = bytes.fromhex(ciphertext)
            decrypted = bytearray()
            
            for i, byte in enumerate(ciphertext_bytes):
                key_byte = self.key_bytes[i % len(self.key_bytes)]
                decrypted.append(byte ^ key_byte)
            
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def encrypt_password(self, password: str) -> str:
        """
        Create a secure hash of password using SHA-256
        
        Args:
            password: Password to hash
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        password_bytes = password.encode('utf-8')
        hash_object = hashlib.sha256(password_bytes)
        return hash_object.hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against stored hash
        
        Args:
            password: Password to verify
            password_hash: Stored password hash
            
        Returns:
            True if password matches hash, False otherwise
        """
        return self.encrypt_password(password) == password_hash


class EncryptionManager:
    """Manages encryption/decryption operations for the automation system"""
    
    def __init__(self, xor_key: str, hash_key: str):
        """
        Initialize encryption manager with keys
        
        Args:
            xor_key: Key for XOR encryption
            hash_key: Key for password hashing (currently unused, for future expansion)
        """
        self.xor = XOREncryption(xor_key)
        self.hash_key = hash_key
    
    def encrypt_link(self, link: str) -> str:
        """Encrypt a DoodStream link"""
        return self.xor.encrypt(link)
    
    def decrypt_link(self, encrypted_link: str) -> str:
        """Decrypt a DoodStream link"""
        return self.xor.decrypt(encrypted_link)
    
    def create_password_hash(self, password: str) -> str:
        """Create password hash"""
        return self.xor.encrypt_password(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password"""
        return self.xor.verify_password(password, password_hash)


# Test encryption/decryption
if __name__ == "__main__":
    from config import XOR_ENCRYPTION_KEY, PASSWORD_HASH_KEY
    
    manager = EncryptionManager(XOR_ENCRYPTION_KEY, PASSWORD_HASH_KEY)
    
    # Test link encryption
    test_link = "https://myvidplay.com/d/ywike1tso4l6"
    encrypted = manager.encrypt_link(test_link)
    decrypted = manager.decrypt_link(encrypted)
    
    print("=== XOR Encryption Test ===")
    print(f"Original:  {test_link}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_link == decrypted}")
    
    # Test password hashing
    print("\n=== Password Hash Test ===")
    password = "TestPassword123"
    password_hash = manager.create_password_hash(password)
    print(f"Password: {password}")
    print(f"Hash: {password_hash}")
    print(f"Verify: {manager.verify_password(password, password_hash)}")
    print(f"Wrong password: {manager.verify_password('WrongPassword', password_hash)}")
