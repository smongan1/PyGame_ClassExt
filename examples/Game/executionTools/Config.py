import configparser
import os

def parse(config_path):
    with open(config_path) as f:
        config_document = f.read()
    config = {}
    for line in config_document.split('\n'):
        if line.startswith('[') and line.endswith(']'):
            current_primary = line.split('[')[-1].split(']')[0].strip()
            if not current_primary in config: 
                config[current_primary] = {}
            continue
        if not line.strip():
            continue
        line = [x.strip() for x in line.split('=')]
        config[current_primary][line[0]] = line[1]
    dir_config_labels = ['\\', '/']
    for primary_key in config:
        for key in config[primary_key]:
            try: config[primary_key][key] = eval(config[primary_key][key])
            except: None
            
            if isinstance(config[primary_key][key],str):
                is_dir_config = any(dir_label in config[primary_key][key] for dir_label in dir_config_labels)
                if is_dir_config:
                    config[primary_key][key] = reformatDirConfig(config[primary_key][key])
                    
    return config

def printConfig(configs):
    print(" --- Using Configs --- ")
    for x in configs:
        print(x)
        for y in configs[x]:
            print('\t', y, ':', configs[x][y])
        print()
        
def reformatDirConfig(dir_config):
    dir_config = dir_config.split('\\')
    if len(dir_config) == 1:
        dir_config = dir_config[0].split('/')
    dir_config = [x for x in dir_config if x]
    dir_config = os.path.abspath(os.path.join(*dir_config))
    return dir_config