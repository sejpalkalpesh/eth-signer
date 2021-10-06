import warnings
from collections.abc import Mapping  # noqa: F401
from typing import Tuple  # noqa: F401

import boto3  # noqa: F401
import botocore  # noqa: F401
from Crypto.Util.asn1 import (DerBitString, DerInteger,  # noqa: F401
                              DerSequence)
from cytoolz import dissoc
from eth_keys.datatypes import (PublicKey, Signature,
                                )
from eth_utils.curried import is_string, keccak, to_bytes
from hexbytes import HexBytes

from eth_account._utils.signing import hash_of_signed_transaction  # noqa: F401
from eth_account._utils.signing import (sign_transaction_dict, to_bytes32,
                                        to_eth_v)
from eth_account.datastructures import SignedTransaction
from eth_account.messages import SignableMessage, _hash_eip191_message
from eth_account.signers.base import BaseAccount  # noqa: F401
from eth_signer.utils.ecdsa import ecdsa_to_signature  # noqa: F401


class AWSKMSKey(BaseAccount):
    r"""
    A collection of convenience methods to sign with an AWS KMS.

    :var string key_id: AWS KMS KeyId

    .. code-block:: python
        >>> my_local_account.address # doctest: +SKIP
        "0xF0109fC8DF000027b6285cc889F5aA624EaC1F55"
        >>> my_local_account.pub_key # doctest: +SKIP
        b"\x01\x23..."
    """

    def __init__(self, kms_client, key_id: str):
        """
        Initialize a new account with the the given AWS KMS key pair.
        :param botocore.client.KMS kms_client: AWS KMS client object
        :param string key_id: KeyId of AWS KMS key pair
        """
        if str(type(kms_client)) == "<class 'botocore.client.KMS'>" and is_string(key_id):
            self._kms_client = kms_client
            self._key_id = key_id
            self._pub_key = self.get_pub_key_from_key_id()
            self._address = self._pub_key.to_checksum_address()
        else:
            raise ValueError(
                "Unsupported format for kms_client Must be an instance of "
                "`botocore.client.KMS` and key_id must be string"
            )

    @property
    def address(self):
        return self._address

    @property
    def key_id(self):
        return self._key_id

    @property
    def kms_client(self):
        """kms_client is `botocore.client.KMS` object"""
        return self._kms_client

    def get_pub_key_from_key_id(self) -> bytes:
        pub_key_info = self._kms_client.get_public_key(KeyId=self._key_id)
        if pub_key_info['KeySpec'] == 'ECC_SECG_P256K1' and \
                pub_key_info['KeyUsage'] == 'SIGN_VERIFY' and \
                pub_key_info['SigningAlgorithms'][0] == 'ECDSA_SHA_256':
            return self.pub_key_from_der(pub_key_info['PublicKey'])
        else:
            raise TypeError('Invalid Key Type')

    @staticmethod
    def pub_key_from_der(der: bytes) -> bytes:
        der_seq = DerSequence()
        der_seq.decode(der)
        pub_key = DerBitString()
        pub_key.decode(der_seq[1])
        if pub_key.value[0:1] == b'\x04':
            return PublicKey(pub_key.value[1:])
        else:
            raise ValueError(
                "Unsupported pub_key value"
            )

    def sign(self, message_hash: HexBytes) -> Signature:
        sign = self._kms_client.sign(
            # key id or 'Alias/<alias>'
            KeyId=self._key_id,
            Message=bytes(message_hash),
            MessageType="DIGEST",
            # 'ECDSA_SHA_256' is the one compatible with ECC_SECG_P256K1.
            SigningAlgorithm="ECDSA_SHA_256",
        )
        return ecdsa_to_signature(message_hash, sign['Signature'], self._address)

    def sign_msg_hash(self, message_hash: HexBytes) -> Signature:
        return self.sign(message_hash)

    def signHash(self, message_hash) -> Tuple[int, int, int, bytes]:
        (v_raw, r, s) = self.sign(self, message_hash).vrs
        v = to_eth_v(v_raw)
        eth_signature_bytes = to_bytes32(r) + to_bytes32(s) + to_bytes(v)
        return v, r, s, eth_signature_bytes

    def sign_message(self, signable_msg: SignableMessage) -> Tuple[int, int, int, bytes]:
        """
        Generate a string with the encrypted key.
        This uses the same structure as in
        :meth:`~eth_signer.signer.AWSKMSKey.sign_message`.
        """
        message_hash = _hash_eip191_message(signable_msg)
        return self.signHash(self, message_hash)

    def signTransaction(self, transaction_dict: dict) -> SignedTransaction:
        warnings.warn(
            "signTransaction is deprecated in favor of sign_transaction",
            category=DeprecationWarning,
        )
        return self.sign_transaction(transaction_dict)

    def sign_transaction(self, transaction_dict: dict) -> SignedTransaction:
        """
        Sign a transaction using a AWS KMS Key .
        It produces signature details and the hex-encoded transaction suitable for broadcast using
        :meth:`w3.eth.sendRawTransaction() <web3.eth.Eth.sendRawTransaction>`.
        To create the transaction dict that calls a contract, use contract object:
        `my_contract.functions.my_function().buildTransaction()
        <http://web3py.readthedocs.io/en/latest/contracts.html#methods>`_
        Note: For non-legacy (typed) transactions, if the transaction type is not explicitly
        provided, it may be determined from the transaction parameters of a well-formed
        transaction. See below for examples on how to sign with different transaction types.
        :param dict transaction_dict: the transaction with available keys, depending on the type of
          transaction: nonce, chainId, to, data, value, gas, gasPrice, type, accessList,
          maxFeePerGas, and maxPriorityFeePerGas
        :returns: Various details about the signature - most
          importantly the fields: v, r, and s
        :rtype: AttributeDict
        .. code-block:: python
            >>> # EIP-1559 dynamic fee transaction (more efficient and preferred over legacy txn)
            >>> dynamic_fee_transaction = {
                    "type": 2,  # optional - can be implicitly determined based on max fee params  # noqa: E501
                    "gas": 100000,
                    "maxFeePerGas": 2000000000,
                    "maxPriorityFeePerGas": 2000000000,
                    "data": "0x616263646566",
                    "nonce": 34,
                    "to": "0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
                    "value": "0x5af3107a4000",
                    "accessList": (  # optional
                        {
                            "address": "0x0000000000000000000000000000000000000001",
                            "storageKeys": (
                                "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                            )
                        },
                    ),
                    "chainId": 1900,
                }
            >>> kms_client = kms.client('kms', 'us-east-1')
            >>> key_id = 'XX0000XX-00XX-00XX-00XX-XXXX0000XXXX'
            >>> signed = AWSKMSKey(kms_client, key_id).sign_transaction(dynamic_fee_transaction)
            {'hash': HexBytes('0x126431f2a7fda003aada7c2ce52b0ce3cbdbb1896230d3333b9eea24f42d15b0'),
             'r': 110093478023675319011132687961420618950720745285952062287904334878381994888509,
             'rawTransaction': HexBytes('0x02f8b282076c2284773594008477359400830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000080a0f366b34a5c206859b9778b4c909207e53443cca9e0b82e0b94bc4b47e6434d3da04a731eda413a944d4ea2d2236671e586e57388d0e9d40db53044ae4089f2aec8'),  # noqa: E501
             's': 33674551144139401179914073499472892825822542092106065756005379322302694600392,
             'v': 0}
            >>> w3.eth.sendRawTransaction(signed.rawTransaction)
        .. code-block:: python
            >>> # legacy transaction (less efficient than EIP-1559 dynamic fee txn)
            >>> legacy_transaction = {
                    # Note that the address must be in checksum format or native bytes:
                    'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                    'value': 1000000000,
                    'gas': 2000000,
                    'gasPrice': 234567897654321,
                    'nonce': 0,
                    'chainId': 1
                }
            >>> kms_client = kms.client('kms', 'us-east-1')
            >>> key_id = 'XX0000XX-00XX-00XX-00XX-XXXX0000XXXX'
            >>> signed = AWSKMSKey(kms_client, key_id).sign_transaction(legacy_transaction)
            {'hash': HexBytes('0x6893a6ee8df79b0f5d64a180cd1ef35d030f3e296a5361cf04d02ce720d32ec5'),
             'r': 4487286261793418179817841024889747115779324305375823110249149479905075174044,
             'rawTransaction': HexBytes('0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428'),  # noqa: E501
             's': 30785525769477805655994251009256770582792548537338581640010273753578382951464,
             'v': 37}
            >>> w3.eth.sendRawTransaction(signed.rawTransaction)
        .. code-block:: python
            >>> access_list_transaction = {
                    "type": 1,  # optional - can be implicitly determined based on 'accessList' and 'gasPrice' params  # noqa: E501
                    "gas": 100000,
                    "gasPrice": 1000000000,
                    "data": "0x616263646566",
                    "nonce": 34,
                    "to": "0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
                    "value": "0x5af3107a4000",
                    "accessList": (
                        {
                            "address": "0x0000000000000000000000000000000000000001",
                            "storageKeys": (
                                "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                            )
                        },
                    ),
                    "chainId": 1900,
                }
            >>> kms_client = kms.client('kms', 'us-east-1')
            >>> key_id = 'XX0000XX-00XX-00XX-00XX-XXXX0000XXXX'
            >>> signed = AWSKMSKey(kms_client, key_id).sign_transaction(access_list_transaction)
            {'hash': HexBytes('0x2864ca20a74ca5e044067ad4139a22ff5a0853434f5f1dc00108f24ef5f1f783'),
             'r': 105940705063391628472351883894091935317142890114440570831409400676736873197702,
             'rawTransaction': HexBytes('0x01f8ad82076c22843b9aca00830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000080a0ea38506c4afe4bb402e030877fbe1011fa1da47aabcf215db8da8fee5d3af086a051e9af653b8eb98e74e894a766cf88904dbdb10b0bc1fbd12f18f661fa2797a4'),  # noqa: E501
             's': 37050226636175381535892585331727388340134760347943439553552848647212419749796,
             'v': 0}
            >>> w3.eth.sendRawTransaction(signed.rawTransaction)
        """
        if not isinstance(transaction_dict, Mapping):
            raise TypeError("transaction_dict must be dict-like, got %r"
                            % transaction_dict)

        # allow from field, *only* if it matches the private key
        if 'from' in transaction_dict:
            if transaction_dict['from'] == self._address:
                sanitized_transaction = dissoc(transaction_dict, 'from')
            else:
                raise TypeError("from field must match key's %s, \
                                but it was %s" % (
                    self._address,
                    transaction_dict['from'],
                ))
        else:
            sanitized_transaction = transaction_dict

        # sign transaction
        (
            v,
            r,
            s,
            encoded_transaction,
        ) = sign_transaction_dict(self, sanitized_transaction)
        transaction_hash = keccak(encoded_transaction)

        return SignedTransaction(
            rawTransaction=HexBytes(encoded_transaction),
            hash=HexBytes(transaction_hash),
            r=r,
            s=s,
            v=v,
        )
