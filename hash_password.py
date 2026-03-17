from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

hashed = password_hash.hash("mysecretpassword")
print(hashed)
print(password_hash.verify("mysecretpassword", hashed))