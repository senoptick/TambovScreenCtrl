import os
import subprocess
import time
import gpiod

# ===== НАСТРОЙКИ =====
GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE = 17
BLACK_IMAGE = "black.png"
VIDEO_FILE = "video.mp4"
# =====================

current_process = None
is_black = None

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

    with gpiod.Chip(GPIO_CHIP) as chip:

        # В libgpiod v2 используется request_lines
        request = chip.request_lines(
            consumer="limit_switch",
            config={
                GPIO_LINE: gpiod.LineSettings(
                    direction=gpiod.LineDirection.INPUT,
                    bias=gpiod.LineBias.PULL_UP
                )
            }
        )

        print("Система запущена...")

        try:
            while True:
                value = request.get_value(GPIO_LINE)

                if value == 0 and is_black is not True:
                    print("Замкнут → черный экран")
                    show_black()
                    is_black = True

                elif value == 1 and is_black is not False:
                    print("Разомкнут → видео")
                    play_video()
                    is_black = False

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Выход...")
            if current_process:
                current_process.terminate()

if __name__ == "__main__":
    main()
