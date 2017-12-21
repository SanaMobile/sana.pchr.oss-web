from django.test import TestCase
from sana_pchr.crypto import Credential, DerivedCredential, NormalizedDerivedCredential
from unittest.mock import patch


class CryptoTestCase(TestCase):
    def test_keygen(self):
        credential = Credential.generate()
        credential_2 = Credential.generate()
        self.assertEqual(len(credential.key), 32)
        self.assertNotEqual(credential.key, credential_2.key)

    def test_encryption(self):
        credential = Credential.generate()
        result = credential.encrypt('bob'.encode('ascii'))
        recovered = credential.decrypt(result).decode('ascii')
        self.assertEqual(recovered, 'bob')

    @patch('os.urandom', side_effect=lambda x: b'q' * x)
    def test_unauthenticated_encryption(self, _):
        credential = Credential.generate()
        result = credential.encrypt('bobbery'.encode('ascii'), authenticate=False)
        # 1) Replace the 1st byte of the IV
        result = result[:4] + b'a' + result[5:]
        # 2) ???
        recovered = credential.decrypt(result, authenticate=False).decode('ascii')
        # 3) Profit!
        self.assertEqual(recovered, 'robbery')

    @patch('os.urandom', side_effect=lambda x: b'q' * x)
    def test_authenticated_encryption(self, _):
        credential = Credential.generate()
        result = credential.encrypt('bobbery'.encode('ascii'))
        result = result[:36] + b'a' + result[37:]
        self.assertRaises(credential.AuthenticationException, credential.decrypt, result)

    def test_random_iv(self):
        credential = Credential.generate()
        result = credential.encrypt('bob'.encode('ascii'))
        result2 = credential.encrypt('bob'.encode('ascii'))
        self.assertNotEqual(result, result2)


class DerivedCryptoTestCase(TestCase):
    def test_derived(self):
        credential = DerivedCredential('test')
        result = credential.encrypt('bob'.encode('ascii'))
        credential_2 = DerivedCredential('test')
        recovered = credential_2.decrypt(result).decode('ascii')
        self.assertEqual(recovered, 'bob')

    def test_derived_bad_passphrase(self):
        credential = DerivedCredential('test')
        result = credential.encrypt('bob'.encode('ascii'))
        credential_2 = DerivedCredential('test2')
        self.assertRaises(credential.AuthenticationException, credential_2.decrypt, result)


@patch('sana_pchr.crypto.DerivedCredential')
class NormalizedDerivedCryptoTestCase(TestCase):
    def test_no_normalization(self, mock_cred):
        NormalizedDerivedCredential('hello')
        NormalizedDerivedCredential('hello')
        self.assertEqual(mock_cred.call_args_list[0], mock_cred.call_args_list[1])

    def test_normalization_caps(self, mock_cred):
        NormalizedDerivedCredential('31 april 2013')
        NormalizedDerivedCredential('31 April 2013')
        self.assertEqual(mock_cred.call_args_list[0], mock_cred.call_args_list[1])

    def test_normalization_spacing(self, mock_cred):
        NormalizedDerivedCredential('thank you')
        NormalizedDerivedCredential('thankyou')
        self.assertEqual(mock_cred.call_args_list[0], mock_cred.call_args_list[1])

    def test_normalization_unicode(self, mock_cred):
        NormalizedDerivedCredential('québécois')
        NormalizedDerivedCredential('québécois')
        self.assertEqual(mock_cred.call_args_list[0], mock_cred.call_args_list[1])

    def test_normalized_diacritics(self, mock_cred):
        NormalizedDerivedCredential('شُكْرًا')
        NormalizedDerivedCredential('شكرا')
        self.assertEqual(mock_cred.call_args_list[0], mock_cred.call_args_list[1])

    def test_too_far(self, mock_cred):
        NormalizedDerivedCredential('شُكْرًا')
        NormalizedDerivedCredential('شكر')
        self.assertNotEqual(mock_cred.call_args_list[0], mock_cred.call_args_list[1])
