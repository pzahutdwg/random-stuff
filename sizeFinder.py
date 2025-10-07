import os
from colorama import Fore
import time
import sys

basePath = input('Input the base path:\n> ')

try:
    os.chdir(basePath)
except FileNotFoundError:
    print(f'{basePath} is not a valid directory.')
except PermissionError:
    print(f'You do not have permission to view {basePath}.')
else:
    print(os.getcwd())
    print('Calculating total size', end='', flush=True)
    size = 0
    file_count = 0
    animation_chars = ['|', '/', '-', '\\']
    animation_index = 0
    
    for dirpath, dirnames, filenames in os.walk(basePath):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            try:
                size += os.path.getsize(filepath)
                file_count += 1
                
                # Show animation every 1000 files
                if file_count % 1000 == 0:
                    sys.stdout.write(f'\rCalculating total size {animation_chars[animation_index]}')
                    sys.stdout.flush()
                    animation_index = (animation_index + 1) % len(animation_chars)
                    
            except (OSError, FileNotFoundError):
                # Skip files that can't be accessed (e.g., system files, broken symlinks)
                continue
    
    print(f'\rThe contents of {basePath} occupy {size} bytes ({size / (1024 ** 3):.2f} GB) on disk.\n')
    warnPercent = float(input('Input the warning percentage (as a decimal, e.g., .02 for 2%): '))
    
    # Calculate size of each immediate subdirectory
    print('Analyzing subdirectories', end='', flush=True)
    otherSize = size
    basePath = os.path.normpath(basePath)  # Normalize the path
    subdirs = [item for item in os.listdir(basePath) if os.path.isdir(os.path.join(basePath, item))]
    
    dot_count = 0
    file_counter = 0
    for i, item in enumerate(subdirs):
        item_path = os.path.join(basePath, item)
        subdir_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(item_path):
                for file in filenames:
                    filepath = os.path.join(dirpath, file)
                    try:
                        subdir_size += os.path.getsize(filepath)
                        file_counter += 1

                        # Show dots animation every 2000 files
                        if file_counter % 2000 == 0:
                            dots = '.' * ((dot_count % 3) + 1)
                            sys.stdout.write(f'\rAnalyzing subdirectories{dots}   ')
                            sys.stdout.flush()
                            dot_count += 1
                            
                    except (OSError, FileNotFoundError):
                        continue
            if subdir_size > size * warnPercent:
                print(f'\r{item_path} takes up {Fore.RED}{subdir_size/size:.2%}{Fore.RESET} of the total size.')
                otherSize -= subdir_size
        except (OSError, PermissionError):
            # Skip directories we can't access
            continue
    
    print(f'\rOther files and directories take up {Fore.YELLOW}{otherSize/size:.2%}{Fore.RESET} of the total size.')
