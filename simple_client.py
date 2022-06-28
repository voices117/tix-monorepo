import time
import random
import socket

from base64 import b64encode


ADDRESS = ('localhost', 4500)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

TRIGGER_ADDRESS = ('localhost', 7561)
sock_trigger_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



def get_timestamp() -> bytes:
    return time.time_ns().to_bytes(length=8, byteorder='big')


def build_data_packet(packets:list) -> bytes:
    user_id = b'testuser'
    installation_id = b'installa'
    public_key = b'\x00' * 294
    public_key = b'\x00' * 294

    data = b''
    for p in packets:
        unix_time_seconds = (time.time_ns() // 1_000_000).to_bytes(length=8, byteorder='little')
        data += unix_time_seconds
        data += b'S' + (32).to_bytes(length=4, byteorder='little')
        data += p

    data = b64encode(data)

    signature = b'\x00' * 256
    
    return (
        b'\x00' * 32 +  # timestamps
        b'DATA' +
        user_id + installation_id + b';;' +
        public_key + b';;' +
        data + b';;' +
        signature
    )


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
    sock.sendto(build_data_packet(packets), ADDRESS)
    print('response to large packet: %r' % sock.recv(32))
    