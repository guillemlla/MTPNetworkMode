import Rx as rx
import Tx as tx
import PacketManager as pm
import Support.Constants as CTE
import random
import passive_node

FileAlreadyReceived = False

def network_mode(own_address):
    receiver = rx()
    transmiter = tx()
    # State ens indica si es un node actiu o no
    active_state = False

    rpistr = "ls /media/pi"
    USB_name = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE)
    line = USB_name.stdout.readline()

    # Comprovem que hi ha un usb enxufat
    if line:
        active_state = True

    finished = False
    historical_data = None
    while not finished:
        if active_state:
            active_node(transmiter, receiver, historical_data)
        else:
            active_state = passive_node(transmiter, receiver)


def active_node(transmiter, receiver, hist):
    send_hello(transmiter, receiver)

    messages = []
    # Aqui s'ha de fer lo del pooling (igual fer-ho com a funció)
    while not time_out():
        receiver.receivePacket()
        new_message = receiver.message
        messages.append(new_message)
    # Aqui s'ha de fer lo del pooling

    destinations = []
    for m in messages:
        source, dest1, dest2, _, sequenceNumber, packetType = pm.readNetworkHeader(m[0:2])
        if (m[2] == CTE.NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD):
            destinations.append(source)

    history = hist
    new_token_owner = destinations[random.randint(len(destinations))]
    for d in destinations:
        send_file(d, transmiter)
        if d == new_token_owner:
            history = history + str(d) + "1"
        else:
            history = history + str(d) + "0"

    pass_token(new_token_owner, history, tx)

    return history



def pass_token(dest, history, tx):
    packet = pm.createNetworkPacket(history, data, dest, dest, 0, 0, CTE.NETWORK_PAQUET_TYPE_PASSTOKEN)
    tx.sendPacket(packet)

#functions to let other modules to know if the file already exists on current device
def setFileAlreadyReceived( FileReceived ):
    FileAlreadyReceived = FileReceived

def isFileAlreadyReceived():
    return FileAlreadyReceived

def send_file(dest, transmiter):




