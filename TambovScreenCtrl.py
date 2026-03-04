import subprocess
from pynput import keyboard

# Флаг для отслеживания состояния
is_black = True

# Пути к файлам
BLACK_IMAGE = "black.png"
VIDEO_FILE = "video.mp4"

# Процесс mpv
current_process = None

def main():
   run_command(f"mpv --vo=x11 --fullscreen --image-display-duration=inf {BLACK_IMAGE}")
    
if __name__ == "__main__":
    main()
