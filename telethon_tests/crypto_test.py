import unittest

import telethon.helpers as utils
from telethon.crypto import AES, Factorization


class CryptoTests(unittest.TestCase):
    def setUp(self):
        # Test known values
        self.key = b'\xd1\xf4MXy\x0c\xf8/z,\xe9\xf9\xa4\x17\x04\xd9C\xc9\xaba\x81\xf3\xf8\xdd\xcb\x0c6\x92\x01\x1f\xc2y'
        self.iv = b':\x02\x91x\x90Dj\xa6\x03\x90C\x08\x9e@X\xb5E\xffwy\xf3\x1c\xde\xde\xfbo\x8dm\xd6e.Z'

        self.plain_text = b'Non encrypted text :D'
        self.plain_text_padded = b'My len is more uniform, promise!'

        self.cipher_text = b'\xb6\xa7\xec.\xb9\x9bG\xcb\xe9{\x91[\x12\xfc\x84D\x1c' \
                           b'\x93\xd9\x17\x03\xcd\xd6\xb1D?\x98\xd2\xb5\xa5U\xfd'

        self.cipher_text_padded = b"W\xd1\xed'\x01\xa6c\xc3\xcb\xef\xaa\xe5\x1d\x1a" \
                                  b"[\x1b\xdf\xcdI\x1f>Z\n\t\xb9\xd2=\xbaF\xd1\x8e'"

    @staticmethod
    def test_sha1():
        string = 'Example string'

        hash_sum = utils.sha1(string.encode('utf-8'))
        expected = b'\nT\x92|\x8d\x06:)\x99\x04\x8e\xf8j?\xc4\x8e\xd3}m9'

        assert hash_sum == expected, 'Invalid sha1 hash_sum representation (should be {}, but is {})'\
            .format(expected, hash_sum)

    def test_aes_encrypt(self):
        value = AES.encrypt_ige(self.plain_text, self.key, self.iv)
        take = 16  # Don't take all the bytes, since latest involve are random padding
        assert value[:take] == self.cipher_text[:take],\
            ('Ciphered text ("{}") does not equal expected ("{}")'
             .format(value[:take], self.cipher_text[:take]))

        value = AES.encrypt_ige(self.plain_text_padded, self.key, self.iv)
        assert value == self.cipher_text_padded, (
            'Ciphered text ("{}") does not equal expected ("{}")'
            .format(value, self.cipher_text_padded))

    def test_aes_decrypt(self):
        # The ciphered text must always be padded
        value = AES.decrypt_ige(self.cipher_text_padded, self.key, self.iv)
        assert value == self.plain_text_padded, (
            'Decrypted text ("{}") does not equal expected ("{}")'
            .format(value, self.plain_text_padded))

    @staticmethod
    def test_calc_key():
        shared_key = b'\xbc\xd2m\xb7\xcav\xf4][\x88\x83\' \xf3\x11\x8as\xd04\x941\xae' \
                     b'*O\x03\x86\x9a/H#\x1a\x8c\xb5j\xe9$\xe0IvCm^\xe70\x1a5C\t\x16' \
                     b'\x03\xd2\x9d\xa9\x89\xd6\xce\x08P\x0fdr\xa0\xb3\xeb\xfecv\x1a' \
                     b'\xdfJ\x14\x96\x98\x16\xa3G\xab\x04\x14!\\\xeb\n\xbcn\xdf\xc4%' \
                     b'\xc6\t\xb7\x16\x14\x9c\'\x81\x15=\xb0\xaf\x0e\x0bR\xaa\x0466s' \
                     b'\xf0\xcf\xb7\xb8>,D\x94x\xd7\xf8\xe0\x84\xcb%\xd3\x05\xb2\xe8' \
                     b'\x95Mr?\xa2\xe8In\xf9\x0b[E\x9b\xaa\x0cX\x7f\x0ei\xde\xeed\x1d' \
                     b'x/J\xce\xea^}0;\xa83B\xbbR\xa1\xbfe\x04\xb9\x1e\xa1"f=\xa5M@' \
                     b'\x9e\xdd\x81\x80\xc9\xa5\xfb\xfcg\xdd\x15\x03p!\x0ffD\x16\x892' \
                     b'\xea\xca\xb1A\x99O\xa94P\xa9\xa2\xc6;\xb2C9\x1dC5\xd2\r\xecL' \
                     b'\xd9\xabw-\x03\ry\xc2v\x17]\x02\x15\x0cBa\x97\xce\xa5\xb1\xe4]' \
                     b'\x8e\xe0,\xcfC{o\xfa\x99f\xa4pM\x00'

        # Calculate key being the client
        msg_key = b'\xba\x1a\xcf\xda\xa8^Cbl\xfa\xb6\x0c:\x9b\xb0\xfc'

        key, iv = utils.calc_key(shared_key, msg_key, client=True)
        expected_key = b"\xaf\xe3\x84Qm\xe0!\x0c\xd91\xe4\x9a\xa0v_gc" \
                       b"x\xa1\xb0\xc9\xbc\x16'v\xcf,\x9dM\xae\xc6\xa5"

        expected_iv = b'\xb8Q\xf3\xc5\xa3]\xc6\xdf\x9e\xe0Q\xbd"\x8d' \
                      b'\x13\t\x0e\x9a\x9d^8\xa2\xf8\xe7\x00w\xd9\xc1' \
                      b'\xa7\xa0\xf7\x0f'

        assert key == expected_key, 'Invalid key (expected ("{}"), got ("{}"))'.format(
            expected_key, key)
        assert iv == expected_iv, 'Invalid IV (expected ("{}"), got ("{}"))'.format(
            expected_iv, iv)

        # Calculate key being the server
        msg_key = b'\x86m\x92i\xcf\x8b\x93\xaa\x86K\x1fi\xd04\x83]'

        key, iv = utils.calc_key(shared_key, msg_key, client=False)
        expected_key = b'\xdd0X\xb6\x93\x8e\xc9y\xef\x83\xf8\x8cj' \
                       b'\xa7h\x03\xe2\xc6\xb16\xc5\xbb\xfc\xe7' \
                       b'\xdf\xd6\xb1g\xf7u\xcfk'

        expected_iv = b'\xdcL\xc2\x18\x01J"X\x86lb\xb6\xb547\xfd' \
                      b'\xe2a4\xb6\xaf}FS\xd7[\xe0N\r\x19\xfb\xbc'

        assert key == expected_key, 'Invalid key (expected ("{}"), got ("{}"))'.format(
            expected_key, key)
        assert iv == expected_iv, 'Invalid IV (expected ("{}"), got ("{}"))'.format(
            expected_iv, iv)

    @staticmethod
    def test_calc_msg_key():
        value = utils.calc_msg_key(b'Some random message')
        expected = b'\xdfAa\xfc\x10\xab\x89\xd2\xfe\x19C\xf1\xdd~\xbf\x81'
        assert value == expected, 'Value ("{}") does not equal expected ("{}")'.format(
            value, expected)

    @staticmethod
    def test_generate_key_data_from_nonce():
        server_nonce = b'I am the server nonce.'
        new_nonce = b'I am a new calculated nonce.'

        key, iv = utils.generate_key_data_from_nonce(server_nonce, new_nonce)
        expected_key = b'?\xc4\xbd\xdf\rWU\x8a\xf5\x0f+V\xdc\x96up\x1d\xeeG\x00\x81|\x1eg\x8a\x8f{\xf0y\x80\xda\xde'
        expected_iv = b'Q\x9dpZ\xb7\xdd\xcb\x82_\xfa\xf4\x90\xecn\x10\x9cD\xd2\x01\x8d\x83\xa0\xa4^\xb8\x91,\x7fI am'

        assert key == expected_key, 'Key ("{}") does not equal expected ("{}")'.format(
            key, expected_key)
        assert iv == expected_iv, 'Key ("{}") does not equal expected ("{}")'.format(
            key, expected_iv)

    @staticmethod
    def test_factorize():
        pq = 3118979781119966969
        p, q = Factorization.factorize(pq)

        assert p == 1719614201, 'Factorized pair did not yield the correct result'
        assert q == 1813767169, 'Factorized pair did not yield the correct result'
