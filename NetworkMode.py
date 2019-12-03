import Constants as CTE
import PacketManager 
import FancyDataSender
import time 

#This function returns one dictionary (ID:reply) and a boolean 'everyoneHasTheFile'
#Reply values:
#   reply = NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD
#   reply = NETWORK_PAQUET_CONTROL_REPLY_NO_PAYLOAD
#   reply = None
#everyoneHasTheFile -> Boolean that says if all the nodes have the file-

#def polling(source,dest1,dest2,payload,timeout = 5, token):
def polling(source, token):
    ID = FancyDataSender.BaseDataSender.address
    thereIsReply = False
    IDdict = {1:None, 2:None, 3:None, 4:None, 5:None, 6:None, 7:None, 8:None}
    timeout = 5
    for x in range(1,8) :
        dest1 = x
        dest2 = x
        if dest1 != ID :
            data=PacketManager.createNetworkPacket(CTE.NETWORK_PAQUET_CONTROL_HELLO_PAYLOAD,source,dest1,dest2,0,0,CTE.NETWORK_PAQUET_TYPE_CONTROL)            
            FancyDataSender.BaseDataSender.sendData(data)
            time_first = time.time()
            while True :
                response = FancyDataSender.BaseDataSender.receiveMessage()
                time_actual = time.time()
                if time_actual >=  time_first + timeout :
                    break
                if response is not None :
                    #From received data take an integer number:
                    intValue = int.from_bytes(response, 'big')
                    if (intValue == CTE.NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD):  #Received reply yes
                        IDdict.update(dest1=CTE.NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD)
                        thereIsReply = True
                        #Do whatever
                    elif (intValue == CTE.NETWORK_PAQUET_CONTROL_REPLY_NO_PAYLOAD) :
                        IDdict.update(dest1=CTE.NETWORK_PAQUET_CONTROL_REPLY_NO_PAYLOAD)
                    break
   
    if thereIsReply == False :
        everyoneHasTheFile = check_token(token)
    return (IDdict, everyoneHasTheFile)
                
def check_token(token) :
    for x in range(0,15) :
        if ((x % 2) != 0) :
            if (token[x] == 0) :
                return False
    return True
    