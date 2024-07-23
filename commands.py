import configparser

def addmod(uid: str, cpu: float, ram: int, storage: int):
    config = configparser.ConfigParser()

    config.read('/etc/setcap.ini')
    
    if ram and ram >= 0:
        config.set('RAMLimits', uid, str(ram))
    
    if cpu and cpu >= 0.0:
        config.set('CPULimits', uid, str(cpu))
    
    if storage and storage >= 0:
        config.set('DiskLimits', uid, str(storage))
    
    print("Here?")

    with open('/etc/setcap.ini') as config_file:
        config.write(config_file)



def delete(uid: int):
    print("Deleting...")

def view():
    print("Viewing...")

def edit():
    print("Editing...")

def install():
    print("Installing...")