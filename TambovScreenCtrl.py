import os
import subprocess
import time
import gpiod

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

def main():
    global is_black

    chip = gpiod.Chip(GPIO_CHIP)
    line = chip.get_line(GPIO_LINE)

    line.request(consumer="limit_switch",
                 type=gpiod.LINE_REQ_DIR_IN,
                 flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)

    print("Система запущена...")

    try:
        while True:
            value = line.get_value()

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
