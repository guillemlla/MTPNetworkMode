import Constants as CTE
import PacketManager 
import FancyDataSender
import time 


def polling(sorce,dest1,dest2,payload,timeout):
    ID=FancyDataSender.BaseDataSender.address
    max_time = time.time() + timeout
    
    for x in range(1,8) :
        dest1 = x
        dest2 = x
        if dest1 != ID :
            data=PacketManager.createNetworkPacket(CTE.NETWORK_PAQUET_CONTROL_HELLO_PAYLOAD, sorce,dest1,dest2,0,0,CTE.NETWORK_PAQUET_TYPE_CONTROL)            
        FancyDataSender.BaseDataSender.sendData(self,data)
        time_first = time.time()
        while True :
            response = FancyDataSender.BaseDataSender.receiveMessage()
            time_actual = time.time()
            if time_actual >=  time_first + 5 :
                break
            if response is not None :
                break