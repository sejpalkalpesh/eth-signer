import pytest
from eth_keys.datatypes import Signature
from eth_keys.exceptions import BadSignature
from eth_signer.utils.ecdsa import ecdsa_to_signature


@pytest.mark.parametrize(
    "hash, sign, address, signature, validation_error",
    [
        # v = 28
        (b'1\xa8\x94<\xc73\xf7\x1di\xd0Q\x88\xfc@\xb6k\xea#\x93\xc6\xfd^C\xebI2\x0cm\x1f\xd8\xf3\x8e',
         b'0E\x02 l\xe8\xca\x03\xc0b,U\x1a3\xc4iG0F\xd6\xcbK\x8b&\xae\xce\xd1\xdd\x14\x1c\x12\xbb\xc0\xbb%\xbb\x02!\x00\xfb\x87\xbf\x90\xa5<\xda\x06"\xdd\x12\x1bM\x1d<\x19\xb1^(l<\xd2\x8c\x17\xdf1\xeaF\xed\xca\xe7\xac',
         '0x40532E26c7100D72ee1CF91Ed65b44A4aEAC2b0f',
         Signature(vrs=(1, 49261090419923592905606736283577801646473489408300680881228574335619649185211, 2021717755985131945314480456552235517224753320641382347191163359072881432981)),
         False),
        # v = 27
        (b'\xf6\xbci\xf2U\xd2\x15\x96\xa6\x0c+\x13\xed\xbb\x1d\xef\xa0L\x8a\xef"\xc6\x7f{\xc33\xb2\x83[\xe4\x81\x93',
         b'0D\x02 t%6k\xe5\xf8\xfc\x13\x9e\xdb9~\xc6\xd3\xbb\x97\xcb\xad[\x92:\xf6\x1av)\x98e`\x9dA\x8a\x13\x02 S\x9al&}|u\xde\xf1\xfd\xa6g\xfds\xb0\xca\xe2\xf1n\x9f\x87\xe9\xdd\xd39"f(}\xc6=\xba',
         '0x40532E26c7100D72ee1CF91Ed65b44A4aEAC2b0f',
         Signature(vrs=(0, 52534039380291662493263907133650350113198528411817157441476220813580053875219, 37814807306685644665403055195405579403516052153803802726184936400849371282874)),
         False),
        # validation error
(b'\xf6\xbci\xf2U\xd2\x15\x96\xa6\x0c+\x13\xed\xbb\x1d\xef\xa0L\x8a\xef"\xc6\x7f{\xc33\xb2\x83[\xe4\x81\x93',
         b'0D\x02 t%6k\xe5\xf8\xec\x13\x9e\xdb9~\xc6\xd3\xba\x97\xcb\xad[\x92:\xf6\x1av)\x98e`\x9dA\x8a\x13\x02 S\x9al&}|u\xde\xf1\xfd\xa6g\xfds\xb0\xca\xe2\xf1n\x9f\x87\xe9\xdd\xd39"f(}\xc6=\xba',
         '0x40532E26c7100D72ee1CF91Ed65b44A4aEAC2b0f',
         Signature(vrs=(0, 52534039380291662493263907133650350113198528411817157441476220813580053875219, 37814807306685644665403055195405579403516052153803802726184936400849371282874)),
         True),
    ]
)
def test_ecdsa_to_eth_sign(hash, sign, address, signature: Signature, validation_error):
    if validation_error:
        with pytest.raises((ValueError, BadSignature)):
            ecdsa_to_signature(hash, sign, address)
    else:
        assert ecdsa_to_signature(hash, sign, address) == signature
