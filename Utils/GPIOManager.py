from Support import Constants as CTE
import RPi.GPIO as GPIO


def getMode():
    sw_1 = GPIO.input(CTE.SW_1)
    sw_2 = GPIO.input(CTE.SW_2)
    if not sw_1 and not sw_2:
        return CTE.TX_MODE
    elif not sw_1 and sw_2:
        return CTE.RX_MODE
    else:
        return CTE.NETWORK_MODE


def isAntennaReady():
    if GPIO.input(CTE.SW_7) == 1:
        return True


def setLEDsMode(mode):
    if mode == CTE.TX_MODE:
        setLeds(True, False, False)
    elif mode == CTE.RX_MODE:
        setLeds(False, True, False)
    else:
        setLeds(False, False, True)


def setLed(led,isOn):
    boolTranslation = {
        True: GPIO.HIGH,
        False: GPIO.LOW
    }
    GPIO.output(led, boolTranslation[isOn])


def setLeds(led1,led2,led3):
    setLed(CTE.LED_1,led1)
    setLed(CTE.LED_2,led2)
    setLed(CTE.LED_3,led3)


def gpioSetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    gpioOut = {CTE.LED_1, CTE.LED_2, CTE.LED_3, CTE.LED_4, CTE.LED_5}
    gpioIn = {CTE.SW_1, CTE.SW_2, CTE.SW_3, CTE.SW_4, CTE.SW_5, CTE.SW_6, CTE.SW_7, CTE.BTN_1, CTE.BTN_2, CTE.BTN_3}
    
    for gpio in gpioOut:
        GPIO.setup(gpio, GPIO.OUT)
        GPIO.output(gpio, GPIO.LOW)
        
    for gpio in gpioIn:
        GPIO.setup(gpio, GPIO.IN)

    mode = getMode()
    setLEDsMode(mode)
    print("[*] We are in mode ", CTE.MODE_SWITCH[mode])

