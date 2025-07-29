#!/usr/bin/env python3
from pyats.topology import loader
import json
import re

def is_valid_ipv4(ip: str) -> bool:
    """
    Check if the given string is a valid IPv4 address.

    Args:
        ip (str): The IP address to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    ip_pattern = re.compile(
        r'^('
        r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}'
        r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$'
    )
    return bool(ip_pattern.match(ip))

def find_device_by_ip(testbed, target_ip):
    for device in testbed.devices.values():
        for conn_name, conn in device.connections.items():
            ip = conn.get("ip")
            if str(ip) == target_ip:
                return device.name
    return None

def collect_raw_outputs(testbed_file, router, commands):
    testbed = loader.load(testbed_file)
    """
    Connects to a device and returns raw output of given show commands.

    Args:
        commands (list): List of show commands to run

    Returns:
        string: Command -> Raw output or error message
    """
    if is_valid_ipv4(router):
        if find_device_by_ip(testbed, router):
            router = find_device_by_ip(testbed, router)
        else:
            print(f"IP address {router} is a valid IP, but not in the testbed")
            router = None

    if router is not None:
        device = testbed.devices[router]
        device.connect(log_stdout=False)

        raw_outputs = {}
        for cmd in commands:
            try:
                raw_outputs[cmd] = device.execute(cmd)
            except Exception as e:
                raw_outputs[cmd] = f"Error parsing '{cmd}': {e}"

        return raw_outputs

def collect_parsed_outputs(testbed_file, router, commands):
    """
    Connects to a device and returns parsed output of given show commands.

    Args:
        commands (list): List of show commands to run

    Returns:
        dict: Command -> Parsed output or error message
    """
    testbed = loader.load(testbed_file)
    if is_valid_ipv4(router):
        if find_device_by_ip(testbed, router):
            router = find_device_by_ip(testbed, router)
        else:
            print(f"IP address {router} is a valid IP, but not in the testbed")
            router = None

    if router is not None:
        device = testbed.devices[router]
        device.connect(log_stdout=False)

        parsed_outputs = {}
        for cmd in commands:
            try:
                parsed_outputs[cmd] = device.parse(cmd)
            except Exception as e:
                parsed_outputs[cmd] = f"Error parsing '{cmd}': {e}"

        return parsed_outputs

if __name__ == "__main__":
    testbed_file = "testbed.yml"
    router = "xr-5"
    commands = ["show version"]

    results = collect_raw_outputs(testbed_file, router, commands)

    for cmd, output in results.items():
        print(f"\n--- Parsed output for: {cmd} ---")
        print(json.dumps(output, indent=2))
        print(output)
