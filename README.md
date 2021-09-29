# eth-signer
A Python library for transection signing using AWS Key Management Service.

## Dependencies

- Python 3.5+

## QuickStart

This Package is available on PyPI. Install via pip as:

```sh
  pip install eth-signer
```

## Usage

1. Instantiate eth signer client

```python
import boto3
from eth_signer import AWSKMSKey
from web3 import Web3


kms_client = boto3.client('kms', 'us-east-1')
key_id = "XX0000XX-00XX-00XX-00XX-XXXX0000XXXX"
kms_signer = AWSKMSKey(kms_client, key_id)

web3 = Web3(Web3.HTTPProvider(node_url))
contract = web3.eth.contract(address=address, abi=abi)

tx_obj = contract.functions.function_name().buildTransaction(
     {
          "nonce": nonce,
          "from": address,
     }
)

signed_tx = AWSKMSKey.sign_transaction(tx_obj)
tx_hash = signed_tx.hash
web3.eth.send_raw_transaction(signed_tx.rawTransaction)

```


### Features

- Support for EIP-2718 (Typed Transaction) and EIP-2939 (Access List Transaction)
- Support for EIP-1559 (Dynamic Fee Transaction)
