import time
import socket

from os import system
from base64 import b64encode
from tempfile import NamedTemporaryFile


ADDRESS = ('localhost', 4500)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

TRIGGER_ADDRESS = ('localhost', 7561)
sock_trigger_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# gen keys
def genkeys() -> NamedTemporaryFile:
    keys = 'keys.pem'
    system(f'openssl genrsa -out {keys} 2048')
    print('Storing keys in', keys)
    return keys


def get_digital_sign(data:bytes, keys:str) -> bytes:
    with NamedTemporaryFile() as sign_file, NamedTemporaryFile() as data_file:
        data_file.write(data)

        system(f'openssl dgst -sha256 -sign {keys} -out {sign_file.name} {data_file.name}')
        signature = sign_file.read()

    return signature


def get_public_key(keys:str) -> bytes:
    with NamedTemporaryFile() as pub:
        # serialize public key in PKCS1 DER format
        system(f'openssl rsa -pubout -outform DER -in {keys} -out {pub.name}')
        return pub.read()


def get_timestamp() -> bytes:
    return time.time_ns().to_bytes(length=8, byteorder='big')


def build_data_packet(packets:list, keys_file:str, public_key:bytes) -> bytes:
    user_id = b'testuser'
    installation_id = b'installa'

    data = b''
    for p in packets:
        unix_time_seconds = (time.time_ns() // 1_000_000).to_bytes(length=8, byteorder='little')
        data += unix_time_seconds
        data += b'S' + (32).to_bytes(length=4, byteorder='little')
        data += p

    data = b64encode(data)

    signature = get_digital_sign(data=data, keys=keys_file)
    assert len(signature) == 256

    assert len(public_key) == 294

    return (
        b'\x00' * 32 +  # timestamps
        b'DATA' + b';;' +
        user_id + installation_id + b';;' +
        public_key + b';;' +
        data + b';;' +
        signature + b';;'
    )


KEYS_FILE_NAME = genkeys()
PUBLIC_KEY = get_public_key(KEYS_FILE_NAME)


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

        packets.append(packet)

    # send long packet
    sock.sendto(build_data_packet(packets, KEYS_FILE_NAME, PUBLIC_KEY), ADDRESS)
    print('response to large packet: %r' % sock.recv(32))
    