"""
Lab3.py
CPSC 5520, Seattle University
This is the program lab3.py that makes the connection with the forex provider, the server running on host 'localhost'
and port '50403'. It receives the forex transaction with timestamps, exchange rates between the currencies.
Creating the UDP/ IP sockets to make the connection with forex provider to recieve the datagrams.
Command to run the provider: python3 forex_provider_v2.py
Command to run lab3: python3 lab3.py
:Authors: Fnu Shipra
:Version: 0.0
"""

from datetime import datetime
from fxp_bytes_subscriber import deserialize_message
import selectors
import socket
import sys
import ipaddress
from bellman_ford import Graph
import math

REQUEST_ADDRESS = ('localhost', 50403)                      # forex provider host and port
source = 'USD'
BUF_SZ = 4096

class Lab3(object):

    """
    Init method that recieves the listener port and host when the instance is created for the class
    and initializes the other variables
    """
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.selector = selectors.DefaultSelector()
        self.all_exchange_records = {}
        self.exchange_rates = []
        self.currency_graph =  Graph()
        self.latest_seen_timestamp = 0
        self.listener, self.listener_address = self.create_listening_socket()

    """
    This method creates a listening socket with the listener host and port that is available and 
    register the read-events with the selector
    """
    def create_listening_socket(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        lsock.bind(('localhost', 0))                                # use any free socket
        events = selectors.EVENT_READ
        lsock.setblocking(False)
        self.selector.register(lsock, events, data=self.service_connection)
        return lsock, lsock.getsockname()

    """
    This method is used to send the listener socket address to the forex provider so that forex provider can
    sends the records. We are sending the host and port in the big Endian format in bytes to the REQUEST_ADDRESS 
    i.e.forex provider
    """
    def register_listening_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            listener_host = self.listener_address[0]
            listener_port = self.listener_address[1]
            int_ip = int(ipaddress.ip_address(listener_host)).to_bytes(4, byteorder='big')
            int_port = int(listener_port).to_bytes(2, byteorder='big')
            int_ip += bytearray(int_port)
            sock.sendto(int_ip, REQUEST_ADDRESS)

    """
    This method is the service connection method that receives records from forex_provider 
    that can be processed using bellman ford algorithm to detect negative cycle
    """
    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recvfrom(BUF_SZ)
            if recv_data:
                print("***************************NEW Message*************************")            # it represents the new message from the forex provider
                records = deserialize_message(recv_data)
                
                for record in records:
                    timestamp = record[0]
                    ts = datetime.fromtimestamp(timestamp/1000)  
                    src = record[1]
                    dest = record[2]
                    price = record[3]
                    
                    print(f" {ts} {src} {dest} {price}")                            # printing timestamp, source, destination and exchange rate
                    if record[0] < self.latest_seen_timestamp:
                        print("ignoring out-of-sequence message")                   # ignoring the out of sequence messages that are older than current timestamp
                    else:
                        self.latest_seen_timestamp = record[0]
                        self.log_of_the_weights(src, dest, price, record[0])        # calculating the log of the exchange rate

        self.currency_graph.BellmanFord(source)                                     # calling bellman ford algorithm
    
    """
    This method calls the calculate_log method to calculate the log rate of the exhange rate between currencies
    and also adds the edges to the graph with the calculated log rates
    """
    def log_of_the_weights(self, src, dest, price, timestamp):
        log_rate = self.calculate_log(price)      
        self.currency_graph.addEdge(src, dest, log_rate, timestamp, price)

    """
    This method takes the exchange rate input and return the log rate.
    """
    def calculate_log(self, exch_rate):
        return -math.log10( exch_rate )

"""
This is the main method that takes listener port we provide as the command line argument. And it calls
create_listening_socket to create the listening socket available port
"""
if __name__ == '__main__':
    lab3 = Lab3()                                                   # creating Lab3 instance
    lab3.create_listening_socket()                                  # calling create_listening_socket()
    lab3.register_listening_socket()                                # calling register_listening_socket()
    try:
        while True:
            events = lab3.selector.select(timeout = None)
            for key, mask in events:
                callback = key.data
                callback(key, mask)                                 # whenever event is generated, the callback is invoked
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        lab3.selector.close()