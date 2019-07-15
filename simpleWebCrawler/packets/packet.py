__author__ = "rasitmete"


class DataObject(object):
    """ All the data received or sent is a dataobject """

    @staticmethod
    def parse_data(data):
        parsed_data = data.split(" ")
        return parsed_data
    
    @staticmethod
    def check_type(parsed_data):
        pass
    
    def pack_data(self, *args):
        pass


class Packet(DataObject):
    """ Even though there is only one packet type, there might be many types in the future """
    
    def __init__(self, sender=None):
        self._sender = sender
        self._header = "cs5700fall2018"
    
    @staticmethod
    def from_bytes(data):
        raise NotImplementedError("Not Implemented")

    def to_bytes(self):
        raise NotImplementedError("Not Implemented")

    @staticmethod
    def parse_packet(data):
        pass
    
    def get_sender(self):
        return self._sender
    
    def info(self, data):
        print "DEBUG: " + data

    @staticmethod
    def recv():
        pass

    def send(self):
        pass

    
