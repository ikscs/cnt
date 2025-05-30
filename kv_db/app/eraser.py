#!/usr/local/bin/python
import os
import sys
import time

def delete_files(folder_path, max_size_bytes, cutoff, conditions):
    size, count = 0, 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_size = os.path.getsize(file_path)

            size_condition = bool(file_size > max_size_bytes)
            time_condition = bool(os.path.getmtime(file_path) < cutoff)

            if (size_condition, time_condition) == conditions:
                os.remove(file_path)
                size += file_size
                count += 1
        break
    return count, size

def usage():
    print(f'Usage: {sys.argv[0]} +-sizeKb +-days')
    print(f'Example: {sys.argv[0]} +100k +5')
    exit()

if __name__=='__main__':
    if len(sys.argv) != 3:
        usage()
    FOLDER = os.environ['DB_FOLDER']
    #FOLDER = '/var/screenshots'
    now = time.time()

    size = sys.argv[1]
    if (size[0] not in '+-') or (size[-1] != 'k'):
        usage()
    size_bytes = int(size[1:-1])*1024

    days = sys.argv[2]
    if (days[0] not in '+-'):
        usage()
    cutoff = now - int(days[1:]) * (24 * 3600)

    conditions = (bool(size[0]=='+'), bool(days[0]=='+'))
    count, size = delete_files(FOLDER, size_bytes, cutoff, conditions)
    print(f'{count} files deleted. {int(size/1024)} Kbytes free.')
