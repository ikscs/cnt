#!/usr/local/bin/python
import os
import sys

def remove_it(path, size_bytes):

    get_files = lambda x : os.path.isfile(os.path.join(path,x))
    files_list = filter(get_files, os.listdir(path))

    st_file = []
    min_t = float('inf')
    max_t = 0
    min_s = float('inf')
    max_s = 0
    total_s = 0

    for f in files_list:
        st = os.stat(os.path.join(path, f))
        total_s += st.st_size
        min_t = min(min_t, st.st_mtime)
        max_t = max(max_t, st.st_mtime)
        min_s = min(min_s, st.st_size)
        max_s = max(max_s, st.st_size)
        st_file.append((f, st.st_size, st.st_mtime))

    delta_t = int(max_t - min_t) if max_t != min_t else 1
    delta_s = int(max_s - min_s) if max_s != min_s else 1

    fun = lambda x : ((x[1]-min_s)/delta_s) + ((x[2]-min_t)/delta_t)

    total = 0
    for f,s,t in sorted(st_file, key = fun, reverse=True):
        if total_s < size_bytes:
            break
        total_s -= s
        total += s
        os.remove(os.path.join(path, f))

    return f"Removed: {round(total/(1024*1024),3)} Mb"

def usage():
    print(f'Usage: {sys.argv[0]} sizeGb')
    print(f'Example: {sys.argv[0]} 30G')
    exit()

if __name__=='__main__':
    if len(sys.argv) != 2:
        usage()
    FOLDER = os.environ['DB_FOLDER']

    size = sys.argv[1]
    if size[-1] != 'G':
        usage()
    size_bytes = int(size[:-1])*1024*1024*1024

    result = remove_it(FOLDER, size_bytes)
    print(result)
