from netmiko import ConnectHandler
from pyats.topology import loader

testbed = loader.load("testbed.yml")

def run_command(host, username, password, command, device_type='cisco_xr', port=22, secret=''):
    """
    Connect to a network device and run a command.

    Args:
        host (str): IP address or hostname of the device
        username (str): SSH username
        password (str): SSH password
        command (str): Command to run on the device
        device_type (str): Netmiko device type (default 'cisco_iosxr')
        port (int): SSH port (default 22)
        secret (str): Enable password if needed (default '')

    Returns:
        str: Output from the command
    """
    device = {
        'device_type': device_type,
        'host': host,
        'username': username,
        'password': password,
        'port': port,
        'secret': secret,
        'verbose': False,
    }

    net_connect = ConnectHandler(**device)
    if secret:
        
        net_connect.enable()

    output = net_connect.send_command(command)
    net_connect.disconnect()
    return output

def find_device_by_ip(testbed, target_ip):
    for device in testbed.devices.values():
        for conn_name, conn in device.connections.items():
            ip = conn.get("ip")
            if str(ip) == target_ip:
                return {
                    "name": device.name,
                    "os": device.os,
                    "credentials": device.credentials,
                    "connection": conn_name
                }
    return None


if __name__ == "__main__":
    testbed = loader.load("testbed.yml")
    result = find_device_by_ip(testbed, "198.18.133.8")

    if result:
        print("Device name:", result["name"])                  # xr-1
        print("OS:", result["os"])                             # iosxr
        print("Credentials:", result["credentials"]["default"])  # {'username': 'cisco', 'password': 'cisco123'}
        print("Connection name:", result["connection"])        # mgmt
    else:
        print("IP not found")

    # output = run_command(
    #     host='198.18.133.8',
    #     username='cisco',
    #     password='cisco123',
    #     command='show mpls oam dpm prefix'
    # )
    # print(output)