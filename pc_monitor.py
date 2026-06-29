import time
import json
import datetime
import psutil
import serial
import serial.tools.list_ports as list_ports

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200


def find_pico():
    ports = list_ports.comports()
    for p in ports:
        if 'MicroPython' in p.description or 'RP2350' in p.description or 'ttyACM' in p.device:
            return p.device
    return None


def connect():
    while True:
        port = find_pico()
        if port is None:
            port = SERIAL_PORT
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=1)
            print(f"Connected to RP2350 on {port}")
            return ser
        except Exception as e:
            print(f"Waiting for RP2350... ({e})")
            time.sleep(2)


ser = connect()
old_net = psutil.net_io_counters()

while True:
    now = datetime.datetime.now().strftime("%H:%M:%S")

    cpu_per = psutil.cpu_percent(interval=0.5)

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    proc_count = len(psutil.pids())

    try:
        batt = psutil.sensors_battery()
        batt_pct = batt.percent if batt else None
    except:
        batt_pct = None

    try:
        top_proc = sorted(psutil.process_iter(['name', 'cpu_percent']),
                          key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[0]
        top_name = top_proc.info['name'][:12] if top_proc.info['name'] else "?"
    except:
        top_name = "?"

    new_net = psutil.net_io_counters()
    sent = (new_net.bytes_sent - old_net.bytes_sent) / 1024 / 0.5
    recv = (new_net.bytes_recv - old_net.bytes_recv) / 1024 / 0.5
    old_net = new_net

    data = {
        "time": now,
        "cpu": f"{cpu_per}%",
        "ram": f"{ram.percent}%",
        "disk": f"{disk.percent}%",
        "battery": f"{batt_pct:.0f}%" if batt_pct is not None else "N/A",
        "top": top_name,
        "up": f"{sent:.1f}K",
        "down": f"{recv:.1f}K"
    }

    payload = json.dumps(data) + "\n"
    try:
        ser.write(payload.encode('utf-8'))
    except serial.SerialException:
        print("RP2350 disconnected, waiting for reconnection...")
        ser.close()
        ser = connect()
        print("Reconnected!")

    time.sleep(0.5)
