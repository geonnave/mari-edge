from happyserial import HappySerial
import time

def _happyserial_rx_cb(buf):
    print('rx: {}'.format(buf))
    
happy = HappySerial.HappySerial(
    serialport = '/dev/ttyACM0',
    rx_cb      = _happyserial_rx_cb,
)


while True:
    happy.tx([0x01,0x02,0x03])
    time.sleep(1)
