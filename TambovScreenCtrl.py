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

# =====================

current_process = None
is_black = None  # текущее состояние

def run_mpv(args):
    global current_process

    if current_process:
        current_process.terminate()
        current_process.wait()

    env = os.environ.copy()
    env["DISPLAY"] = ":0"

    current_process = subprocess.Popen(args, env=env)

def show_black():
    run_mpv([
        "mpv",
        "--vo=x11",
        "--fullscreen",
        "--image-display-duration=inf",
        BLACK_IMAGE
    ])

def play_video():
    run_mpv([
        "mpv",
        "--vo=x11",
        "--fullscreen",
        "--loop-file=inf",
        VIDEO_FILE
    ])


def get_line_value(chip_path, line_offset):
    with gpiod.request_lines(
        chip_path,
        consumer="get-line-value",
        config={line_offset: gpiod.LineSettings(direction=Direction.INPUT)},
    ) as request:
        value = request.get_value(line_offset)
        return value


def main():
    global is_black
    try:
        while True:
            value = get_line_value(GPIO_CHIP, GPIO_LINE)
            print(value)
            # value == 0 → замкнут (на GND)
            if value == 0 and is_black is not True:
                print("Концевик замкнут → черный экран")
                show_black()
                is_black = True

            # value == 1 → разомкнут
            elif value == 1 and is_black is not False:
                print("Концевик разомкнут → запуск видео")
                play_video()
                is_black = False

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Выход...")
        if current_process:
            current_process.terminate()

if __name__ == "__main__":
    main()
