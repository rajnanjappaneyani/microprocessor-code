import serial
import time


class ComWindow:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None

    def open(self):
        """Open the serial connection"""
        if not self.serial_conn or not self.serial_conn.is_open:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            # Allow device reset (important for Arduino)
            time.sleep(2)

    def close(self):
        """Close the serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()

    def write(self, message: str):
        """Send a string over serial"""
        if not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("Serial port not open")

        self.serial_conn.write((message + "\n").encode("utf-8"))
        self.serial_conn.flush()

    def read(self) -> str:
        """Read a line from serial"""
        if not self.serial_conn or not self.serial_conn.is_open:
            raise RuntimeError("Serial port not open")

        return self.serial_conn.readline().decode("utf-8", errors="ignore").strip()

    def print_write(self, message: str):
        """Print and send message"""
        print(f"[TX] {message}")
        self.write(message)

    def print_read(self) -> str:
        """Read and print incoming message"""
        response = self.read()
        if response:
            print(f"[RX] {response}")
        return response

    def flush(self):
        """Clear input and output buffers"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()

    def is_open(self) -> bool:
        """Check if serial port is open"""
        return self.serial_conn.is_open if self.serial_conn else False
