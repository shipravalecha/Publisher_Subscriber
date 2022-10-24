from audioop import reverse
from cmath import log
from copyreg import pickle
from distutils.log import Log
from email import message
from ntpath import join
from fxp_bytes_subscriber import deserialize_message
from datetime import datetime
import selectors
import socket
import sys
import ipaddress
from bellman_ford import Graph
import math

listen_count = 100
REQUEST_ADDRESS = ('localhost', 50403)
LOCAL_IP = "127.0.0.1"

class Lab3(object):

    def __init__(self, listener_host, listener_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.selector = selectors.DefaultSelector()
        self.listener_host = listener_host
        self.listener_port = listener_port
        self.all_exchange_records = {}
        self.exchange_rates = []
        self.currency_graph =  Graph()
        self.latest_seen_timestamp = 0

    def create_listening_socket(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        lsock.bind((listener_host, listener_port))
        events = selectors.EVENT_READ
        lsock.setblocking(False)
        events = selectors.EVENT_READ
        self.selector.register(lsock, events, data=self.service_connection)

    def register_listening_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            int_ip = int(ipaddress.ip_address(LOCAL_IP)).to_bytes(4, byteorder='big')
            int_port = int(self.listener_port).to_bytes(2, byteorder='big')
            int_ip += bytearray(int_port)
            sock.sendto(int_ip, REQUEST_ADDRESS)

    """
    This method is the service connection method which is a server that sends the messages to client 
    and updates the states of all the members in the group.
    """
    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recvfrom(4096)
            if recv_data:
                print("***************************NEW Message*************************")
                records = deserialize_message(recv_data)
                for record in records:
                    # timestamp = datetime.fromtimestamp(record[0])
                    source = record[1]
                    dest = record[2]
                    price = record[3]
                    if record[0] < self.latest_seen_timestamp:
                        print("ignoring out-of-sequence message")
                    else:
                        self.latest_seen_timestamp = record[0]
                        self.log_of_the_weights(source, dest, price, record[0])
        print("starting bellman ford")
        self.currency_graph.BellmanFord('USD')
    
    def log_of_the_weights(self, source, dest, price, timestamp):
        log_rate = self.calculate_log(price)
        reverse_log_rate = self.calculate_reverse_log(price)        
        self.currency_graph.addEdge(source, dest, log_rate, timestamp)
        # self.currency_graph.addEdge(dest, source, -log_rate, timestamp)

    def calculate_log(self, exch_rate):
        return -math.log10( exch_rate )

    def calculate_reverse_log(self, exch_rate):
        return -math.log10(1/exch_rate)

if __name__ == '__main__':
    listener_port = int(sys.argv[1])
    listener_host = '127.0.0.1'
    lab3 = Lab3(listener_host, listener_port)
    lab3.create_listening_socket()
    lab3.register_listening_socket()
    try:
        while True:
            events = lab3.selector.select(timeout = None)
            for key, mask in events:
                callback = key.data
                callback(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        lab3.selector.close()