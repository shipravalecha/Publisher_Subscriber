from typing import Any
from array import array

def deserialize_message(message) -> Any:
    """
    Get the host, port address that the client wants us to publish to.

    >>> deserialize_address(b'\\x7f\\x00\\x00\\x01\\xff\\xfe')
    ('127.0.0.1', 65534)

    :param b: 6-byte sequence in subscription request
    :return: ip address and port pair
    """
    records = []
    start=0
    while True:
        try:
            deserialize_record(message, start, records)
            start+=32
        except :
            break
    return records

def deserialize_record(message, start, records):
    data, extra = message
    timestamp = deserialize_timestamp(data[start: start + 8])
    timestamp_seconds = timestamp / 1000
    source_currency = (data[start + 8: start + 11])
    destination_currency =  data[start + 11: start + 14]
    price = data[start + 14: start + 22]
    decoded_price = deserialize_price(price)
    records.append((timestamp_seconds, source_currency.decode('utf-8'), destination_currency.decode('utf-8'), decoded_price))
    return records

def deserialize_timestamp(ts_bytes):
    p = array('Q')
    p.frombytes(ts_bytes)
    p.byteswap()  # to big-endian
    return p[0]

def deserialize_price(price_bytes):
    p = array('d')
    p.frombytes(price_bytes)
    return p[0]
