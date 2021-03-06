# eth-signer
[![PyPI](https://img.shields.io/pypi/v/eth-signer)](https://pypi.org/project/eth-signer/)
[![PyPI - License](https://img.shields.io/pypi/l/eth-signer)](https://github.com/sejpalkalpesh/eth-signer/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/eth-signer)](https://pepy.tech/project/eth-signer)
[![eth-signer workflow](https://github.com/sejpalkalpesh/eth-signer/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/sejpalkalpesh/eth-signer/actions/workflows/python-app.yml)

Eth-signer is A Python library for transection and message signing using Key Management Services such as AWS Key Management Service, Azure Key Vault, Vault by HashiCorp.


## Features 

- [x] Support for Ethereum Transaction and Message Signing using AWS Key Management Service  
- [x] Support all types of Transactions and message signing supported by the eth-account package.
- [ ] Support for Ethereum Transaction and Message Signing using Azure Key Vault
- [ ] Support for Ethereum Transaction and Message Signing using Vault by HashiCorp ( will wait till PR for secp256k1 support be accepted.)
- [ ] Support For signing Ethereum 2.0 Transaction and Message
- [x] Support eth-signer in Mac OS 11.6 , Ubuntu 20.04 LTS and Windows 11 

## Dependencies

- Python 3.6+

## QuickStart

`eth-signer` is available on [PyPI](https://pypi.org/project/eth-signer/). Install via pip as:

```sh
  pip install eth-signer
```

## Usage

`eth-signer` needs AWS-KMS Client Object from `boto3` to sign Ethereum transaction or message.

In the following example, the Basic use of `eth-signer` with `boto3` has been given.

Step - 1 :  Install required dependencies 
```bash 
pip3 install boto3 eth-signer web3
```
> Please, do configure [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) before following step 2. 

Step - 2: Create a new key pair using boto3 ( Optional )
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

# Print Key ID and Eth address
print("KeyId: ", key_id)
print("Eth Address: ", kms_signer.address)
```
Output:
```python
KeyId: af8929db-010c-4476-00X0-0X00000X00X0
Eth Address: 0x40532E26c7100D72ee1CF91Ed65b44A4aEAC2b0f
```
Step - 3: Send a new transaction using web3, boto3, and eth-signer
> Example 1: Transfer 0.01 ETH from AWS KMS managed Ethereum Account to another Ethereum Account. ( Please, do make you have sufficient balance in the Account before executing the example code.)
```python
import boto3
from eth_signer.signer import AWSKMSKey
from web3 import Web3

# Get a kms_client Object From boto3
kms_client = boto3.client('kms', 'us-east-1')

# User a KeyId of the AWS KMS Key
key_id = 'af8929db-010c-4476-00X0-0X00000X00X0'
kms_signer = AWSKMSKey(kms_client, key_id)

web3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/<PROJECT_ID>'))
nonce = web3.eth.get_transaction_count(kms_signer.address)

print(web3.eth.getBalance(kms_signer.address))
# build a transaction in a dictionary
tx_obj = {
        "nonce": nonce,
        "from": kms_signer.address,
        "to": '0xBe0745cF5b82aB1de6fB1CEd849081BE06d9b3be',
        "value": web3.toWei(0.01, "ether"),
        "gas": 200000,
        "gasPrice": web3.toWei("50", "gwei"),
    }

signed_tx = kms_signer.sign_transaction(tx_obj)
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("https://ropsten.etherscan.io/tx/" + tx_hash.hex())
```
Output:
```python
34750000000000000
https://ropsten.etherscan.io/tx/0x826a52e59431a4be8780807cdd09da01d0dbbb00848fd7c9dff8383869c7372c
```
Transaction on [etherscan.io](https://ropsten.etherscan.io/tx/0x826a52e59431a4be8780807cdd09da01d0dbbb00848fd7c9dff8383869c7372c) 

> Example 2: Transfer 0.01 ETH from AWS KMS managed Ethereum Account to another Ethereum Account. ( Please, do make you have sufficient balance in the Account before executing the example code.) (Using EIP-1559 Dynamic fee transaction)
```python
import boto3
from eth_signer.signer import AWSKMSKey
from web3 import Web3

# Get a kms_client Object From boto3
kms_client = boto3.client('kms', 'us-east-1')

# User a KeyId of the AWS KMS Key
key_id = 'af8929db-010c-4476-00X0-0X00000X00X0'
kms_signer = AWSKMSKey(kms_client, key_id)

web3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/<PROJECT_ID>'))
nonce = web3.eth.get_transaction_count(kms_signer.address)

print(web3.eth.getBalance(kms_signer.address))
# build a transaction in a dictionary
tx_obj = {
    "nonce": nonce,
    "from": kms_signer.address,
    "to": "0xBe0745cF5b82aB1de6fB1CEd849081BE06d9b3be",
    "value": web3.toWei(12, "wei"),
    "gas": 25000,
    "maxFeePerGas": web3.toWei(5, "gwei"),
    "maxPriorityFeePerGas": web3.toWei(5, "gwei"),
    "type": "0x2",
    # ChainId "0x3" for ropsten chain 
    "chainId": "0x3",
}


signed_tx = kms_signer.sign_transaction(tx_obj)
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("https://ropsten.etherscan.io/tx/" + tx_hash.hex())
```
Output:
```python
34750000000000000
https://ropsten.etherscan.io/tx/0xb7248612afb1b8ff2388b9ddfed6127c8b8d4e6dcc609816fd421cd6c1e8b3f1
```
Transaction on [etherscan.io](https://ropsten.etherscan.io/tx/0xb7248612afb1b8ff2388b9ddfed6127c8b8d4e6dcc609816fd421cd6c1e8b3f1) 


> Example 3: Sign and Verify a Message
```python
import boto3
from eth_account.messages import encode_defunct
from web3.auto import w3

# Get a kms_client Object From boto3
kms_client = boto3.client('kms', 'us-east-1')

# User a KeyId of the AWS KMS Key
key_id = 'af8929db-010c-4476-00X0-0X00000X00X0'
kms_signer = AWSKMSKey(kms_client, key_id)

msg = "From eth-signer"
message = encode_defunct(text=msg)

# Sign a Message
signed_message = kms_signer.sign_message(message)
# Recover Eth address from original message and Signature
eth_address = w3.eth.account.recover_message(message, signature=signed_message.signature)
print("Eth Address: ", eth_address)

# Recover Eth address from signed message
eth_address = w3.eth.account.recoverHash(signed_message.messageHash, signature=signed_message.signature)
print("Eth Address: ", eth_address)

```
Output:
```python
Eth Address: 0x40532E26c7100D72ee1CF91Ed65b44A4aEAC2b0f
Eth Address: 0x40532E26c7100D72ee1CF91Ed65b44A4aEAC2b0f
```


### Contributors
 
* [Kalpesh Sejpal](https://github.com/sejpalkalpesh/)
* [Medium Article from Lucas Henning](https://luhenning.medium.com/the-dark-side-of-the-elliptic-curve-signing-ethereum-transactions-with-aws-kms-in-javascript-83610d9a6f81)

### Runtime dependencies
The distributed eth-signer contains software from the following projects from PyPI:

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
