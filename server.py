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

def HELPER_fetchNameString(playerString):
    players = []
    for player in playerString.split(', '):
        players.append(player.replace("\xA7(10)\x1B","").replace("\x1C\xA7(-1)\x1B","").strip())
    return players

def HELPER_dictionaryToDataString(dataIn):
    conversion = ''
    for x,y in dataIn:
        conversion += ';' + x + '=' + y
    return conversion

def HELPER_dataStringToDictionary(dataIn):
    conversion = {}
    for x in dataIn.split(';'):
        y,z = x.split('=')
        if len(y) > 0:
            conversion[y] = z
    return conversion


class MultiplayerSession():
    def __init__(self, data):
        for x,y in data.iteritems():
            setattr(self, x, y)

    def getAsGameString(self):
        temp_dict = {}
        for x in dir(self).remove('__doc__').remove('__module__'):
            temp_dict[x] = getattr(self, x)
        temp_dict['players'] = HELPER_buildNameString(temp_dict['players']) 
        return HELPER_dictionaryToDataString(temp_dict)

class CommunityServer():
    def __init__(self):
        self.sessions = {}
    #byte 3 should be mode \x00, ignore? byte 4 should be content-len, ignore?
    def checkMasterServerUpdate(self):
        return True
    
    def performMasterServerUpdate(self, modname=''):
        request = UDP_DEBUGR_REQUEST.format(modname)
        requestlen = struct.pack('B', len(request))
        self.transport.write("\x13\x37\x00"+requestlen+request, (CFG_MASTER_SERVER_IP, 54321))
    
    def receiveMasterServerUpdate(self, request):
        pass #process data here

    def startSession(self, data, modname=''):
        newGame = MultiplayerSession(data)
        newGame.mod = modname #omit me maybe
        if not modname in self.sessions:
            self.sessions[modname] = {}
        self.sessions[modname][data['server_addr']] = newGame
        return newGame

    def endSession(self, session):
        self.sessions[session.mod].pop(session.server_addr, None)

    def processUDP(self, data):
        session = data[:2]  
        mode = data[3]
        length = int(data[4].encode('hex'), 16)
        request = HELPER_dataStringToDictionary(data[4:])

        print 'UDP', request
        #if mode == UDP_SERVER_RESPONSE:
        #    return #u what mate
        #else: #master response should not trigger update call
        #    if self.checkMasterServerUpdate():
        #        self.performMasterServerUpdate()       
        #response = UDP_DEBUGR_RESPONSE
        if not 'mod' in request:
            request['mod'] = ''

        for x,y in self.sessions[request['mod']].iteritems():
            response = y.getAsGameString()
            responselen = struct.pack('B', len(response))
            yield session + UDP_SERVER_RESPONSE + responselen + response

    def processTCP(self, data):
        packet = int(data[:4].encode('hex'), 16)
        #unknown = data[4:8]
        length = int(data[8:12][::-1].encode('hex'), 16) #little edian (wtf!)
        request = data[12:12+length]
        print 'TCP', request
        return packet, length, request

class TCPComProtocol(protocol.Protocol):   
    def __init__(self):
        self.session = None

    def doStart(self):
        pass

    def dataReceived(self, data):
        packet, length, request_raw = self.factory.master.processTCP(data)
        request = HELPER_dataStringToDictionary(request_raw) 
        if 'players' in request:
            request['players'] = HELPER_fetchNameString(request['players'])
        request['server_addr'] = self.transport.getPeer().host
        print request
        if self.session is None:
            self.session = self.factory.master.startSession(request)
        else: #update?
            for x,y in request.iteritems():
                setattr(self.session, x, y)
        if not self.kickCall is None:
            self.kickCall.cancel()
            self.kickCall = None

    def connectionMade(self):
        self.kickCall = reactor.callLater(5, self.autoKick)

    def autoKick(self):
        if not self.session is None:
            if self.factory.master.endSession(self.session):
                self.session = None
                self.isHost = False
        self.transport.loseConnection()

    def connectionLost(self, reason):
        if not self.session is None:
            self.factory.master.endSession(self.session)

class UDPComProtocol(protocol.DatagramProtocol):
    def __init__(self, master):
        self.server = master
    def doStart(self):
        pass
    def datagramReceived(self, data, address):
        #if address[0] is CFG_MASTER_SERVER_IP:
        #    self.receiveMasterServerUpdate(data)
        #    return
        for response in self.server.processUDP(data):
            self.transport.write(response, address)

def main():
    masterserver = CommunityServer()
    factory = protocol.ServerFactory()
    factory.protocol = TCPComProtocol
    factory.master = masterserver
    reactor.listenTCP(54321, factory)
    reactor.listenUDP(54321, UDPComProtocol(masterserver))
    reactor.run()

if __name__ == '__main__':
    main()