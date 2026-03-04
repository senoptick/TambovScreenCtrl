import subprocess

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

def main():
   run_command(f"mpv --vo=x11 --fullscreen --image-display-duration=inf {BLACK_IMAGE}")
    
if __name__ == "__main__":
    main()
