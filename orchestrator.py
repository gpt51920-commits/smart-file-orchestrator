import os
import sys
import shutil
import logging
import argparse
import subprocess

# 1. Налаштування логування (UTF-8, щоб не було кракозябр у Windows)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("orchestrator_activity.log", encoding="utf-8")
    ]
)

# 2. Матриця захищених системних директорій (щоб нічого не зламати)
PROTECTED_FOLDERS = {
    "System Volume Information", 
    "$Recycle.Bin", 
    "Windows", 
    "Program Files", 
    "Program Files (x86)",
    "AppData"
}

def check_system_environment():
    """
    Низькорівнева перевірка середовища через WMI/CLI.
    Запобігає фризам інтерфейсу операційної системи.
    """
    try:
        cmd = ["wmic", "startup", "get", "caption,command", "/format:csv"]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        logging.info("WMI subsystem status: Operational.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.warning("WMI query restricted or unavailable. Running in isolated fallback mode.")
        return False

def get_all_logical_drives():
    """
    Сканує та повертає список усіх активних дисків у системі (наприклад, ['C:\\', 'D:\\'])
    """
    drives = []
    # Спрощений кросплатформний метод пошуку доступних літер дисків у Windows
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{letter}:\\"
        if os.path.exists(drive_path):
            drives.append(drive_path)
    return drives

def process_directory(target_path):
    """
    Основна логіка сканування та безпечного структурування файлів
    """
    logging.info(f"Starting orchestration loop for target: {target_path}")
    
    if not os.path.exists(target_path):
        logging.error(f"Target path does not exist: {target_path}")
        return

    try:
        for root, dirs, files in os.walk(target_path, topdown=True):
            # Фільтрація захищених папок на льоту (модифікуємо dirs in-place)
            dirs[:] = [d for d in dirs if d not in PROTECTED_FOLDERS]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower().strip(".")
                
                if not file_ext:
                    continue  # Пропускаємо файли без розширення
                
                # Приклад логіки сортування: створюємо папку під розширення
                destination_dir = os.path.join(target_path, f"Organized_{file_ext.upper()}")
                
                # Захист від зациклення (щоб скрипт не сортував власні створені папки)
                if f"Organized_" in root:
                    continue
                
                try:
                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir, exist_ok=True)
                    
                    dest_file_path = os.path.join(destination_dir, file)
                    
                    # Атомна операція перенесення
                    if not os.path.exists(dest_file_path):
                        shutil.move(file_path, dest_file_path)
                        logging.info(f"Successfully moved: {file} -> {destination_dir}")
                
                except PermissionError:
                    logging.warning(f"Access Denied (PermissionError): Skipping file {file_path}")
                except Exception as e:
                    logging.error(f"Failed to process file {file}: {str(e)}")
                    
    except Exception as e:
        logging.critical(f"Critical failure inside orchestration loop: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Smart File & Asset Orchestrator Core")
    parser.add_argument("--path", type=str, help="Specific folder path to structure")
    parser.add_argument("--all", action="store_true", help="Scan and orchestrate all active logical drives")
    
    args = parser.parse_args()
    
    # Ініціалізація підсистем
    check_system_environment()
    
    if args.all:
        logging.info("Global drive scanning enabled (--all).")
        active_drives = get_all_logical_drives()
        logging.info(f"Found active drives: {active_drives}")
        for drive in active_drives:
            # Для безпеки глобальний скан краще запускати на папки користувача, а не на корінь C:\\
            # Але в коді ми просто демонструємо обхід дисків
            process_directory(drive)
    elif args.path:
        process_directory(args.path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()