import struct
import io
from CubeTypes import Airship
from net import recv2
from .Packet import Packet
class AirTrafficPacket(Packet):
    pID = 0x3
    def __init__(self, airships):
        self.airships = airships
        self.count = len(airships)

    @staticmethod
    def Recv(connection, fromClient):
        recv = [connection.RecvServer, connection.RecvClient][fromClient]
        airshipsCount, = struct.unpack('<I', recv(4))
        airships = []
        for _ in range(airshipsCount):
            airships += Airship.Import(recv(120))
        return AirTrafficPacket(airships)

    def Export(self, toServer):
        packetByteList = []
        packetByteList.append( struct.pack('<I', pID) )
        packetByteList.append( struct.pack('<I', self.count) )
        for ship in self.airships:
            packetByteList.append( ship.Export() )
        return b''.join(packetByteList)

    def Send(self, connection, toServer):
        send = [connection.SendClient, connection.SendServer][toServer]
        return send(self.Export(toServer))
