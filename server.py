from socket import *
import sys
import select
address = ('localhost', 54321)
hostsock = socket(AF_INET, SOCK_DGRAM)
hostsock.bind(address)

while(1):
    print "Listening"
    data, clisock = hostsock.recvfrom(2048)
    if data == "Request 1" :
        print "Received request 1"
        server_socket.sendto("Response 1", clisock)
    elif data == "Request 2" :
        print "Received request 2"
        data = "Response 2"
        server_socket.sendto(data, clisock)

from twisted.internet import reactor, protocol

class HostedGame():
    pass
game_mode=3;inet=1;maxpl=1;nation=de;numpl=1;password=0;players=§(10)←Patric
k∟§(-1)←;run=1;server_addr=62.143.7.179;server_name=tot98 (Patrick);server_port=
58282;vmaj=1;vmin=3;vtype=f

class CommunityServer():
    def __init__(self):
        self.games = []
    def addGame(self, client, request):
        pass
    def endGame(self, client):
        pass
    def getGames(self):
        return self.games
    def processUDP(self, data):
        print request
        return "game_mode=3;inet=1;maxpl=1;nation=de;numpl=1;password=0;players=§(10)←Patrick∟§(-1)←;run=1;server_addr=62.143.7.179;server_name=tot98 (Patrick);server_port=58282;vmaj=1;vmin=3;vtype=f"

class TCPFactory(protocol.Protocol):   
    def __init__(self, master):
        self.server = master

    def dataReceived(self, data):
        self.transport.write(data)
        print data

class UDPFactory(protocol.DatagramProtocol):
    def __init__(self, master):
        self.server = master

    def dataReceived(self, data, address):
        prefix = datagram[:4]
        request = datagram[4:]
        self.transport.write(prefix + self.server.processUDP(request), address)


def main():
    masterserver = CommunityServer()
    reactor.listenTCP(54321,TCPFactory(masterserver))
    reactor.listenUDP(54321,UDPFactory(masterserver))
    reactor.run()

if __name__ == '__main__':
    main()