# SPDX-FileCopyrightText: 2022-present Inria
# SPDX-FileCopyrightText: 2022-present Alexandre Abadie <alexandre.abadie@inria.fr>
# SPDX-FileCopyrightText: 2025-present Geovane Fedrecheski <geovane.fedrecheski@inria.fr>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Serial interface using HappySerial."""

import logging
import sys
import threading
from typing import Callable

from serial.tools import list_ports
from happyserial import HappySerial

SERIAL_DEFAULT_PORT = "/dev/ttyACM0"
SERIAL_DEFAULT_BAUDRATE = 115_200


def get_default_port():
    """Return default serial port."""
    ports = [port for port in list_ports.comports()]
    if sys.platform != "win32":
        ports = sorted([port for port in ports if "J-Link" == port.product])
    if not ports:
        return SERIAL_DEFAULT_PORT
    # return first JLink port available
    return ports[0].device


class SerialInterfaceException(Exception):
    """Exception raised when serial port is disconnected."""


class SerialInterfaceHappy:
    """Bidirectional serial interface using HappySerial."""

    def __init__(self, port: str, baudrate: int, callback: Callable):
        self.lock = threading.Lock()
        self.callback = callback
        self.port = port
        self.baudrate = baudrate
        self._logger = logging.getLogger(__name__)
        
        try:
            self.happy_serial = HappySerial.HappySerial(
                serialport=port,
                # baudrate=baudrate,
                rx_cb=self._rx_callback,
            )
            self._logger.info(f"HappySerial initialized on {port} at {baudrate} baud")
        except Exception as exc:
            self._logger.error(f"Failed to initialize HappySerial: {exc}")
            raise SerialInterfaceException(f"Failed to initialize HappySerial: {exc}") from exc

    def _rx_callback(self, data):
        """Internal callback that forwards data to the user callback."""
        try:
            # HappySerial provides data as a list of bytes, convert to bytes object
            if isinstance(data, list):
                data = bytes(data)
            # print(f">>> Received data: {data}")
            self.callback(data)
        except Exception as exc:
            self._logger.error(f"Error in rx callback: {exc}")

    def stop(self):
        """Stop the serial interface."""
        try:
            if hasattr(self.happy_serial, 'close'):
                self.happy_serial.close()
            elif hasattr(self.happy_serial, 'stop'):
                self.happy_serial.stop()
        except Exception as exc:
            self._logger.error(f"Error stopping HappySerial: {exc}")

    def write(self, data):
        """Write bytes on serial."""
        try:
            # Convert bytes to list if needed (HappySerial might expect a list)
            if isinstance(data, bytes):
                data = list(data)
            self.happy_serial.tx(data)
        except Exception as exc:
            self._logger.error(f"Error writing to serial: {exc}")
            raise SerialInterfaceException(f"Error writing to serial: {exc}") from exc
