import configparser
import caputils
import os
import pwd
import re
import subprocess
import grp

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
        config.remove_option('DiskLimits', uid)
    
    subprocess.run(["sudo", "setquota", "-u", uid, "0", "0", "0", "0", "/"])

    if os.path.isdir(f'/sys/fs/cgroup/{uid}'):
        subprocess.run(["sudo", "rmdir", f"/sys/fs/cgroup/{uid}"])
    
    if os.path.isfile(f'/etc/cgrules.conf'):
        contents = ""

        with open('/etc/cgrules.conf', "r") as file:
            contents = file.read()
        
        contents = re.sub(f"{caputils.name_from_uid(int(uid))}\\s*cpu,ram\\s*/sys/fs/cgroup/{uid}", "", contents)

        with open('/etc/cgrules.conf', "w") as file:
            file.write(contents)
    
    with open('/etc/setcap.ini', "w") as config_file:
        config.write(config_file)

def view():
    print(f"{"UID":<17}{"Username":<17}{"CPU Usage":<17}{"RAM Usage":<17}{"Storage Usage":<17}{"CPU Limit":<17}{"RAM Limit":<17}{"Storage Limit":<17}")
    print("-------------------------------------------------------------------------------------------------------------------------------------------")

    config = configparser.ConfigParser()
    ram_dict = {}
    cpu_dict = {}

    directory = os.fsencode("/proc")
    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if re.match("\\d+", filename):
            owner = None

            try:
                with open(f"/proc/{filename}/loginuid") as owner_file:
                    owner = owner_file.read()
                    owner = int(owner)

                    if(owner >= 4_000_000_000):
                        owner = 0
            except:
                continue
            
            if owner not in ram_dict:
                ram_dict[owner] = []
            
            if owner not in cpu_dict:
                cpu_dict[owner] = []

            ram = os.popen(f"""cat /proc/{filename}/smaps | grep -i pss |  awk '{{Total+=$2}} END {{print Total/1024/1024"GB"}}'""").read()
            ram = caputils.stringbytes_to_integer(ram, resource="RAM")

            cpu = os.popen(f"ps -p {filename} -o %cpu").read()
            cpu = re.sub("%CPU", "", cpu)
            cpu = cpu.strip(' \n\t')
            cpu = float(cpu)

            ram_dict[owner].append(ram)
            cpu_dict[owner].append(cpu)

    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)

    for p in pwd.getpwall():
        if p.pw_uid != 65534 and p.pw_uid >= 1000 or p.pw_uid == 0:
            ram_limit = None
            cpu_limit = None
            disk_limit = None

            disk_usage = None
            cpu_usage = 0.0
            ram_usage = 0.0

            if p.pw_uid in cpu_dict:
                cpu_usage = sum(cpu_dict[p.pw_uid])
                cpu_usage = round(cpu_usage, 2)
            
            if p.pw_uid in ram_dict:
                ram_usage = sum(ram_dict[p.pw_uid])


            if p.pw_uid != 0:
                disk_usage = caputils.get_size(f"/home/{p.pw_name}")
                disk_usage = caputils.integer_to_stringbytes(disk_usage)

            if config.has_option('RAMLimits', str(p.pw_uid)):
                ram_limit = config.get('RAMLimits', str(p.pw_uid))
                ram_limit = int(float(ram_limit))
                ram_limit = caputils.integer_to_stringbytes(ram_limit)
            
            if config.has_option('CPULimits', str(p.pw_uid)):
                cpu_limit = config.get('CPULimits', str(p.pw_uid))
            
            if config.has_option('DiskLimits', str(p.pw_uid)):
                disk_limit = config.get('DiskLimits', str(p.pw_uid))
                disk_limit = int(float(disk_limit))
                disk_limit = caputils.integer_to_stringbytes(disk_limit)
            
            print(f"{p.pw_uid:<17}{p.pw_name:<17}{str(cpu_usage) + "%":<17}{caputils.integer_to_stringbytes(ram_usage):<17}{disk_usage if disk_usage else "N/A":<17}{cpu_limit + "%" if cpu_limit else "N/A":<17}{ram_limit if ram_limit else "N/A":<17}{disk_limit if disk_limit else "N/A":<17}")
            print("-------------------------------------------------------------------------------------------------------------------------------------------")

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
    config = configparser.ConfigParser()

    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    storage_limits = dict(config.items('DiskLimits'))

    for uid in storage_limits:
        subprocess.run(["sudo", "setquota", "-u", uid, str(int(float(storage_limits[uid]))), str(int(float(storage_limits[uid]))), "0", "0", "/"])
    
    cpu_limits = dict(config.items("CPULimits"))

    for uid in cpu_limits:
        converted_limit = int(cpu_limits[uid]) * 10000

        if not os.path.isdir(f'/sys/fs/cgroup/{uid}'):
            os.system(f"sudo mkdir /sys/fs/cgroup/{uid}")
        
        os.system(f"""sudo echo "{converted_limit} 1000000" | sudo tee /sys/fs/cgroup/{uid}/cpu.max""")

    
    ram_limits = dict(config.items("RAMLimits"))

    for uid in ram_limits:
        if not os.path.isdir(f'/sys/fs/cgroup/{uid}'):
            os.system(f"sudo mkdir /sys/fs/cgroup/{uid}")
        
        os.system(f"""sudo echo "{int(float(ram_limits[uid]))}" | sudo tee /sys/fs/cgroup/{uid}/memory.max""")
    
    cgconfig_file = open("/etc/cgrules.conf", "w")
    
    cg_uids = list(ram_limits.keys()) + list(cpu_limits.keys())
    cg_uids = list(set(cg_uids))
    contents = ""
    
    for uid in cg_uids:
        contents += f"{caputils.name_from_uid(int(uid))} cpu,ram /sys/fs/cgroup/{uid}\n"

    cgconfig_file.write(contents)

    cgconfig_file.close()

    os.system(f"sudo cgrulesengd")