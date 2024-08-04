import sys
import os
import subprocess
import platform
import json
import create_vczp


CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def create_spec(file_name):
    if not os.path.exists(current_env):
        print(f"Diretório {current_env} não encontrado.")
        sys.exit(1)
    content = """
Name:
Version:
Author:
Description:
Architecture:
Licence:
SourceType:
installDir:
installDebugDir:

%prebuildsource

%buildsource

%install

%debuginstall

"""
    file_path = f"{current_env}/specs/{file_name}"
    with open(file_path, 'w') as f:
        f.write(content)
    f.close()


def verificar_gcc_instalado():
    try:
        # Executa o comando 'gcc --version' e captura a saída
        resultado = subprocess.run(['gcc', '--version'], capture_output=True, text=True)
        # Verifica se o GCC foi encontrado
        return resultado.returncode == 0
    except Exception as e:
        print(f"Erro ao verificar GCC: {e}")
        return False

def executar_comandos(comando, mensagem):
    print(f"{mensagem}: {comando}")
    sistema = platform.system()
    if sistema == "Windows":
        comando = comando.replace('/', '\\')  # Ajusta o comando para Windows
    resultado = subprocess.run(comando, shell=True)
    if resultado.returncode != 0:
        print(f"Erro ao executar o comando: {comando}")
        sys.exit(1)

def parse_spec(file_path):
    sections = {
        'Name': '',
        'Version': '',
        'Author': '',
        'installDir':'',
        'installDebugDir':'',
        'Description': '',
        'Architecture': '',
        'Licence': '',
        'SourceType': '',
        'prebuildsource': [],
        'buildsource': [],
        'install': [],
        'debuginstall': []
    }

    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('%'):
            current_section = line[1:].lower()
        elif current_section:
            line = line.replace("$current_env", current_env)
            line = line.replace("$files", "files")
            line = line.replace("$sources", "sources")
            line = line.replace("$debug", "debug")
            name =  sections['Name']
            name = name.lower()
            line = line.replace("$name", name)
            
            sections[current_section].append(line)
        else:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                print(value)
                if key in sections:
                    sections[key] = value
    
    return sections

def readSpec(file):
    if not os.path.exists(current_env):
        print(f"Diretório {current_env} não encontrado.")
        sys.exit(1)
    
    file_path = f"{current_env}/specs/{file}"

    if not os.path.exists(file_path):
        print(f"arquivo {file} não encontrado.")
        sys.exit(1)
    
    
    sections = parse_spec(file_path)

    if sections["SourceType"] == "C/C++":
        if not verificar_gcc_instalado():
            print("GCC não encontrado.")
            sys.exit(1)
        for prebuild in sections['prebuildsource']:
            print("Configurando..")
            executar_comandos(prebuild, "configurando compilação..")

        print("Compilando Projeto")
        for source in sections['buildsource']:
            executar_comandos(source, "compilando..")
        
        print("Preparando arquivos")
        name = sections['Name']
        name = name.lower()
        base_path = f"{current_env}/files"
        path = os.path.join(base_path, name)

        files_info = []
        file_info = create_vczp.create_list_files_info(path, base_path)
        files_info.append(file_info)
        files_info = create_vczp.inner_file_infos(files_info, base_path)
        
        path_vczp = f"{current_env}/output/{name}.vczp"

        debug_exec = False

        package_info = {
            "Name": sections["Name"],
            "Version": sections["Version"],
            "Author": sections["Author"],
            "Description": sections["Description"],
            "Architecture": sections["Architecture"],
            "installDir": sections["installDir"]
        }

        commands = []
        for command in sections["install"]:
            command_obj = {
                "command": command,
                "type":"release"
            }
            commands.append(command_obj)
        
        if sections['installDebugDir'] != None or sections['installDebugDir'] != "":
            debug_exec = True
            package_info["installDebugDir"] = sections['installDebugDir']
            if len(sections["debuginstall"]) > 0:
                for command in sections["debuginstall"]:
                    command_obj = {
                        "command": command,
                        "type":"debug"
                    }
                    commands.append(command_obj)
        create_vczp.pack_vczp(path_vczp, files_info, commands, package_info, base_path)
        if debug_exec == True:
            create_vczp.debug(path_vczp, current_env)
    else:
        print(f"Tipo de fonte {sections['SourceType']} não suportado.")
        sys.exit(1)


def create_env(env_name):
    print(env_name)
    os.makedirs(f"{env_name}/specs", exist_ok=True)
    os.makedirs(f"{env_name}/sources", exist_ok=True)
    os.makedirs(f"{env_name}/files", exist_ok=True)
    os.makedirs(f"{env_name}/output", exist_ok=True)
    os.makedirs(f"{env_name}/debug", exist_ok=True)
    print(f"Environment '{env_name}' created.")

def select_env(env_name):
    global current_env
    current_env = None
    if os.path.isdir(env_name):
        current_env = env_name
        save_config({'current_env': env_name})
        print(f"Switched to environment '{env_name}'.")
    else:
        print(f"Environment '{env_name}' does not exist.")

def exit_env():
    global current_env
    current_env = None
    if os.path.exists("config.json"):
        os.remove("config.json")
    print("Exited the current environment.")

def help():
    print("Uso: vczp [opção] <arquivos>")
    print("vczp-devel: --h: help")
    print("vczp-devel: Create Dir Structure")
    print("vczp-devel: --create <file.spec>: create spac file")
    print("vczp-devel: --create-env <env_name>: create env project")
    print("vczp-devel: --select-env <env_name>: select env project")
    print("vczp-devel: --exit-env: exit env project")
    print("vczp-devel: --make <file.spec>: build spec")

def main():
    global current_env
    config = load_config()
    current_env = config.get('current_env', None)


    if len(sys.argv) >1:
        args = sys.argv[1:]
        if args[0] == '--h':
            help()
        if args[0] == "--create":
            if current_env == None:
                print("Nenum ambiente selecionado.")
                sys.exit(1)
            if len(args) == 2:
                create_spec(args[1])
            else:
                help()
        if args[0] == "--make":
            if current_env == None:
                print("Nenum ambiente selecionado.")
                sys.exit(1)
            if len(args) == 2:
                readSpec(args[1])
            else:
                help()
        if args[0] == "--create-env":
            if len(args) == 2:
                create_env(args[1])
            else:
                help()
        if args[0] == "--select-env":
            if len(args) == 2:
                select_env(args[1])
            else:
                help()
        if args[0] == "--exit-env":
            exit_env()
    else:
        help()

if __name__ == "__main__":
    main()
