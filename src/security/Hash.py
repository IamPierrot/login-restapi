import bcrypt

origin_salt = bytes(b'$2b$12$sdN980kInBCb7A0xkWKph.')

class Hashing:
    salt: bytes = origin_salt
    
    def __new__(cls, password: str | dict) -> bytes:
        encodedPw = str(password).encode('utf-8')
        pwHashed = bcrypt.hashpw(encodedPw, cls.salt)
        return pwHashed
    
    @classmethod
    def check_password(cls, password_db: bytes, client_input_password: str) -> bool:
        return password_db == Hashing(client_input_password)