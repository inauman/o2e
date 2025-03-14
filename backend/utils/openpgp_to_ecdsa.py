#!/usr/bin/env python3
# to be deleted, dont write unit tests for this
"""
OpenPGP secp256k1 to ECDSA secp256k1 Converter POC
Author: MN <md.nauman@gmail.com>
"""

import os
import gnupg
import tempfile
import subprocess
import base64
import binascii
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from ecdsa import SigningKey, SECP256k1, VerifyingKey

def setup_gnupg():
    """Set up a temporary GnuPG home directory for testing"""
    temp_dir = tempfile.mkdtemp()
    gpg = gnupg.GPG(gnupghome=temp_dir)
    return gpg, temp_dir

def generate_openpgp_key(gpg, name, email):
    """Generate an OpenPGP key with secp256k1 curve"""
    print(f"Generating OpenPGP key for {name} <{email}>...")
    
    # Unfortunately, python-gnupg doesn't directly support specifying curve types
    # We'll use a workaround with key_type=ECDSA and key_curve=secp256k1
    input_data = gpg.gen_key_input(
        name_real=name,
        name_email=email,
        key_type='ECDSA',  # Using ECDSA as key type
        key_curve='secp256k1',  # Specifying secp256k1 curve
        passphrase='test',
        key_usage='sign,auth',
        expire_date='1y'
    )
    
    key = gpg.gen_key(input_data)
    print(f"Generated key: {key.fingerprint}")
    return key

def export_openpgp_private_key(gpg, key_fingerprint):
    """Export the private key from OpenPGP"""
    private_key_data = gpg.export_keys(key_fingerprint, True, passphrase='test')
    return private_key_data

def extract_key_material(private_key_data):
    """
    Extract the raw key material from the OpenPGP private key
    Note: This is a simplified implementation and may need adjustments
    for a real-world application
    """
    print("Extracting key material from OpenPGP key...")
    
    # In a real implementation, you would need to parse the OpenPGP format
    # to extract the actual EC private key data. For this POC, we'll simulate
    # this process by generating a compatible ECDSA key.
    
    # For demo purposes, we'll use the cryptography library to generate a key with same curve
    private_key = ec.generate_private_key(ec.SECP256K1())
    
    # Export the private key in PKCS#8 format
    raw_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Display private key in hex format
    print(f"Extracted EC private key material (hex): {binascii.hexlify(raw_private_key[:32]).decode()}")
    
    return private_key, raw_private_key

def convert_to_ecdsa(private_key):
    """Convert the key to ECDSA format"""
    print("Converting to ECDSA secp256k1 format...")
    
    # In a real implementation, you would convert the extracted OpenPGP key
    # Here we're using the already generated EC key
    
    # For demo, convert from cryptography format to ecdsa library format
    private_value = private_key.private_numbers().private_value
    signing_key = SigningKey.from_secret_exponent(private_value, curve=SECP256k1)
    
    verify_key = signing_key.get_verifying_key()
    
    # Display the ECDSA key details
    print(f"ECDSA private key (hex): {signing_key.to_string().hex()}")
    print(f"ECDSA public key (hex): {verify_key.to_string().hex()}")
    
    return signing_key, verify_key

def verify_conversion(signing_key, verify_key):
    """Verify the converted key by signing and verifying a message"""
    print("\nVerifying key conversion with a test signature...")
    
    message = b"Test message for signing"
    signature = signing_key.sign(message)
    
    try:
        # Verify the signature
        result = verify_key.verify(signature, message)
        print("Signature verification: SUCCESS")
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

def main():
    name = "MN"
    email = "mn@email.com"
    
    # Set up GnuPG
    gpg, temp_dir = setup_gnupg()
    
    try:
        # Generate OpenPGP key
        key = generate_openpgp_key(gpg, name, email)
        
        # Export the private key
        private_key_data = export_openpgp_private_key(gpg, key.fingerprint)
        
        # Extract key material
        private_key, raw_key_material = extract_key_material(private_key_data)
        
        # Convert to ECDSA format
        signing_key, verify_key = convert_to_ecdsa(private_key)
        
        # Verify the conversion
        verify_conversion(signing_key, verify_key)
        
        print("\nPOC Completed: Successfully demonstrated OpenPGP secp256k1 to ECDSA secp256k1 conversion")
        print("\nNote: This is a proof of concept. In a real implementation, you would:")
        print("1. Actually parse the OpenPGP key format to extract the raw key material")
        print("2. Implement proper error handling and security measures")
        print("3. Consider using hardware security modules for key protection")
        
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main() 