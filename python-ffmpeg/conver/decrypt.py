import base64
# pip install pycryptodomex
from Cryptodome.Cipher import AES
import json
import secrets

def decrypt(key,text, iv):
    unpad = lambda s: s[0:-ord(s[-1:])]
    decode = base64.b64decode(text)
    cryptor = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    plain_text = cryptor.decrypt(decode)
    return unpad(plain_text).decode('utf-8')


if __name__ == '__main__':
    # 5分钟有效期
    for num in range(10, 20):
        randomPath = secrets.token_urlsafe(16)
        print(randomPath[0:16])
    randomPath = secrets.token_urlsafe(16)
    print(randomPath)
    d = decrypt('9fZKCo7graLa7geF','3kg1CCWafDjUGs46Pa3F9K3TiBEdh6FeZVSUThlwA5yTNed0XjofWWC/yyJfZyDM',
                'MFEuniyz1fvnG5NI')

    print(d)
    h = json.loads(d)
    print(h)
    try:
        s = h['t']

        print(h['t'])
        print(h['key'])
    except:
        pass
