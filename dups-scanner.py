import subprocess
import os
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
import json
from tqdm import tqdm


def get_connected_hds():
    cmd = ['lsblk', '-o', 'NAME,TYPE,MOUNTPOINT', '--json']
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = json.loads(result.stdout)
    devices = output['blockdevices']

    hds = []
    for device in devices:
        if device['type'] == 'disk':
            if 'children' in device:
                for child in device['children']:
                    if child['type'] == 'part' and child['mountpoint']:
                        if 'SWAP' not in child['mountpoint'] and '/boot/' not in child['mountpoint']:
                            hds.append({'name': child['name'], 'mountpoint': child['mountpoint']})

    return hds

def get_files_from_hd(hd):
    print(f"Processando: {hd['name']}")
    root_dir = f"{hd['mountpoint']}/"
    file_list = []
    for dirpath, dirnames, filenames in tqdm(os.walk(root_dir)):
        for file in filenames:
            file_list.append(os.path.join(dirpath, file))
    return file_list



def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_metadata(file_path):
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1]
    file_size = os.path.getsize(file_path)
    file_location = file_path
    return {
        'name': file_name,
        'extension': file_extension,
        'size': file_size,
        'location': file_location
    }

def process_files_multithreaded(files, function):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(function, files))
    return results




def main():
    hds = get_connected_hds()
    print(hds)

    for hd in hds:
        filelist = get_files_from_hd(hd)
        print(f"{hd} tem {len(filelist)}")

main()