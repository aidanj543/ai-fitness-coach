from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    # TODO: Hash the password and return the hash
    pass

def verify_password(plain_password: str, hashed_password: str) -> bool:
    #TODO: Verify whether the password matches the hash
    pass