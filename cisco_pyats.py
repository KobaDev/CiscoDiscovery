from pyats.topology import loader
from genie.testbed import load
from genie.libs.parser.utils.common import get_parser



class device:
    def __init__(self,
                 hostname,
                 ip,
                 serial_number,
                 device_type,
                 equipment_model,
                 connections):
        self.hostname: str = hostname
        self.ip: list = ip
        self.serial_number: str = serial_number
        self.device_type: str = device_type
        self.equipment_model: str = equipment_model
        self.connections: list = connections


def get_info(device):

    # Connections
    testbed = loader.load(f'./testbed.yaml')                                            # Step 0: load the testbed
    device_target = testbed.devices[device]                                                    # Step 1: testbed is a dictionary. Extract the device device_target
    device_target.connect(init_exec_commands=[], init_config_commands=[], log_stdout=False)    # Step 2: Connect to the device

    # Misc executables
    # cmd = device_target.execute('show version')
    cmd_version = device_target.parse('show version')
    cmd_running_config = device_target.parse('show running-config')

    # Getting hostname:
    cmd_hostname_execute = device_target.execute('show hosts')                                  # The DevBox doesn't set a hostname, so mock data will be used
    hostname = cmd_hostname_execute.splitlines()
    hostname = hostname[3]

    # Getting ip:
    ips = []
    cmd_ip = device_target.parse('show ipv4 interface brief')
    for intf, data in cmd_ip['interface'].items():
        data = {intf: data['ip_address']}
        ips.append(data)

    # Getting serial number:
    cmd_sn = device_target.parse('show inventory')
    serial_number = cmd_sn['module_name']['0/0']['sn']                                  # Might need some adjustments for real devices out of the DevBox

    # Getting device type and model:
    cmd_device_family = cmd_version['device_family']
    mapping = {
        "IOS-XRv": "Router",
        "ASR": "Router",
        "ISR": "Router",
        "Catalyst": "Switch",
        "Nexus": "Datacenter Switch",
        "ASA": "Firewall",
        "FPR": "Firewall",   # Firepower
    }
    device_type = "n/a"
    for prefix, dtype in mapping.items():
        if cmd_device_family.startswith(prefix):
            device_type = dtype
            break

    # Getting connections:
    cmd_show_neighbours = device_target.execute('show cdp') #It shows "that % CDP is not enabled"
    # cmd_show_neighbours = device_target.parse('show cdp neighbors detail')
    # neighbours = cmd_show_neighbours['index']
    # for idx, data in neighbours.items():
    #     print(f"Neighbor {data['device_id']} on {data['local_interface']} "
    #         f"via {data['port_id']}")



    print(cmd_show_neighbours)

    # d1 = device(hostname, ips, serial_number, connected_devices, device_type, cmd_device_family)




    # Step 5: disconnect from the device
    device_target.disconnect()

get_info('iosxr1')