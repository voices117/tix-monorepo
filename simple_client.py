import time
import socket
from typing import List, Tuple
import requests
from requests.auth import HTTPBasicAuth

from os import system, path
from base64 import b64encode
from tempfile import NamedTemporaryFile


ADDRESS = ('localhost', 4500)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

TRIGGER_ADDRESS = ('localhost', 7561)
sock_trigger_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

USER = 'guest'
# user_id is the numeric value assigned to the user in the DB. In this
# case I'm hardcoding it to 1, which is the Id of the admin user (guest)
USER_ID = 1
PASSSWORD = 'guest'


# gen keys
def genkeys() -> str:
    keys = 'keys.pem'

    if not path.exists(keys):
        system(f'openssl genrsa -out {keys} 2048')
        print('Storing keys in', keys)

    return keys


def get_digital_sign(data:bytes, keys:str) -> bytes:
    with NamedTemporaryFile() as sign_file, NamedTemporaryFile() as data_file:
        data_file.write(data)
        data_file.seek(0)

        system(f'openssl dgst -sha1 -sign {keys} -out {sign_file.name} {data_file.name}')
        signature = sign_file.read()

    return signature


def get_public_key(keys:str) -> bytes:
    with NamedTemporaryFile() as pub:
        # serialize public key in PKCS1 DER format
        system(f'openssl rsa -pubout -outform DER -in {keys} -out {pub.name}')
        return pub.read()


def get_timestamp() -> bytes:
    return time.time_ns().to_bytes(length=8, byteorder='big')


def get_unix_timestamp() -> bytes:
    # return the seconds elapsed since epoch encoded as an 8 byte array
    unix_time_seconds = (time.time_ns() // 1_000_000_000)
    return unix_time_seconds.to_bytes(length=8, byteorder='big')


def build_data_packet(packets:List[Tuple[bytes, bytes]], keys_file:str, public_key:bytes) -> bytes:
    user_id = (USER_ID).to_bytes(length=8, byteorder='big')
    installation_id = (INSTALLATION_ID).to_bytes(length=8, byteorder='big')

    data = b''
    for p, unix_time_seconds in packets:
        data += unix_time_seconds
        data += b'S' + (32).to_bytes(length=4, byteorder='big')
        data += p

    signature = get_digital_sign(data=data, keys=keys_file)
    assert len(signature) == 256

    assert len(public_key) == 294

    return (
        # the "large packet" can also be used as a ping packet
        # for this example we only want to send the data, so we hardcode
        # the last message's timestamps instead of doing a roundtrip
        packets[-1][0] +
        b'DATA' + b';;' +
        user_id + installation_id + b';;' +
        public_key + b';;' +
        b64encode(data) + b';;' +
        signature + b';;'
    )


def create_installation():
    print('Creating new installation...')
    auth = HTTPBasicAuth(username=USER, password=PASSSWORD)
    data = {'name': 'test_location', 'publickey': b64encode(PUBLIC_KEY).decode('ascii')}
    r = requests.post(f'http://localhost:3001/api/user/{USER_ID}/installation', json=data, auth=auth)
    assert r.ok, (r.status_code, r.text)
    return r.json()


def get_installation_id():
    return create_installation()['id']


KEYS_FILE_NAME = genkeys()
PUBLIC_KEY = get_public_key(KEYS_FILE_NAME)
INSTALLATION_ID = get_installation_id()
print('Installation ID:', INSTALLATION_ID)


while True:
    # notify trigger service
    print('Sending ping...')
    sock_trigger_service.sendto(b'\x75\x61', TRIGGER_ADDRESS)
    print('Trigger service response:', sock_trigger_service.recv(2))

    packets = []
    for i in range(10):
        time.sleep(1)

        # short packet

        ts = get_timestamp()
        # complete the initial packet with the rest of the TS zeroed
        packet = ts + b'\x00' * 24

        print('sending %r' % packet)
        sock.sendto(packet, ADDRESS)

        packet = sock.recv(32)
        print('received %r' % packet)

        # add final timestamp
        packet = packet[0:24] + get_timestamp()
        print('final packet: %r' % packet)

        packets.append((packet, get_unix_timestamp()))

    # send long packet
    sock.sendto(build_data_packet(packets, KEYS_FILE_NAME, PUBLIC_KEY), ADDRESS)
    print('response to large packet: %r' % sock.recv(32))
    