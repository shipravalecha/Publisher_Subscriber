"""
fxp_bytes_subscriber.py
CPSC 5520, Seattle University
This is the program fxp_bytes_subscriber.py that is used to deserialize the records and then messages 
coming from the provider. The record received from the provider is in the bytes form and has the format
timestamp, source currency, destination currency, and exchange rate between the currencies.
:Authors: Fnu Shipra
:Version: 0.0
"""

from typing import Any
from array import array

"""
This method gets the entire record from the publisher that can have multiple messages, that is 32 bytes long.
It calls deserialize_record to deserialize each record of the message it receives.
:input b: message from forex provider
:return: records to lab3.py as an output
"""
def deserialize_message(message) -> Any:

    records = []
    start=0
    while True:
        try:
            deserialize_record(message, start, records)
            start+=32
        except :
            break
    return records

"""
This method gets the record from the deserialize_message method and deserialize the bytes of the record
into timestamp, source_currency, destination_currency and exchange_rate (price) 
:input b: record from deserialize_message
:return: deserialized record
"""
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

"""
This method deserializes the timestamp which is in the bytes format
"""
def deserialize_timestamp(ts_bytes):
    p = array('Q')
    p.frombytes(ts_bytes)
    p.byteswap()
    return p[0]

"""
This method deserializes the exchange_rate which is in the bytes format
"""
def deserialize_price(price_bytes):
    p = array('d')
    p.frombytes(price_bytes)
    return p[0]
