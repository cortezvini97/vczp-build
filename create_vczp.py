import struct
import os
import sys
import json
import subprocess
import platform

def executar_comandos(comando, mensagem):
    print(f"{mensagem}: {comando}")
    sistema = platform.system()
    if sistema == "Windows":
        comando = comando.replace('/', '\\')  # Ajusta o comando para Windows
    resultado = subprocess.run(comando, shell=True)
    if resultado.returncode != 0:
        print(f"Erro ao executar o comando: {comando}")
        sys.exit(1)

def get_files_folder_info(folder, files_info, base_path):
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_mtime = int(os.path.getmtime(file_path))  # Last modification time
            
            relative_path = os.path.relpath(file_path, base_path)
            if os.sep != '/':  # Adjust path separator for Windows
                relative_path = relative_path.replace(os.sep, '/')
            
            info = {
                "name": file_name,
                "type": "file",
                "path": relative_path,  # Use relative path
                "size": file_size,
                "mtime": file_mtime
            }
            files_info.append(info)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            dir_size = get_folder_size(dir_path)
            dir_mtime = int(os.path.getmtime(dir_path))  # Last modification time
            
            relative_path = os.path.relpath(dir_path, base_path)
            if os.sep != '/':  # Adjust path separator for Windows
                relative_path = relative_path.replace(os.sep, '/')
                
            info = {
                "name": dir,
                "type": "folder",
                "path": relative_path,  # Use relative path
                "size": dir_size,
                "mtime": dir_mtime
            }
            files_info.append(info)
    return files_info

  

def get_folder_size(folder):
    total_size = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except OSError as e:
                print(f"Erro ao acessar o arquivo {file_path}: {e}")
    return total_size

def create_list_files_info(path_or_file, base_path):
    info = {}
    if os.path.isdir(path_or_file):
        folder_name = os.path.basename(path_or_file)
        folder_size = get_folder_size(path_or_file)
        folder_mtime = int(os.path.getmtime(path_or_file))  # Last modification time
        
        info["name"] = folder_name
        info["type"] = "root_folder"
        info["path"] = os.path.relpath(path_or_file, base_path)  # Use relative path
        if os.sep != '/':  # Adjust path separator for Windows
            info["path"] = info["path"].replace(os.sep, '/')
        info["size"] = folder_size
        info["mtime"] = folder_mtime
        
    else:
        file_name = os.path.basename(path_or_file)
        file_size = os.path.getsize(path_or_file)
        file_mtime = int(os.path.getmtime(path_or_file))  # Last modification time
        
        info["name"] = file_name
        info["type"] = "file"
        info["path"] = os.path.relpath(path_or_file, base_path)  # Use relative path
        if os.sep != '/':  # Adjust path separator for Windows
            info["path"] = info["path"].replace(os.sep, '/')
        info["size"] = file_size
        info["mtime"] = file_mtime
    return info

def inner_file_infos(files_infos, base_dir):
    new_file_infos = []
    for file_info in files_infos:
        if file_info["type"] == "file":
            new_file_infos.append(file_info)
        elif file_info["type"] == "root_folder":
            new_file_infos.append(file_info)
            dir_file = os.path.join(base_dir, file_info["path"])
            get_files_folder_info(dir_file, new_file_infos, base_dir)
        elif file_info["type"] == "folder":
            new_file_infos.append(file_info)
            dir_file = os.path.join(base_dir, file_info["path"])
            get_files_folder_info(dir_file, new_file_infos, base_dir)
    return new_file_infos

def pack_vczp(path_vczp, files, commands, package_info, base_dir):
    print("criando ", path_vczp)
    print("Name: ", package_info["Name"])
    print("Version: ", package_info["Version"])
    print("Description: ", package_info["Description"])
    print("Author: ", package_info["Author"])
    print("Architecture: ", package_info["Architecture"])

    package_info_str = json.dumps(package_info)

    with open(path_vczp, 'wb') as archive:
        header = b'VCZP\x01'  # Magic number and version
        archive.write(header)
        archive.write(struct.pack('I', len(package_info_str)))
        archive.write(package_info_str.encode())

        archive.write(struct.pack('I', len(commands)))
        for command in commands:
            archive.write(struct.pack('I', len(command["command"])))
            archive.write(command["command"].encode())
            archive.write(struct.pack('I', len(command["type"])))
            archive.write(command["type"].encode())

        for file_obj in files:
            file_obj_name = file_obj["name"]
            file_obj_type = file_obj["type"]
            file_obj_path = file_obj["path"]
            file_obj_size = file_obj["size"]
            file_obj_mtime = file_obj["mtime"]

            archive.write(struct.pack('I', len(file_obj_name)))
            archive.write(file_obj_name.encode())

            archive.write(struct.pack('I', len(file_obj_type)))
            archive.write(file_obj_type.encode())

            archive.write(struct.pack('I', len(file_obj_path)))
            archive.write(file_obj_path.encode())

            archive.write(struct.pack('I', file_obj_size))
            archive.write(struct.pack('I', file_obj_mtime))

            dir_file_path = f"{base_dir}/{file_obj_path}"
            print(dir_file_path)

            if file_obj_type == "file":
                with open(dir_file_path, 'rb') as f:
                    data = f.read()
                    archive.write(data)

def debug(file_name, current_env):
    with open(file_name, 'rb') as archive:
        print("debug")
        # Read the header
        header = archive.read(5)
        if header != b'VCZP\x01':
            raise ValueError("Invalid file format")
        
        package_info_length = struct.unpack('I', archive.read(4))[0]
        package_info = json.loads(archive.read(package_info_length).decode())
        
        print("Name: ", package_info["Name"])
        print("Version: ", package_info["Version"])
        print("Description: ", package_info["Description"])
        print("Author: ", package_info["Author"])
        print("Architecture: ", package_info["Architecture"])

        commands_length = struct.unpack('I', archive.read(4))[0]
        
        for _ in range(commands_length):
            command_length = struct.unpack('I', archive.read(4))[0]
            command = archive.read(command_length).decode()
            type_length = struct.unpack('I', archive.read(4))[0]
            typeComand = archive.read(type_length).decode()
            if typeComand == "debug":
                print("Command: ", command)
                executar_comandos(command, "debug")

        while True:
            file_name_length_data = archive.read(4)
            if not file_name_length_data:
                break

            file_name_length = struct.unpack('I', file_name_length_data)[0]
            file_name = archive.read(file_name_length).decode()

            print("FILE_NAME: ", file_name)

            file_type_length = struct.unpack('I', archive.read(4))[0]
            file_type = archive.read(file_type_length).decode()

            file_path_length = struct.unpack('I', archive.read(4))[0]
            file_path = archive.read(file_path_length).decode()

            file_size = struct.unpack('I', archive.read(4))[0]
            file_mtime = struct.unpack('I', archive.read(4))[0]

            print(f"File: {file_name}, Type: {file_type}, Path: {file_path}, Size: {file_size}, Mtime: {file_mtime}")

            

            output_path = os.path.join(package_info['installDebugDir'], file_path)
            output_path = output_path.replace("$current_env", current_env)
            output_path = output_path.replace("$debug", "debug")

            print("FOLDER:> ", output_path)

            if file_type == "file":
                data = archive.read(file_size)
                with open(output_path, 'wb') as f:
                    f.write(data)
                print(f"Extracted {file_name} to {file_path}")
            elif file_type == "root_folder" or file_type == "folder":
                # Create the directory
                os.makedirs(output_path, exist_ok=True)
                os.utime(output_path, (file_mtime, file_mtime))