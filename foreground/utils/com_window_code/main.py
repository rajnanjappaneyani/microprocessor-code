import asyncio
from datetime import datetime

import comencment_marco_polo_code
from init import ComWindow  # adjust if your module name differs

LISTEN_PORT = 80  # change to 8080 if port 80 permission issues


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def tx(label: str, msg: str):
    print(f"[{now()}] [TX {label}] {msg!r}",flush=True)


def rx(label: str, msg: str):
    print(f"[{now()}] [RX {label}] {msg!r},",flush=True)


def handshake(com: ComWindow, verbose: bool):
    if verbose:
        tx("SER", "marco")
    com.write("marco")
    print("marco",flush=True)
    r = com.read().strip().lower()
    if verbose:
        rx("SER", r)
    if r != "polo":
        raise RuntimeError(f"Expected 'polo', got {r!r}")

    if verbose:
        tx("SER", "success")
    com.write("success")
    print("success",flush=True)
    r = com.read().strip().lower()
    if verbose:
        rx("SER", r)
    if r != "ok":
        raise RuntimeError(f"Expected 'ok', got {r!r}")


def send_and_read(com: ComWindow, msg: str, verbose: bool) -> str:
    if verbose:
        tx("SER", msg)
    print(msg,flush=True)
    com.write(msg)
    r = com.read().strip()
    if verbose:
        rx("SER", r)
    return r


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, com: ComWindow):
    peer = writer.get_extra_info("peername")
    print(f"[{now()}] TCP connected from {peer}",flush=True)

    try:
        data = await reader.read(4096)
        if not data:
            return

        x = data.decode("utf-8", errors="replace").strip()
        print(f"[{now()}] TCP RX x={x!r}")

        # previous_x is the TCP x from the previous run
        previous_x = getattr(handle_client, "previous_x", None)

        # First phase: do not spam logs until equality becomes true
        verbose = False

        # Run marco/polo + success/ok
        handshake(com, verbose)

        # Send x to Arduino and read y back
        y = send_and_read(com, x, verbose)
        print(f"[{now()}] Stored y={y!r} (from Arduino)",flush=True)

        # Update previous_x for next session
        setattr(handle_client, "previous_x", x)

        # Equality condition: y == previous_x(previous)
        if previous_x is not None and y == previous_x:
            print(f"[{now()}] CONDITION TRUE: y == previous_x -> communication started")
            verbose = True

            # From this point: print all inputs/outputs on terminal and run correction flow
            r1 = send_and_read(com, "(1,2,3,correction)", verbose)
            # If you want strict validation, uncomment:
            # if r1 != "((1,2,3),(3,4,5))": raise RuntimeError(f"Unexpected r1: {r1!r}")

            r2 = send_and_read(com, "(1,4,5,correction)", verbose)
            # if r2 != "((1,4,5),(1,3,5))": raise RuntimeError(f"Unexpected r2: {r2!r}")

        else:
            print(f"[{now()}] CONDITION FALSE: y != previous_x (previous_x={previous_x!r})")

        # You requested no OK/no_correction messaging. So we do not send status.
        # Close the TCP connection quietly.

    except Exception as e:
        # For debugging: still send an error line (optional). Remove if you want silence.
        try:
            writer.write(f"ERR:{e}\n".encode("utf-8", errors="replace"))
            await writer.drain()
        except Exception:
            pass

    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        print(f"[{now()}] TCP disconnected from {peer}")


async def main():
    # Discover Arduino and open serial once
    result = comencment_marco_polo_code.find_first_polo_port()
    if not result:
        print("No device responded with 'polo'",flush=True)
        raise SystemExit(1)

    comencment_marco_polo_code.write_dict_to_file(result, "detected_port.txt")
    print(f"[{now()}] Detected port saved: {result['port']}",flush=True)

    com = ComWindow(port=result["port"], baudrate=9600, timeout=2)
    com.open()
    com.flush()

    server = await asyncio.start_server(lambda r, w: handle_client(r, w, com),
                                        host="0.0.0.0",
                                        port=LISTEN_PORT)
    print(f"[{now()}] Listening on 0.0.0.0:{LISTEN_PORT}",flush=True)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        print(f"running", flush=True)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down.")
