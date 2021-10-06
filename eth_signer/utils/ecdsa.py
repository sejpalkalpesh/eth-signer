from eth_keys.constants import SECPK1_N as N  # noqa: F401
from eth_keys.datatypes import PublicKey, Signature  # noqa: F401
from eth_keys.utils.der import two_int_sequence_decoder  # noqa: F401

from eth_account.account import Account  # noqa: F401
from Crypto.Util.asn1 import (DerBitString, DerInteger,  # noqa: F401
                              DerSequence)


def ecdsa_to_signature(hash: bytes, sign: bytes, address: str) -> Signature:
    der_seq = DerSequence()
    der_seq.decode(sign)
    r = DerInteger(der_seq[0]).value
    s_raw = DerInteger(der_seq[1]).value
    s = s_raw if s_raw * 2 < N else N - s_raw
    account = Account()
    if account._recover_hash(hash, vrs=(27, r, s)) == address:
        return Signature(vrs=(0, r, s))
    elif account._recover_hash(hash, vrs=(28, r, s)) == address:
        return Signature(vrs=(1, r, s))
    else:
        raise ValueError("v %r is invalid, must be one of: 0, 1, 27, 28, 35+")
