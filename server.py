# -*- coding: utf-8 -*-
from twisted.internet import reactor, protocol
import struct

UDP_SERVER_RESPONSE = "\x80"
UDP_CLIENT_REQUEST = "\x00"
UDP_DEBUGR_RESPONSE = "game_mode=3;inet=1;maxpl=4;nation=de;numpl=1;password=0;players=\xA7(10)\x1BnoBlubb\x1C\xA7(-1)\x1B;run=1;server_addr=127.0.0.1;server_name=Blubberium (noBlubb);server_port=58282;vmaj=1;vmin=1;vtype=f"
UDP_DEBUGR_REQUEST = "game=EM4;lang=de;mod={0:s}"

CFG_MASTER_SERVER_IP = '84.201.2.89'

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
    #byte 3 should be mode \x00, ignore? byte 4 should be content-len, ignore?
    def checkMasterServerUpdate(self):
        return true
    
    def performMasterServerUpdate(self, modname=''):
        request = UDP_DEBUGR_REQUEST.format(modname)
        requestlen = struct.pack('B', len(request))
        self.transport.write("\x13\x37\x00"+requestlen+request, (CFG_MASTER_SERVER_IP, 54321))
    
    def receiveMasterServerUpdate(self, request):
        pass #process data here

    def processUDP(self, data):
        session = data[:2]  
        mode = data[3]
        request = data[4:]
        print request
        if mode == UDP_SERVER_RESPONSE:
            return #u what mate
        else: #master response should not trigger update call
            if self.checkMasterServerUpdate():
                self.performMasterServerUpdate()       
        response = UDP_DEBUGR_RESPONSE
        responselen = struct.pack('B', len(response))
        return session + UDP_SERVER_RESPONSE + responselen + response

    def processTCP(self, data):
        packet = data[:4]
        unknown = data[4:4]
        #length = int(data[8:4].reverse(), 16)
        request = data[12:]
        print data

class TCPFactory(protocol.Protocol):   
    def __init__(self, master):
        self.server = master

    def doStart(self):
        pass

    def dataReceived(self, data):
        response = self.server.processTCP(data)
        if not response is None:
            self.transport.write(response)
        #verify data first then cancel kickCall
        self.kickCall.cancel()

    def connectionMade(self):
        self.kickCall = reactor.callLater(5, self.autoKick)

    def autoKick(self):
        self.transport.loseConnection()

    def connectionLost(self, reason):
        pass


class UDPFactory(protocol.DatagramProtocol):
    def __init__(self, master):
        self.server = master
    def doStart(self):
        pass

    def datagramReceived(self, data, address):
        if address[0] is CFG_MASTER_SERVER_IP:
            self.receiveMasterServerUpdate()
            return

        response = self.server.processUDP(data)
        if not response is None:
            self.transport.write(response, address)


def main():
    masterserver = CommunityServer()
    #reactor.listenTCP(54321,TCPFactory(masterserver))
    reactor.listenUDP(54321,UDPFactory(masterserver))
    reactor.run()

if __name__ == '__main__':
    main()