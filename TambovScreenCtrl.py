import os
import subprocess
import time

BLACK_IMAGE = "black.png"
VIDEO_FILE = "video.mp4"

current_process = None

def run_command(args):
    global current_process

    # Если mpv уже запущен — убиваем
    if current_process:
        current_process.terminate()
        current_process.wait()

    # Копируем текущее окружение
    env = os.environ.copy()
    env["DISPLAY"] = ":0"

    # Запускаем mpv
    current_process = subprocess.Popen(
        args,
        env=env
    )

def main():
    run_command([
        "mpv",
        "--vo=x11",
        "--fullscreen",
        "--image-display-duration=inf",
        BLACK_IMAGE
    ])

    # Держим скрипт живым
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if current_process:
            current_process.terminate()

if __name__ == "__main__":
    main()
