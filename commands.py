import configparser
import os

def addmod(uid: str, cpu: float, ram: int, storage: int):
    config = configparser.ConfigParser()
    
    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    if ram and ram >= 0:
        config.set('RAMLimits', uid, str(ram))
    
    if cpu and cpu >= 0.0:
        config.set('CPULimits', uid, str(cpu))
    
    if storage and storage >= 0:
        config.set('DiskLimits', uid, str(storage))

    with open('/etc/setcap.ini', "w") as config_file:
        config.write(config_file)



def delete(uid: str):
    config = configparser.ConfigParser()

    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    if config.has_option('RAMLimits', uid):
        config.remove_option('RAMLimits', uid)
    
    if config.has_option('CPULimits', uid):
        config.remove_option('CPULimits', uid)
    
    if config.has_option('DiskLimits', uid):
        config.remove_option('Disklimits', uid)
    
    with open('/etc/setcap.ini', "w") as config_file:
        config.write(config_file)

def view():
    print("Viewing...")

def editor(app: str):
    config = configparser.ConfigParser()

    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    if app:
        config.set("Editor", 'app', app)

        with open('/etc/setcap.ini', "w") as config_file:
            config.write(config_file)
    
    os.system(f"sudo {config['Editor']['app']} /etc/setcap.ini")

def install():
    print("Installing...")