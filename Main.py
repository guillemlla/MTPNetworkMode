import GPIOManager as gpio
import Exceptions
import Constants as CTE


def begin():
    gpio.gpioSetup()
    mode = gpio.getMode()
    gpio.setLEDsMode(mode)

    if mode == CTE.TX_MODE:
        i = 1
        #do whatever
    elif mode == CTE.RX_MODE:
        i = 1
        #do whatever
    elif mode == CTE.NETWORK_MODE:
        i = 1
        #do whatever
    else:
        raise Exceptions.ModeError()

try:
    begin()
except Exceptions.ModeError():
    print("Error in the mode")
