from Crypto.Cipher import AES
import binascii
keystring = '00000000000000000000000000000000'
iostoken = '107005ed3f3845aea7696d838df8389385b88224e4696b2e78be02cfc83d4d770143db63ee66b0cdff9f69917680151e'
key = bytes.fromhex(keystring)
cipher = AES.new(key, AES.MODE_ECB)
token = cipher.decrypt(bytes.fromhex(iostoken[:64]))
print(token)