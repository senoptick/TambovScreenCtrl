import os
import subprocess
import time
import gpiod
from gpiod.line import Direction


# ===== НАСТРОЙКИ =====
GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE = 17  # номер GPIO
BLACK_IMAGE = "black.png"
VIDEO_FILE = "video.mp4"

# =====================е

def start_mpv_controlled():
    global current_process
    if current_process is not None:
        current_process.terminate()
        current_process.wait()

    env = os.environ.copy()
    env["DISPLAY"] = ":0"

    current_process = subprocess.Popen([
        "mpv",
        "--vo=x11",
        "--fullscreen",
        "--idle=yes",                   # не выходить когда ничего не играет
        "--loop-playlist=inf",
        "--keepaspect=no",
        BLACK_IMAGE, VIDEO_FILE         # оба файла в плейлисте
    ], env=env, stdin=subprocess.PIPE)

    # даём mpv 1–2 секунды на запуск
    time.sleep(1.5)


def switch_to_black():
    if current_process and current_process.poll() is None:
        current_process.stdin.write(b"playlist-play-index 0\n")
        current_process.stdin.flush()


def switch_to_video():
    if current_process and current_process.poll() is None:
        current_process.stdin.write(b"playlist-play-index 1\n")
        current_process.stdin.flush()


def get_line_value(chip_path, line_offset):
    with gpiod.request_lines(
        chip_path,
        consumer="get-line-value",
        config={line_offset: gpiod.LineSettings(direction=Direction.INPUT)},
    ) as request:
        value = request.get_value(line_offset)
        return bool(value)


def main():
    start_mpv_controlled()

    
    try:
        while True:
            value = get_line_value(GPIO_CHIP, GPIO_LINE)
            print("GPIO 17: ", value)
            
            if value == 1:                    # замкнут → чёрный
                    if not is_black:
                        print("→ black")
                        switch_to_black()
                        is_black = True
            else:                             # разомкнут → видео
                if is_black:
                    print("→ video")
                    switch_to_video()
                    is_black = False

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Выход...")
        if current_process:
            current_process.terminate()

if __name__ == "__main__":
    main()
