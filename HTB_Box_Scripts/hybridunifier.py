import requests
import json
import random
from base64 import b64encode as be, b64decode as bd
from Crypto.Util.number import getPrime, long_to_bytes as l2b
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from secrets import randbelow
from hashlib import sha256
import os

URL = 'http://localhost:1337'
#r = requests.post(f'{URL}/a-cool-endpoint', json={'key1': 'json', 'key2': 'data'})
#print(r.content)

print("Initializing Diffie-Hellman Key Exchange...")

r = requests.post(f'{URL}/api/request-session-parameters')
session_params = json.loads(r.content)
print("API response: {}".format(r.content))
g = session_params["g"]
p = session_params["p"]
print("generator (g): {} int: {}".format(g, int(g, 16)))
print("prime number (p): {} int: {}".format(p, int(p, 16)))

a = random.getrandbits(64)

# Use python's modular exponentiation
public_integer = pow(int(g, 16), a, int(p, 16))
print("Generated OUR public key (A): {}".format(hex(public_integer)))

print("Sending/Recieving public keys...")
r2 = requests.post(f'{URL}/api/init-session', json={'client_public_key': public_integer})
server_key_json = json.loads(r2.content)
print("API response: {}".format(r2.content))
server_public_integer = int(server_key_json["server_public_key"], 16) #This is B

shared_secret = pow(server_public_integer, a, int(p, 16))
session_key = sha256(str(shared_secret).encode()).digest()
print("Shared Secret: {}".format(shared_secret))

print("Requesting challenge...")
r3 = requests.post(f'{URL}/api/request-challenge')
print("API response: {}".format(r3.content))
challenge_json = json.loads(r3.content)
challenge = challenge_json["encrypted_challenge"]
print("Challenge: {}".format(challenge))



challenge_raw = bd(challenge)
iv = challenge_raw[:16]
cipher = AES.new(session_key, AES.MODE_CBC, iv)
decrypted_challenge = unpad(cipher.decrypt(challenge_raw[16:]), 16)
challenge_response = sha256(decrypted_challenge).hexdigest()

def encrypt_packet(packet):
    iv = os.urandom(16)
    cipher = AES.new(session_key, AES.MODE_CBC, iv)
    encrypted_packet = iv + cipher.encrypt(pad(packet.encode(), 16))
    return be(encrypted_packet).decode()

def decrypt_packet(packet):
    decoded_packet = bd(packet)        # base64 decode first
    iv = decoded_packet[:16]
    ciphertext = decoded_packet[16:]
    cipher = AES.new(session_key, AES.MODE_CBC, iv)
    try:
        decrypted_packet = unpad(cipher.decrypt(ciphertext), 16)
        return decrypted_packet.decode()
    except:
        return {'error': 'Malformed packet.'}

print("Requesting flag...")
r4 = requests.post(f'{URL}/api/dashboard', json={'challenge': challenge_response, 'packet_data': encrypt_packet("flag")})
print("API response: {}".format(r4.content))
response_json = json.loads(r4.content)
flag_decoded = decrypt_packet(response_json["packet_data"])
print("Flag:", flag_decoded)
