import os
import subprocess
import time
import socket
import json
import threading
import sys
import gpiod
from gpiod.line import Direction, Bias

GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE = 17
BLACK_IMAGE = "black.jpg"
VIDEO_FILE = "/content/video.mp4"
MPV_SOCKET = "/tmp/mpvsocket"
TCP_HOST = "0.0.0.0"
TCP_PORT = 5555

is_black = None
mpv_process = None

def start_mpv():
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    return subprocess.Popen([
        "mpv",
        "--vo=gpu",
        "--fullscreen",
        "--idle=yes",
        "--loop-file=inf",
        f"--input-ipc-server={MPV_SOCKET}",
        BLACK_IMAGE
    ], env=env)

def send_mpv_command(command):
    if not os.path.exists(MPV_SOCKET):
        return
    sock = socket.socket(socket.AF_UNIX)
    sock.connect(MPV_SOCKET)
    sock.send((json.dumps(command) + "\n").encode())
    sock.close()

def show_black():
    print("Черный экран")
    send_mpv_command({
        "command": ["loadfile", BLACK_IMAGE, "replace"]
    })

def play_video():
    print("Видео")
    send_mpv_command({
        "command": ["loadfile", VIDEO_FILE, "replace"]
    })

def get_line_value(chip_path, line_offset):
    with gpiod.request_lines(
        chip_path,
        consumer="limit_switch",
        config={line_offset: gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP)},
    ) as request:
        value = request.get_value(line_offset)
        return bool(value)

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_HOST, TCP_PORT))
        s.listen(1)
        print(f"TCP-сервер слушает {TCP_HOST}:{TCP_PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode().strip().lower()
                print(f"TCP команда от {addr}: {data}")

                if data == "poweroff":
                    print("Выключаю устройство...")
                    send_mpv_command({"command": ["quit"]})
                    time.sleep(0.3)
                    subprocess.run(["sudo", "poweroff"], check=False)
                    sys.exit(0)

def main():
    global is_black, mpv_process
    mpv_process = start_mpv()
    time.sleep(1)

    t = threading.Thread(target=tcp_server, daemon=True)
    t.start()

    try:
        while True:
            value = get_line_value(GPIO_CHIP, GPIO_LINE)
            print(value)
            if value == 1 and is_black is not True:
                show_black()
                is_black = True
            elif value == 0 and is_black is not False:
                play_video()
                is_black = False
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Выход...")
        if mpv_process:
            mpv_process.terminate()

if __name__ == "__main__":
    main()