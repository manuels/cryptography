# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import textwrap

import pretend

import pytest

from .utils import (
    load_nist_vectors, load_vectors_from_file, load_cryptrec_vectors,
    load_openssl_vectors, load_hash_vectors, check_for_iface,
    check_backend_support, select_backends, load_pkcs1_vectors
)


class FakeInterface(object):
    pass


def test_select_one_backend():
    b1 = pretend.stub(name="b1")
    b2 = pretend.stub(name="b2")
    b3 = pretend.stub(name="b3")
    backends = [b1, b2, b3]
    name = "b2"
    selected_backends = select_backends(name, backends)
    assert len(selected_backends) == 1
    assert selected_backends[0] == b2


def test_select_no_backend():
    b1 = pretend.stub(name="b1")
    b2 = pretend.stub(name="b2")
    b3 = pretend.stub(name="b3")
    backends = [b1, b2, b3]
    name = "back!"
    with pytest.raises(ValueError):
        select_backends(name, backends)


def test_select_backends_none():
    b1 = pretend.stub(name="b1")
    b2 = pretend.stub(name="b2")
    b3 = pretend.stub(name="b3")
    backends = [b1, b2, b3]
    name = None
    selected_backends = select_backends(name, backends)
    assert len(selected_backends) == 3


def test_select_two_backends():
    b1 = pretend.stub(name="b1")
    b2 = pretend.stub(name="b2")
    b3 = pretend.stub(name="b3")
    backends = [b1, b2, b3]
    name = "b2 ,b1 "
    selected_backends = select_backends(name, backends)
    assert len(selected_backends) == 2
    assert selected_backends == [b1, b2]


def test_check_for_iface():
    item = pretend.stub(keywords=["fake_name"], funcargs={"backend": True})
    with pytest.raises(pytest.skip.Exception) as exc_info:
        check_for_iface("fake_name", FakeInterface, item)
    assert exc_info.value.args[0] == "True backend does not support fake_name"

    item = pretend.stub(
        keywords=["fake_name"],
        funcargs={"backend": FakeInterface()}
    )
    check_for_iface("fake_name", FakeInterface, item)


def test_check_backend_support_skip():
    supported = pretend.stub(
        kwargs={"only_if": lambda backend: False, "skip_message": "Nope"}
    )
    item = pretend.stub(keywords={"supported": supported},
                        funcargs={"backend": True})
    with pytest.raises(pytest.skip.Exception) as exc_info:
        check_backend_support(item)
    assert exc_info.value.args[0] == "Nope (True)"


def test_check_backend_support_no_skip():
    supported = pretend.stub(
        kwargs={"only_if": lambda backend: True, "skip_message": "Nope"}
    )
    item = pretend.stub(keywords={"supported": supported},
                        funcargs={"backend": True})
    assert check_backend_support(item) is None


def test_check_backend_support_no_backend():
    supported = pretend.stub(
        kwargs={"only_if": "notalambda", "skip_message": "Nope"}
    )
    item = pretend.stub(keywords={"supported": supported},
                        funcargs={})
    with pytest.raises(ValueError):
        check_backend_support(item)


def test_load_nist_vectors():
    vector_data = textwrap.dedent("""
    # CAVS 11.1
    # Config info for aes_values
    # AESVS GFSbox test data for CBC
    # State : Encrypt and Decrypt
    # Key Length : 128
    # Generated on Fri Apr 22 15:11:33 2011

    [ENCRYPT]

    COUNT = 0
    KEY = 00000000000000000000000000000000
    IV = 00000000000000000000000000000000
    PLAINTEXT = f34481ec3cc627bacd5dc3fb08f273e6
    CIPHERTEXT = 0336763e966d92595a567cc9ce537f5e

    COUNT = 1
    KEY = 00000000000000000000000000000000
    IV = 00000000000000000000000000000000
    PLAINTEXT = 9798c4640bad75c7c3227db910174e72
    CIPHERTEXT = a9a1631bf4996954ebc093957b234589

    [DECRYPT]

    COUNT = 0
    KEY = 00000000000000000000000000000000
    IV = 00000000000000000000000000000000
    CIPHERTEXT = 0336763e966d92595a567cc9ce537f5e
    PLAINTEXT = f34481ec3cc627bacd5dc3fb08f273e6

    COUNT = 1
    KEY = 00000000000000000000000000000000
    IV = 00000000000000000000000000000000
    CIPHERTEXT = a9a1631bf4996954ebc093957b234589
    PLAINTEXT = 9798c4640bad75c7c3227db910174e72
    """).splitlines()

    assert load_nist_vectors(vector_data) == [
        {
            "key": b"00000000000000000000000000000000",
            "iv": b"00000000000000000000000000000000",
            "plaintext": b"f34481ec3cc627bacd5dc3fb08f273e6",
            "ciphertext": b"0336763e966d92595a567cc9ce537f5e",
        },
        {
            "key": b"00000000000000000000000000000000",
            "iv": b"00000000000000000000000000000000",
            "plaintext": b"9798c4640bad75c7c3227db910174e72",
            "ciphertext": b"a9a1631bf4996954ebc093957b234589",
        },
        {
            "key": b"00000000000000000000000000000000",
            "iv": b"00000000000000000000000000000000",
            "plaintext": b"f34481ec3cc627bacd5dc3fb08f273e6",
            "ciphertext": b"0336763e966d92595a567cc9ce537f5e",
        },
        {
            "key": b"00000000000000000000000000000000",
            "iv": b"00000000000000000000000000000000",
            "plaintext": b"9798c4640bad75c7c3227db910174e72",
            "ciphertext": b"a9a1631bf4996954ebc093957b234589",
        },
    ]


def test_load_nist_vectors_with_null_chars():
    vector_data = textwrap.dedent("""
    COUNT = 0
    KEY = thing\\0withnulls

    COUNT = 1
    KEY = 00000000000000000000000000000000
    """).splitlines()

    assert load_nist_vectors(vector_data) == [
        {
            "key": b"thing\x00withnulls",
        },
        {
            "key": b"00000000000000000000000000000000",
        },
    ]


def test_load_cryptrec_vectors():
    vector_data = textwrap.dedent("""
    # Vectors taken from http://info.isl.ntt.co.jp/crypt/eng/camellia/
    # Download is t_camelia.txt

    # Camellia with 128-bit key

    K No.001 : 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

    P No.001 : 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    C No.001 : 07 92 3A 39 EB 0A 81 7D 1C 4D 87 BD B8 2D 1F 1C

    P No.002 : 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    C No.002 : 48 CD 64 19 80 96 72 D2 34 92 60 D8 9A 08 D3 D3

    K No.002 : 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

    P No.001 : 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    C No.001 : 07 92 3A 39 EB 0A 81 7D 1C 4D 87 BD B8 2D 1F 1C
    """).splitlines()

    assert load_cryptrec_vectors(vector_data) == [
        {
            "key": b"00000000000000000000000000000000",
            "plaintext": b"80000000000000000000000000000000",
            "ciphertext": b"07923A39EB0A817D1C4D87BDB82D1F1C",
        },
        {
            "key": b"00000000000000000000000000000000",
            "plaintext": b"40000000000000000000000000000000",
            "ciphertext": b"48CD6419809672D2349260D89A08D3D3",
        },
        {
            "key": b"10000000000000000000000000000000",
            "plaintext": b"80000000000000000000000000000000",
            "ciphertext": b"07923A39EB0A817D1C4D87BDB82D1F1C",
        },
    ]


def test_load_cryptrec_vectors_invalid():
    vector_data = textwrap.dedent("""
    # Vectors taken from http://info.isl.ntt.co.jp/crypt/eng/camellia/
    # Download is t_camelia.txt

    # Camellia with 128-bit key

    E No.001 : 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    """).splitlines()

    with pytest.raises(ValueError):
        load_cryptrec_vectors(vector_data)


def test_load_openssl_vectors():
    vector_data = textwrap.dedent(
        """
        # We don't support CFB{1,8}-CAMELLIAxxx.{En,De}crypt
        # For all CFB128 encrypts and decrypts, the transformed sequence is
        #   CAMELLIA-bits-CFB:key:IV/ciphertext':plaintext:ciphertext:encdec
        # CFB128-CAMELLIA128.Encrypt
        """
        "CAMELLIA-128-CFB:2B7E151628AED2A6ABF7158809CF4F3C:"
        "000102030405060708090A0B0C0D0E0F:6BC1BEE22E409F96E93D7E117393172A:"
        "14F7646187817EB586599146B82BD719:1\n"
        "CAMELLIA-128-CFB:2B7E151628AED2A6ABF7158809CF4F3C:"
        "14F7646187817EB586599146B82BD719:AE2D8A571E03AC9C9EB76FAC45AF8E51:"
        "A53D28BB82DF741103EA4F921A44880B:1\n\n"
        "# CFB128-CAMELLIA128.Decrypt\n"
        "CAMELLIA-128-CFB:2B7E151628AED2A6ABF7158809CF4F3C:"
        "000102030405060708090A0B0C0D0E0F:6BC1BEE22E409F96E93D7E117393172A:"
        "14F7646187817EB586599146B82BD719:0\n"
        "CAMELLIA-128-CFB:2B7E151628AED2A6ABF7158809CF4F3C:"
        "14F7646187817EB586599146B82BD719:AE2D8A571E03AC9C9EB76FAC45AF8E51:"
        "A53D28BB82DF741103EA4F921A44880B:0"
    ).splitlines()

    assert load_openssl_vectors(vector_data) == [
        {
            "key": b"2B7E151628AED2A6ABF7158809CF4F3C",
            "iv": b"000102030405060708090A0B0C0D0E0F",
            "plaintext": b"6BC1BEE22E409F96E93D7E117393172A",
            "ciphertext": b"14F7646187817EB586599146B82BD719",
        },
        {
            "key": b"2B7E151628AED2A6ABF7158809CF4F3C",
            "iv": b"14F7646187817EB586599146B82BD719",
            "plaintext": b"AE2D8A571E03AC9C9EB76FAC45AF8E51",
            "ciphertext": b"A53D28BB82DF741103EA4F921A44880B",
        },
        {
            "key": b"2B7E151628AED2A6ABF7158809CF4F3C",
            "iv": b"000102030405060708090A0B0C0D0E0F",
            "plaintext": b"6BC1BEE22E409F96E93D7E117393172A",
            "ciphertext": b"14F7646187817EB586599146B82BD719",
        },
        {
            "key": b"2B7E151628AED2A6ABF7158809CF4F3C",
            "iv": b"14F7646187817EB586599146B82BD719",
            "plaintext": b"AE2D8A571E03AC9C9EB76FAC45AF8E51",
            "ciphertext": b"A53D28BB82DF741103EA4F921A44880B",
        },
    ]


def test_load_hash_vectors():
    vector_data = textwrap.dedent("""

        # http://tools.ietf.org/html/rfc1321
        [irrelevant]

        Len = 0
        Msg = 00
        MD = d41d8cd98f00b204e9800998ecf8427e

        Len = 8
        Msg = 61
        MD = 0cc175b9c0f1b6a831c399e269772661

        Len = 24
        Msg = 616263
        MD = 900150983cd24fb0d6963f7d28e17f72

        Len = 112
        Msg = 6d65737361676520646967657374
        MD = f96b697d7cb7938d525a2f31aaf161d0
    """).splitlines()
    assert load_hash_vectors(vector_data) == [
        (b"", "d41d8cd98f00b204e9800998ecf8427e"),
        (b"61", "0cc175b9c0f1b6a831c399e269772661"),
        (b"616263", "900150983cd24fb0d6963f7d28e17f72"),
        (b"6d65737361676520646967657374", "f96b697d7cb7938d525a2f31aaf161d0"),
    ]


def test_load_hmac_vectors():
    vector_data = textwrap.dedent("""
Len = 224
# "Jefe"
Key = 4a656665
# "what do ya want for nothing?"
Msg = 7768617420646f2079612077616e7420666f72206e6f7468696e673f
MD = 750c783e6ab0b503eaa86e310a5db738
    """).splitlines()
    assert load_hash_vectors(vector_data) == [
        (b"7768617420646f2079612077616e7420666f72206e6f7468696e673f",
         "750c783e6ab0b503eaa86e310a5db738",
         b"4a656665"),
    ]


def test_load_hash_vectors_bad_data():
    vector_data = textwrap.dedent("""
        # http://tools.ietf.org/html/rfc1321

        Len = 0
        Msg = 00
        UNKNOWN=Hello World
    """).splitlines()
    with pytest.raises(ValueError):
        load_hash_vectors(vector_data)


def test_load_vectors_from_file():
    vectors = load_vectors_from_file(
        os.path.join("ciphers", "Blowfish", "bf-cfb.txt"),
        load_nist_vectors,
    )
    assert vectors == [
        {
            "key": b"0123456789ABCDEFF0E1D2C3B4A59687",
            "iv": b"FEDCBA9876543210",
            "plaintext": (
                b"37363534333231204E6F77206973207468652074696D6520666F722000"
            ),
            "ciphertext": (
                b"E73214A2822139CAF26ECF6D2EB9E76E3DA3DE04D1517200519D57A6C3"
            ),
        }
    ]


def test_load_nist_gcm_vectors():
    vector_data = textwrap.dedent("""
        [Keylen = 128]
        [IVlen = 96]
        [PTlen = 0]
        [AADlen = 0]
        [Taglen = 128]

        Count = 0
        Key = 11754cd72aec309bf52f7687212e8957
        IV = 3c819d9a9bed087615030b65
        PT =
        AAD =
        CT =
        Tag = 250327c674aaf477aef2675748cf6971

        Count = 1
        Key = 272f16edb81a7abbea887357a58c1917
        IV = 794ec588176c703d3d2a7a07
        PT =
        AAD =
        CT =
        Tag = b6e6f197168f5049aeda32dafbdaeb

        Count = 2
        Key = a49a5e26a2f8cb63d05546c2a62f5343
        IV = 907763b19b9b4ab6bd4f0281
        CT =
        AAD =
        Tag = a2be08210d8c470a8df6e8fbd79ec5cf
        FAIL

        Count = 3
        Key = 5c1155084cc0ede76b3bc22e9f7574ef
        IV = 9549e4ba69a61cad7856efc1
        PT = d1448fa852b84408e2dad8381f363de7
        AAD = e98e9d9c618e46fef32660976f854ee3
        CT = f78b60ca125218493bea1c50a2e12ef4
        Tag = d72da7f5c6cf0bca7242c71835809449

        [Keylen = 128]
        [IVlen = 96]
        [PTlen = 0]
        [AADlen = 0]
        [Taglen = 120]

        Count = 0
        Key = eac258e99c55e6ae8ef1da26640613d7
        IV = 4e8df20faaf2c8eebe922902
        CT =
        AAD =
        Tag = e39aeaebe86aa309a4d062d6274339
        PT =

        Count = 1
        Key = 3726cf02fcc6b8639a5497652c94350d
        IV = 55fef82cde693ce76efcc193
        CT =
        AAD =
        Tag = 3d68111a81ed22d2ef5bccac4fc27f
        FAIL

        Count = 2
        Key = f202299d5fd74f03b12d2119a6c4c038
        IV = eec51e7958c3f20a1bb71815
        CT =
        AAD =
        Tag = a81886b3fb26e51fca87b267e1e157
        FAIL

        Count = 3
        Key = fd52925f39546b4c55ffb6b20c59898c
        IV = f5cf3227444afd905a5f6dba
        CT =
        AAD =
        Tag = 1665b0f1a0b456e1664cfd3de08ccd
        PT =

        [Keylen = 128]
        [IVlen = 8]
        [PTlen = 104]
        [AADlen = 0]
        [Taglen = 128]

        Count = 0
        Key = 58fab7632bcf10d2bcee58520bf37414
        IV = 3c
        CT = 15c4db4cbb451211179d57017f
        AAD =
        Tag = eae841d4355feeb3f786bc86625f1e5b
        FAIL
    """).splitlines()
    assert load_nist_vectors(vector_data) == [
        {'aad': b'',
         'pt': b'',
         'iv': b'3c819d9a9bed087615030b65',
         'tag': b'250327c674aaf477aef2675748cf6971',
         'key': b'11754cd72aec309bf52f7687212e8957',
         'ct': b''},
        {'aad': b'',
         'pt': b'',
         'iv': b'794ec588176c703d3d2a7a07',
         'tag': b'b6e6f197168f5049aeda32dafbdaeb',
         'key': b'272f16edb81a7abbea887357a58c1917',
         'ct': b''},
        {'aad': b'',
         'iv': b'907763b19b9b4ab6bd4f0281',
         'tag': b'a2be08210d8c470a8df6e8fbd79ec5cf',
         'key': b'a49a5e26a2f8cb63d05546c2a62f5343',
         'ct': b'',
         'fail': True},
        {'aad': b'e98e9d9c618e46fef32660976f854ee3',
         'pt': b'd1448fa852b84408e2dad8381f363de7',
         'iv': b'9549e4ba69a61cad7856efc1',
         'tag': b'd72da7f5c6cf0bca7242c71835809449',
         'key': b'5c1155084cc0ede76b3bc22e9f7574ef',
         'ct': b'f78b60ca125218493bea1c50a2e12ef4'},
        {'aad': b'',
         'pt': b'',
         'iv': b'4e8df20faaf2c8eebe922902',
         'tag': b'e39aeaebe86aa309a4d062d6274339',
         'key': b'eac258e99c55e6ae8ef1da26640613d7',
         'ct': b''},
        {'aad': b'',
         'iv': b'55fef82cde693ce76efcc193',
         'tag': b'3d68111a81ed22d2ef5bccac4fc27f',
         'key': b'3726cf02fcc6b8639a5497652c94350d',
         'ct': b'',
         'fail': True},
        {'aad': b'',
         'iv': b'eec51e7958c3f20a1bb71815',
         'tag': b'a81886b3fb26e51fca87b267e1e157',
         'key': b'f202299d5fd74f03b12d2119a6c4c038',
         'ct': b'',
         'fail': True},
        {'aad': b'',
         'pt': b'',
         'iv': b'f5cf3227444afd905a5f6dba',
         'tag': b'1665b0f1a0b456e1664cfd3de08ccd',
         'key': b'fd52925f39546b4c55ffb6b20c59898c',
         'ct': b''},
        {'aad': b'',
         'iv': b'3c',
         'tag': b'eae841d4355feeb3f786bc86625f1e5b',
         'key': b'58fab7632bcf10d2bcee58520bf37414',
         'ct': b'15c4db4cbb451211179d57017f',
         'fail': True},
    ]


def test_load_pkcs1_vectors():
    vector_data = textwrap.dedent("""
    Test vectors for RSA-PSS
    ========================

    This file contains an extract of the original pss-vect.txt

    Key lengths:

    Key  8: 1031 bits
    Key  9: 1536 bits
    ===========================================================================

    <snip>

    # Example 8: A 1031-bit RSA key pair
    # -----------------------------------


    # Public key
    # ----------

    # Modulus:
    49 53 70 a1 fb 18 54 3c 16 d3 63 1e 31 63 25 5d
    f6 2b e6 ee e8 90 d5 f2 55 09 e4 f7 78 a8 ea 6f
    bb bc df 85 df f6 4e 0d 97 20 03 ab 36 81 fb ba
    6d d4 1f d5 41 82 9b 2e 58 2d e9 f2 a4 a4 e0 a2
    d0 90 0b ef 47 53 db 3c ee 0e e0 6c 7d fa e8 b1
    d5 3b 59 53 21 8f 9c ce ea 69 5b 08 66 8e de aa
    dc ed 94 63 b1 d7 90 d5 eb f2 7e 91 15 b4 6c ad
    4d 9a 2b 8e fa b0 56 1b 08 10 34 47 39 ad a0 73
    3f

    # Exponent:
    01 00 01

    # Private key
    # -----------

    # Modulus:
    49 53 70 a1 fb 18 54 3c 16 d3 63 1e 31 63 25 5d
    f6 2b e6 ee e8 90 d5 f2 55 09 e4 f7 78 a8 ea 6f
    bb bc df 85 df f6 4e 0d 97 20 03 ab 36 81 fb ba
    6d d4 1f d5 41 82 9b 2e 58 2d e9 f2 a4 a4 e0 a2
    d0 90 0b ef 47 53 db 3c ee 0e e0 6c 7d fa e8 b1
    d5 3b 59 53 21 8f 9c ce ea 69 5b 08 66 8e de aa
    dc ed 94 63 b1 d7 90 d5 eb f2 7e 91 15 b4 6c ad
    4d 9a 2b 8e fa b0 56 1b 08 10 34 47 39 ad a0 73
    3f

    # Public exponent:
    01 00 01

    # Exponent:
    6c 66 ff e9 89 80 c3 8f cd ea b5 15 98 98 83 61
    65 f4 b4 b8 17 c4 f6 a8 d4 86 ee 4e a9 13 0f e9
    b9 09 2b d1 36 d1 84 f9 5f 50 4a 60 7e ac 56 58
    46 d2 fd d6 59 7a 89 67 c7 39 6e f9 5a 6e ee bb
    45 78 a6 43 96 6d ca 4d 8e e3 de 84 2d e6 32 79
    c6 18 15 9c 1a b5 4a 89 43 7b 6a 61 20 e4 93 0a
    fb 52 a4 ba 6c ed 8a 49 47 ac 64 b3 0a 34 97 cb
    e7 01 c2 d6 26 6d 51 72 19 ad 0e c6 d3 47 db e9

    # Prime 1:
    08 da d7 f1 13 63 fa a6 23 d5 d6 d5 e8 a3 19 32
    8d 82 19 0d 71 27 d2 84 6c 43 9b 0a b7 26 19 b0
    a4 3a 95 32 0e 4e c3 4f c3 a9 ce a8 76 42 23 05
    bd 76 c5 ba 7b e9 e2 f4 10 c8 06 06 45 a1 d2 9e
    db

    # Prime 2:
    08 47 e7 32 37 6f c7 90 0f 89 8e a8 2e b2 b0 fc
    41 85 65 fd ae 62 f7 d9 ec 4c e2 21 7b 97 99 0d
    d2 72 db 15 7f 99 f6 3c 0d cb b9 fb ac db d4 c4
    da db 6d f6 77 56 35 8c a4 17 48 25 b4 8f 49 70
    6d

    # Prime exponent 1:
    05 c2 a8 3c 12 4b 36 21 a2 aa 57 ea 2c 3e fe 03
    5e ff 45 60 f3 3d de bb 7a da b8 1f ce 69 a0 c8
    c2 ed c1 65 20 dd a8 3d 59 a2 3b e8 67 96 3a c6
    5f 2c c7 10 bb cf b9 6e e1 03 de b7 71 d1 05 fd
    85

    # Prime exponent 2:
    04 ca e8 aa 0d 9f aa 16 5c 87 b6 82 ec 14 0b 8e
    d3 b5 0b 24 59 4b 7a 3b 2c 22 0b 36 69 bb 81 9f
    98 4f 55 31 0a 1a e7 82 36 51 d4 a0 2e 99 44 79
    72 59 51 39 36 34 34 e5 e3 0a 7e 7d 24 15 51 e1
    b9

    # Coefficient:
    07 d3 e4 7b f6 86 60 0b 11 ac 28 3c e8 8d bb 3f
    60 51 e8 ef d0 46 80 e4 4c 17 1e f5 31 b8 0b 2b
    7c 39 fc 76 63 20 e2 cf 15 d8 d9 98 20 e9 6f f3
    0d c6 96 91 83 9c 4b 40 d7 b0 6e 45 30 7d c9 1f
    3f

    # RSA-PSS signing of 6 random messages with random salts
    # -------------------------------------------------------

    <snip>

    # =============================================

    # Example 9: A 1536-bit RSA key pair
    # -----------------------------------


    # Public key
    # ----------

    # Modulus:
    e6 bd 69 2a c9 66 45 79 04 03 fd d0 f5 be b8 b9
    bf 92 ed 10 00 7f c3 65 04 64 19 dd 06 c0 5c 5b
    5b 2f 48 ec f9 89 e4 ce 26 91 09 97 9c bb 40 b4
    a0 ad 24 d2 24 83 d1 ee 31 5a d4 cc b1 53 42 68
    35 26 91 c5 24 f6 dd 8e 6c 29 d2 24 cf 24 69 73
    ae c8 6c 5b f6 b1 40 1a 85 0d 1b 9a d1 bb 8c bc
    ec 47 b0 6f 0f 8c 7f 45 d3 fc 8f 31 92 99 c5 43
    3d db c2 b3 05 3b 47 de d2 ec d4 a4 ca ef d6 14
    83 3d c8 bb 62 2f 31 7e d0 76 b8 05 7f e8 de 3f
    84 48 0a d5 e8 3e 4a 61 90 4a 4f 24 8f b3 97 02
    73 57 e1 d3 0e 46 31 39 81 5c 6f d4 fd 5a c5 b8
    17 2a 45 23 0e cb 63 18 a0 4f 14 55 d8 4e 5a 8b

    # Exponent:
    01 00 01

    # Private key
    # -----------

    # Modulus:
    e6 bd 69 2a c9 66 45 79 04 03 fd d0 f5 be b8 b9
    bf 92 ed 10 00 7f c3 65 04 64 19 dd 06 c0 5c 5b
    5b 2f 48 ec f9 89 e4 ce 26 91 09 97 9c bb 40 b4
    a0 ad 24 d2 24 83 d1 ee 31 5a d4 cc b1 53 42 68
    35 26 91 c5 24 f6 dd 8e 6c 29 d2 24 cf 24 69 73
    ae c8 6c 5b f6 b1 40 1a 85 0d 1b 9a d1 bb 8c bc
    ec 47 b0 6f 0f 8c 7f 45 d3 fc 8f 31 92 99 c5 43
    3d db c2 b3 05 3b 47 de d2 ec d4 a4 ca ef d6 14
    83 3d c8 bb 62 2f 31 7e d0 76 b8 05 7f e8 de 3f
    84 48 0a d5 e8 3e 4a 61 90 4a 4f 24 8f b3 97 02
    73 57 e1 d3 0e 46 31 39 81 5c 6f d4 fd 5a c5 b8
    17 2a 45 23 0e cb 63 18 a0 4f 14 55 d8 4e 5a 8b

    # Public exponent:
    01 00 01

    # Exponent:
    6a 7f d8 4f b8 5f ad 07 3b 34 40 6d b7 4f 8d 61
    a6 ab c1 21 96 a9 61 dd 79 56 5e 9d a6 e5 18 7b
    ce 2d 98 02 50 f7 35 95 75 35 92 70 d9 15 90 bb
    0e 42 7c 71 46 0b 55 d5 14 10 b1 91 bc f3 09 fe
    a1 31 a9 2c 8e 70 27 38 fa 71 9f 1e 00 41 f5 2e
    40 e9 1f 22 9f 4d 96 a1 e6 f1 72 e1 55 96 b4 51
    0a 6d ae c2 61 05 f2 be bc 53 31 6b 87 bd f2 13
    11 66 60 70 e8 df ee 69 d5 2c 71 a9 76 ca ae 79
    c7 2b 68 d2 85 80 dc 68 6d 9f 51 29 d2 25 f8 2b
    3d 61 55 13 a8 82 b3 db 91 41 6b 48 ce 08 88 82
    13 e3 7e eb 9a f8 00 d8 1c ab 32 8c e4 20 68 99
    03 c0 0c 7b 5f d3 1b 75 50 3a 6d 41 96 84 d6 29

    # Prime 1:
    f8 eb 97 e9 8d f1 26 64 ee fd b7 61 59 6a 69 dd
    cd 0e 76 da ec e6 ed 4b f5 a1 b5 0a c0 86 f7 92
    8a 4d 2f 87 26 a7 7e 51 5b 74 da 41 98 8f 22 0b
    1c c8 7a a1 fc 81 0c e9 9a 82 f2 d1 ce 82 1e dc
    ed 79 4c 69 41 f4 2c 7a 1a 0b 8c 4d 28 c7 5e c6
    0b 65 22 79 f6 15 4a 76 2a ed 16 5d 47 de e3 67

    # Prime 2:
    ed 4d 71 d0 a6 e2 4b 93 c2 e5 f6 b4 bb e0 5f 5f
    b0 af a0 42 d2 04 fe 33 78 d3 65 c2 f2 88 b6 a8
    da d7 ef e4 5d 15 3e ef 40 ca cc 7b 81 ff 93 40
    02 d1 08 99 4b 94 a5 e4 72 8c d9 c9 63 37 5a e4
    99 65 bd a5 5c bf 0e fe d8 d6 55 3b 40 27 f2 d8
    62 08 a6 e6 b4 89 c1 76 12 80 92 d6 29 e4 9d 3d

    # Prime exponent 1:
    2b b6 8b dd fb 0c 4f 56 c8 55 8b ff af 89 2d 80
    43 03 78 41 e7 fa 81 cf a6 1a 38 c5 e3 9b 90 1c
    8e e7 11 22 a5 da 22 27 bd 6c de eb 48 14 52 c1
    2a d3 d6 1d 5e 4f 77 6a 0a b5 56 59 1b ef e3 e5
    9e 5a 7f dd b8 34 5e 1f 2f 35 b9 f4 ce e5 7c 32
    41 4c 08 6a ec 99 3e 93 53 e4 80 d9 ee c6 28 9f

    # Prime exponent 2:
    4f f8 97 70 9f ad 07 97 46 49 45 78 e7 0f d8 54
    61 30 ee ab 56 27 c4 9b 08 0f 05 ee 4a d9 f3 e4
    b7 cb a9 d6 a5 df f1 13 a4 1c 34 09 33 68 33 f1
    90 81 6d 8a 6b c4 2e 9b ec 56 b7 56 7d 0f 3c 9c
    69 6d b6 19 b2 45 d9 01 dd 85 6d b7 c8 09 2e 77
    e9 a1 cc cd 56 ee 4d ba 42 c5 fd b6 1a ec 26 69

    # Coefficient:
    77 b9 d1 13 7b 50 40 4a 98 27 29 31 6e fa fc 7d
    fe 66 d3 4e 5a 18 26 00 d5 f3 0a 0a 85 12 05 1c
    56 0d 08 1d 4d 0a 18 35 ec 3d 25 a6 0f 4e 4d 6a
    a9 48 b2 bf 3d bb 5b 12 4c bb c3 48 92 55 a3 a9
    48 37 2f 69 78 49 67 45 f9 43 e1 db 4f 18 38 2c
    ea a5 05 df c6 57 57 bb 3f 85 7a 58 dc e5 21 56

    # RSA-PSS signing of 6 random messages with random salts
    # -------------------------------------------------------

    <snip>

    # =============================================

    <snip>
    """).splitlines()

    vectors = tuple(load_pkcs1_vectors(vector_data))
    expected = (
        (
            {
                'modulus': int(
                    '495370a1fb18543c16d3631e3163255df62be6eee890d5f25509e4f77'
                    '8a8ea6fbbbcdf85dff64e0d972003ab3681fbba6dd41fd541829b2e58'
                    '2de9f2a4a4e0a2d0900bef4753db3cee0ee06c7dfae8b1d53b5953218'
                    'f9cceea695b08668edeaadced9463b1d790d5ebf27e9115b46cad4d9a'
                    '2b8efab0561b0810344739ada0733f', 16),
                'public_exponent': int('10001', 16),
                'private_exponent': int(
                    '6c66ffe98980c38fcdeab5159898836165f4b4b817c4f6a8d486ee4ea'
                    '9130fe9b9092bd136d184f95f504a607eac565846d2fdd6597a8967c7'
                    '396ef95a6eeebb4578a643966dca4d8ee3de842de63279c618159c1ab'
                    '54a89437b6a6120e4930afb52a4ba6ced8a4947ac64b30a3497cbe701'
                    'c2d6266d517219ad0ec6d347dbe9', 16),
                'p': int(
                    '8dad7f11363faa623d5d6d5e8a319328d82190d7127d2846c439b0ab7'
                    '2619b0a43a95320e4ec34fc3a9cea876422305bd76c5ba7be9e2f410c'
                    '8060645a1d29edb', 16),
                'q': int(
                    '847e732376fc7900f898ea82eb2b0fc418565fdae62f7d9ec4ce2217b'
                    '97990dd272db157f99f63c0dcbb9fbacdbd4c4dadb6df67756358ca41'
                    '74825b48f49706d', 16)
            },

            {
                'modulus': int(
                    '495370a1fb18543c16d3631e3163255df62be6eee890d5f25509e4f77'
                    '8a8ea6fbbbcdf85dff64e0d972003ab3681fbba6dd41fd541829b2e58'
                    '2de9f2a4a4e0a2d0900bef4753db3cee0ee06c7dfae8b1d53b5953218'
                    'f9cceea695b08668edeaadced9463b1d790d5ebf27e9115b46cad4d9a'
                    '2b8efab0561b0810344739ada0733f', 16),
                'public_exponent': int('10001', 16)
            }
        ),
        (
            {
                'modulus': int(
                    'e6bd692ac96645790403fdd0f5beb8b9bf92ed10007fc365046419dd0'
                    '6c05c5b5b2f48ecf989e4ce269109979cbb40b4a0ad24d22483d1ee31'
                    '5ad4ccb1534268352691c524f6dd8e6c29d224cf246973aec86c5bf6b'
                    '1401a850d1b9ad1bb8cbcec47b06f0f8c7f45d3fc8f319299c5433ddb'
                    'c2b3053b47ded2ecd4a4caefd614833dc8bb622f317ed076b8057fe8d'
                    'e3f84480ad5e83e4a61904a4f248fb397027357e1d30e463139815c6f'
                    'd4fd5ac5b8172a45230ecb6318a04f1455d84e5a8b', 16),
                'public_exponent': int('10001', 16),
                'private_exponent': int(
                    '6a7fd84fb85fad073b34406db74f8d61a6abc12196a961dd79565e9da'
                    '6e5187bce2d980250f7359575359270d91590bb0e427c71460b55d514'
                    '10b191bcf309fea131a92c8e702738fa719f1e0041f52e40e91f229f4'
                    'd96a1e6f172e15596b4510a6daec26105f2bebc53316b87bdf2131166'
                    '6070e8dfee69d52c71a976caae79c72b68d28580dc686d9f5129d225f'
                    '82b3d615513a882b3db91416b48ce08888213e37eeb9af800d81cab32'
                    '8ce420689903c00c7b5fd31b75503a6d419684d629', 16),
                'p': int(
                    'f8eb97e98df12664eefdb761596a69ddcd0e76daece6ed4bf5a1b50ac'
                    '086f7928a4d2f8726a77e515b74da41988f220b1cc87aa1fc810ce99a'
                    '82f2d1ce821edced794c6941f42c7a1a0b8c4d28c75ec60b652279f61'
                    '54a762aed165d47dee367', 16),
                'q': int(
                    'ed4d71d0a6e24b93c2e5f6b4bbe05f5fb0afa042d204fe3378d365c2f'
                    '288b6a8dad7efe45d153eef40cacc7b81ff934002d108994b94a5e472'
                    '8cd9c963375ae49965bda55cbf0efed8d6553b4027f2d86208a6e6b48'
                    '9c176128092d629e49d3d', 16)
            },

            {
                'modulus': int(
                    'e6bd692ac96645790403fdd0f5beb8b9bf92ed10007fc365046419dd0'
                    '6c05c5b5b2f48ecf989e4ce269109979cbb40b4a0ad24d22483d1ee31'
                    '5ad4ccb1534268352691c524f6dd8e6c29d224cf246973aec86c5bf6b'
                    '1401a850d1b9ad1bb8cbcec47b06f0f8c7f45d3fc8f319299c5433ddb'
                    'c2b3053b47ded2ecd4a4caefd614833dc8bb622f317ed076b8057fe8d'
                    'e3f84480ad5e83e4a61904a4f248fb397027357e1d30e463139815c6f'
                    'd4fd5ac5b8172a45230ecb6318a04f1455d84e5a8b', 16),
                'public_exponent': int('10001', 16)
            }
        )
    )
    assert vectors == expected
