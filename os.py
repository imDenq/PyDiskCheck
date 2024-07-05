import os
import concurrent.futures
from tqdm import tqdm

def get_size(path):
    total_size = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += get_size(entry.path)
    except PermissionError:
        print(f"Permission denied: {path}")
    except Exception as e:
        print(f"Error accessing {path}: {e}")
    return total_size

def scan_directory(path, files_and_dirs, pbar):
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                try:
                    files_and_dirs.append((entry.path, entry.stat().st_size))
                except PermissionError:
                    print(f"Permission denied: {entry.path}")
                except Exception as e:
                    print(f"Error accessing {entry.path}: {e}")
            elif entry.is_dir():
                try:
                    dir_size = get_size(entry.path)
                    files_and_dirs.append((entry.path, dir_size))
                except PermissionError:
                    print(f"Permission denied: {entry.path}")
                except Exception as e:
                    print(f"Error accessing {entry.path}: {e}")
            pbar.update(1)
    except PermissionError:
        print(f"Permission denied: {path}")
    except Exception as e:
        print(f"Error accessing {path}: {e}")

def main():
    path = "C:/"
    files_and_dirs = []

    num_items = sum([len(files) + len(dirs) for _, dirs, files in os.walk(path)])

    with tqdm(total=num_items, desc="Scanning files and directories") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    dir_full_path = os.path.join(root, d)
                    futures.append(executor.submit(scan_directory, dir_full_path, files_and_dirs, pbar))
                for f in files:
                    file_full_path = os.path.join(root, f)
                    try:
                        if os.path.exists(file_full_path):
                            files_and_dirs.append((file_full_path, os.path.getsize(file_full_path)))
                            pbar.update(1)
                    except PermissionError:
                        print(f"Permission denied: {file_full_path}")
                    except Exception as e:
                        print(f"Error accessing {file_full_path}: {e}")
                        
            for future in concurrent.futures.as_completed(futures):
                future.result()

    files_and_dirs.sort(key=lambda x: x[1], reverse=True)
    
    print("Top 10 largest files and directories:")
    for item in files_and_dirs[:10]:
        print(f"{item[0]}: {item[1]/(1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
