import calendar
import unicodedata
from datetime import datetime

import base64
import hmac
import os
import re
import struct
from Crypto.Cipher import AES
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils.crypto import pbkdf2
from hashlib import sha256

from sana_pchr.settings import CRYPTO_KEY_SIZE


class Credential:
    class AuthenticationException(Exception):
        pass

    def __init__(self, key):
        assert len(key) == CRYPTO_KEY_SIZE, "Key length incorrect, expected %d" % CRYPTO_KEY_SIZE
        self._key = bytes(key)

    @staticmethod
    def generate():
        return Credential(os.urandom(CRYPTO_KEY_SIZE))

    @property
    def key(self):
        return self._key

    # Wrapped all the references to key and plaintext into bytes() in order to get
    # it working with python 3.4.3
    @classmethod
    def encrypt_with_key(cls, key, plaintext, authenticate=True):
        ''' Encrypt the given plaintext with our key '''
        iv = os.urandom(16)
        aes = AES.new(bytes(key), AES.MODE_CBC, iv)
        padded = bytes(plaintext) + ((16 - len(plaintext) % 16) * chr(16 - len(plaintext) % 16)).encode("ascii")
        ciphertext = aes.encrypt(padded)
        timestamp = struct.pack("<I", calendar.timegm(datetime.utcnow().utctimetuple()))
        mac = b''
        if authenticate:
            mac = hmac.HMAC(bytes(key), timestamp + iv + ciphertext, sha256).digest()
        return mac + timestamp + iv + ciphertext

    def encrypt(self, plaintext, authenticate=True):
        return Credential.encrypt_with_key(self._key, plaintext, authenticate)

    @classmethod
    def decrypt_with_key(cls, key, data, authenticate=True):
        ''' Optionally verify, then decrypt the given data with our key '''
        if authenticate:
            mac = data[:32]
            timestamp = data[32:36]
            iv = data[36:52]
            ciphertext = data[52:]

            ref_mac = hmac.HMAC(key, timestamp + iv + ciphertext, sha256).digest()
            if mac != ref_mac:
                raise Credential.AuthenticationException("HMAC authentication failed")
        else:
            iv = data[4:20]
            ciphertext = data[20:]
        aes = AES.new(bytes(key), AES.MODE_CBC, iv)
        padded = aes.decrypt(ciphertext)
        plaintext = padded[:-padded[-1]]
        return plaintext

    def decrypt(self, data, authenticate=True):
        return Credential.decrypt_with_key(self._key, data, authenticate)


class DerivedCredential(Credential):
    ''' Like a Credential, but you can use a plaintext key
        Note that encrypt & decrypt now real in plaintext in the style of Django's password hashing
          i.e. algm$iter$salt$data
        This has some probably-too-magical logic to allow for decryption of different iteration coun
    '''

    algorithm = 'pbkdf2_sha256'

    def __init__(self, passphrase=None, key=None, salt=None, iterations=None):
        assert (passphrase is not None) ^ (key is not None and salt is not None and iterations is not None)
        self._passphrase = passphrase
        self._key = key
        self._salt = salt if salt else PBKDF2PasswordHasher().salt()
        self._iterations = iterations if iterations else PBKDF2PasswordHasher.iterations
        if not self._key:
            self._key = pbkdf2(self.passphrase, self._salt, self._iterations, digest=PBKDF2PasswordHasher.digest,
                               dklen=CRYPTO_KEY_SIZE)
        super(DerivedCredential, self).__init__(self.key)

    @property
    def passphrase(self):
        return self._passphrase

    @property
    def salt(self):
        return self._salt

    @property
    def iterations(self):
        return self._iterations

    def encrypt(self, data, authenticate=True):
        encrypted = Credential.encrypt_with_key(self.key, data, authenticate=authenticate)
        return "%s$%d$%s$%s" % (
            self.algorithm, self._iterations, self._salt, base64.b64encode(encrypted).decode('ascii').strip())

    def decrypt(self, data, authenticate=True):
        algorithm, iterations, salt, blob = data.split('$', 3)
        iterations = int(iterations)
        assert algorithm == self.algorithm
        if salt == self.salt and iterations == self.iterations:
            key = self.key
        else:
            key = pbkdf2(self.passphrase, salt, iterations, digest=PBKDF2PasswordHasher.digest, dklen=CRYPTO_KEY_SIZE)
        return Credential.decrypt_with_key(key, base64.b64decode(blob), authenticate=authenticate)


class NormalizedDerivedCredential:
    ''' Like a DerivedCredential, but normalizes the passphrase
        - Lowercase
        - Strip whitespace
        - Decompose diacritics
        - Strip diacritics
    '''

    def __new__(self, passphrase):
        passphrase = passphrase.lower()
        passphrase = re.sub("\s", "", passphrase)
        passphrase = unicodedata.normalize('NFD', passphrase)
        passphrase = re.sub(".", lambda s: "" if unicodedata.category(s.group(0)) == "Mn" else s.group(0), passphrase)
        return DerivedCredential(passphrase)
