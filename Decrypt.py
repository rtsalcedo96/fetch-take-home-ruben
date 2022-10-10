from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP

# DECRYPTION CODE BLOCK MAKE SURE TO DOUBLE CHECK BETWEEN DATA2 AND CIPHERTEXT2 VARIABLES FOR IP AND DEVICE_ID
file_in = open("encrypted_data.bin", "rb")

private_key = RSA.import_key(open("private.pem").read())

enc_session_key, nonce, tag, ciphertext2 = \
   [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

# Decrypt the session key with the private RSA key
cipher_rsa = PKCS1_OAEP.new(private_key)
session_key = cipher_rsa.decrypt(enc_session_key)

# Decrypt the data with the AES session key
cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
data2 = cipher_aes.decrypt_and_verify(ciphertext2, tag)

print(data2.decode("utf-8"))

#  lines 6-21 can be copied to main.py to double check decryption in code