import subprocess
from pynput import keyboard

# Флаг для отслеживания состояния
is_black = True

# Пути к файлам
BLACK_IMAGE = "black.png"
VIDEO_FILE = "video.mp4"

# Процесс mpv
current_process = None

def run_command(command):
    global current_process
    # Если процесс уже запущен — убиваем его
    if current_process:
        current_process.terminate()
    # Запускаем новую команду
    current_process = subprocess.Popen(command, shell=True, env={"DISPLAY": ":0"})

def on_press(key):
    global is_black

    try:
        if key == keyboard.Key.f12:  # замените на нужную клавишу
            if is_black:
                run_command(f"mpv --vo=x11 --fullscreen --image-display-duration=inf {BLACK_IMAGE}")
            else:
                run_command(f"mpv --vo=x11 --fullscreen --loop-file=inf {VIDEO_FILE}")
            is_black = not is_black
    except Exception as e:
        print(f"Error: {e}")

def main():
    # Ловим нажатия клавиш
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
