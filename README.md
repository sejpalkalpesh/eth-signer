# eth-signer
A Python library for transection signing using AWS Key Management Service.

## Dependencies

- Python 3.6+

## QuickStart

This Package is available on [PyPI](https://pypi.org/project/eth-signer/). Install via pip as:

```sh
  pip install eth-signer
```

## Usage

`eth-signer` needs AWS-KMS Client Object from `boto3` to sign Ethereum transaction or message.

In the following example, the Basic use of `eth-signer` with `boto3` has been given.

```python
import boto3
from eth_signer.signer import AWSKMSKey
from web3 import Web3

# Get a kms_client Object From boto3
kms_client = boto3.client('kms', 'us-east-1')

# Generate new Key Pair using kms_client
new_key = kms.create_key(
    Description='New Eth Key',
    KeyUsage='SIGN_VERIFY',
    KeySpec='ECC_SECG_P256K1',
    Origin='AWS_KMS',
    MultiRegion=False
)

# Use KekId of newly generated key pair for AWSKMSKey Object

key_id = new_key['KeyMetadata']['KeyId']
kms_signer = AWSKMSKey(kms_client, key_id)

web3 = Web3(Web3.HTTPProvider('NODE URL'))
contract = web3.eth.contract(address='TOKEN_ADDRESS', abi=ABI)
nonce = web3.eth.get_transaction_count(kms_signer.address)

tx_obj = contract.functions.function_name().buildTransaction(
     {
          "nonce": nonce,
          "from": kms_signer.address,
     }
)

signed_tx = AWSKMSKey.sign_transaction(tx_obj)
tx_hash = signed_tx.hash
web3.eth.send_raw_transaction(signed_tx.rawTransaction)

```


### Features

- Support for Ethereum Transaction and Message Signing using AWS Key Management Service  

### Contributors
 
* [Kalpesh Sejpal](https://github.com/sejpalkalpesh/)
* [Medium Article from Lucas Henning](https://luhenning.medium.com/the-dark-side-of-the-elliptic-curve-signing-ethereum-transactions-with-aws-kms-in-javascript-83610d9a6f81)

### Runtime dependencies
The distributed eth-signer contains software from the following projects from PyPi:

* eth-utils
* eth-typing
* hexbytes
* eth-rlp
* pycryptodome
* boto3
* flake8
* isort
* mypy
* Sphinx
* sphinx_rtd_theme
* towncrier
* bumpversion
* setuptools
* tox
* twine

