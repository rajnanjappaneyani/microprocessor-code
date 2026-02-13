import serial
import serial.tools.list_ports
import time
import json


def find_first_polo_port(
    baudrate=9600,
    timeout=1,
    request=b"marco\n",
    expected_response=b'polo\r\n'
):
    ports = serial.tools.list_ports.comports()

    for port in ports:
        print(port)
        try:
            with serial.Serial(
                port=port.device,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            ) as ser:

                # Allow Arduino reset
                time.sleep(2)

                ser.reset_input_buffer()
                ser.reset_output_buffer()

                # Send "marco"
                ser.write(request)
                ser.flush()

                # Read response
                response = ser.readline()
                print(response)
                if response == expected_response:
                    return {
                        "port": port.device,
                        "description": port.description,
                        "manufacturer": port.manufacturer,
                        "product": port.product,
                        "hwid": port.hwid,
                        "vid": port.vid,
                        "pid": port.pid,
                        "serial_number": port.serial_number,
                    }

        except (serial.SerialException, OSError):
            continue

    return None


def write_dict_to_file(data: dict, filename: str):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    result = find_first_polo_port()

    if result:
        write_dict_to_file(result, "detected_port.txt")
        print("First responding port saved to detected_port.txt")
    else:
        print("No device responded with 'polo'")
