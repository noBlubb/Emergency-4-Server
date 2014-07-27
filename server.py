from twisted.internet import reactor, protocol
import struct

UDP_SERVER_RESPONSE = "\x80"
UDP_CLIENT_REQUEST = "\x00"
UDP_DEBUGR_RESPONSE = "game_mode=3;inet=1;maxpl=4;nation=de;numpl=1;password=0;players=\xA7(10)\x1BnoBlubb\x1C\xA7(-1)\x1B;run=1;server_addr=127.0.0.1;server_name=Blubberium (noBlubb);server_port=58282;vmaj=1;vmin=1;vtype=f"

"""
len     type            val

2 bytes "session-id"    random?
1 byte  "mode"          hex(00)=>request(client->server), hex(80)=>response(server->client)   
1 byte  "content-len"   hex encoded content length
"""
def HELPER_buildNameString(playerList):
    if len(playerList) == 1:
        return "\xA7(10)\x1B{0:s}\x1C\xA7(-1)\x1B".format(playerList[0])
    elif len(playerList) == 2:
        return "\xA7(10)\x1B{0:s}\x1C\xA7(-1)\x1B, {1:s}".format(playerList[0],playerList[1])
    elif len(playerList) > 2:
        return "\xA7(10)\x1B{0:s}\x1C\xA7(-1)\x1B, ".format(playerList[0]) + ', '.join(playerList[1:4])

def HELPER_dictionaryToDataString(dataIn):
    conversion = ''
    for x,y in dataIn:
        conversion += ';' + x + '=' + y
    return conversion

def HELPER_dataStringToDictionary(dataIn):
    conversion = {}
    for x in dataIn.split(';'):
        x,y = x.split('=')
        if len(x) > 0:
            conversion[x] = y
    return conversion

class CommunityServer():
    def __init__(self):
        self.games = []
    #Byte 3 should be mode \x00, ignore. Byte 4 should be content-len, ignore
    def processUDP(self, data):
        session = data[:2]  
        request = data[4:]
        print request
        response = UDP_DEBUGR_RESPONSE
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
    def datagramReceived(self, data, address):
        response = self.server.processUDP(data)
        self.transport.write(response, address)


def main():
    masterserver = CommunityServer()
    #reactor.listenTCP(54321,TCPFactory(masterserver))
    reactor.listenUDP(54321,UDPFactory(masterserver))
    reactor.run()

if __name__ == '__main__':
    main()