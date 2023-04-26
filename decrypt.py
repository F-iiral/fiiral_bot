from cryptography.fernet import Fernet

encrypted = input("Key?")
key = Fernet(b'bQG938RWdMyECb7Mujsz6bgcYmxnSIT1FNYjK5u-w-4=')

print(int(key.decrypt(encrypted)))