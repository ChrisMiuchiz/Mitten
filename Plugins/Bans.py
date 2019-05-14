from Packets.JoinPacket import JoinPacket
from Packets.ChatPacket import ChatPacket
import time

aBannedConnections = {}

def HandlePacket(connection, packet, fromClient):
    global aBannedConnections
    if type(packet) != JoinPacket and aBannedConnections.get(connection, False) is True and fromClient is True:
        return True
    elif aBannedConnections.get(connection, False) is True:
        return
    
    while True:
        try:
            with open('bans.txt', 'r') as f:
                IPs = [x.strip() for x in f.read().split('\n') if x.strip()]
        except FileNotFoundError:
            with open('bans.txt', 'w') as f:
                pass
        else:
            break

    IP = connection.ClientIP()
    if IP in IPs:
        #print(f'{IP} tried to connect, but they are banned.')
        aBannedConnections[connection] = True
        print(f'{IP} Is banned and thinks we care about his packets')
        #packet.Send(connection, fromClient)
        #newPacket = ChatPacket('You have been banned from this server.', 0)
        #newPacket.Send(connection, toServer=False)
        #time.sleep(1)
        #connection.Close()
        return
    
    
