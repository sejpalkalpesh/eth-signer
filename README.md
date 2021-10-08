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

Step - 1 :  Install required dependencies 
```bash 
$ pip3 install boto3 eth-signer web3
```
Step - 2 : Create a new key pair using boto3 ( Optional )
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
Step - 3 : Send a new transaction using web3, boto3 and eth-signer
> Example 1: Transfer 0.01 ETH from AWS KMS managed Ethereum Account to another Ethereum Account. ( Please, do make you have sufficient balance in Account before executing the example code.)
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
print(tx_hash)
```
Output:
```python
34750000000000000
HexBytes('0x826a52e59431a4be8780807cdd09da01d0dbbb00848fd7c9dff8383869c7372c')
```
Transaction on [etherscan.io](https://ropsten.etherscan.io/tx/0x826a52e59431a4be8780807cdd09da01d0dbbb00848fd7c9dff8383869c7372c) 


> Example 2 : Sign and Verify a Message
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

