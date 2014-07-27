from twisted.internet import reactor, protocol
import struct

UDP_SERVER_RESPONSE = "\x80"
UDP_CLIENT_REQUEST = "\x00"


"""
len     type            val

2 bytes "session-id"    random?
1 byte  "mode"          hex(00)=>request(client->server), hex(80)=>response(server->client)   
1 byte  "content-len"   hex encoded content length

"""
class HostedGame():
    pass 

class CommunityServer():
    def __init__(self):
        self.games = []
    #Byte 3 should be mode \x00, ignore. Byte 4 should be content-len, ignore
    def processUDP(self, data):
        session = data[:2]  
        request = data[4:]
        print request
        response = "game_mode=3;inet=1;maxpl=4;nation=de;numpl=1;password=0;players=\xA7(10)\x1BnoBlubb\x1C\xA7(-1)\x1B;run=1;server_addr=88.76.57.26;server_name=Blubberium (noBlubb);server_port=58282;vmaj=1;vmin=1;vtype=f"
        responselen = struct.pack('B', len(response))
        return session + UDP_SERVER_RESPONSE + responselen + response

class TCPFactory(protocol.Protocol):   
    def __init__(self, master):
        self.server = master
    def doStart(self):
        pass
    def dataReceived(self, data):
        self.transport.write(data)
        print data

class UDPFactory(protocol.DatagramProtocol):
    def __init__(self, master):
        self.server = master
    def doStart(self):
        pass
    def dataReceived(self, data, address):
        response = self.server.processUDP(data)
        self.transport.write(response, address)


def main():
    masterserver = CommunityServer()
    #reactor.listenTCP(54321,TCPFactory(masterserver))
    reactor.listenUDP(54321,UDPFactory(masterserver))
    reactor.run()

if __name__ == '__main__':
    main()