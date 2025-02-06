#!/usr/bin/env python3
import argparse
import requests
import sys
import json
import socket
import time
import platform
from datetime import datetime
from subprocess import Popen, PIPE

# Nagios exit codes
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

def check_os():
    current_platform = platform.system().lower()
    if current_platform == 'windows':
        return 'windows'
    elif current_platform == 'linux':
        return 'linux'
    elif current_platform == 'darwin':
        return 'macos'
    else:
        return 'unknown'

def query_zabbix_agent(host_ip, key):
    request_data = b"ZBXD\x01" + len(key).to_bytes(8, byteorder="little") + key.encode()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((host_ip, 10050))
            sock.sendall(request_data)
            response_data = b""

            while True:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response_data += chunk

        if not response_data:
            raise ValueError("No data received from Zabbix agent")

        response = response_data[13:].decode().strip()
        return response

    except (socket.timeout, socket.error, ValueError) as e:
        print(f"CRITICAL: Failed to query '{key}' from agent at {host_ip} - {e}")
        sys.exit(STATE_CRITICAL)

def check_threshold(value, warning_threshold, critical_threshold, metric_name):
    if critical_threshold is not None and value >= critical_threshold:
        print(f"CRITICAL: {metric_name} exceeds critical threshold ({value:.2f} > {critical_threshold}) | {metric_name}={value:.2f}")
        sys.exit(STATE_CRITICAL)
    elif warning_threshold is not None and value >= warning_threshold:
        print(f"WARNING: {metric_name} exceeds warning threshold ({value:.2f} > {warning_threshold}) | {metric_name}={value:.2f}")
        sys.exit(STATE_WARNING)
    else:
        print(f"OK: {metric_name} is within acceptable limits ({value:.2f}) | {metric_name}={value:.2f}")
        sys.exit(STATE_OK)

def get_cpu_usage(host_ip, api_url, warning_threshold, critical_threshold):
    response = query_zabbix_agent(host_ip, "system.cpu.util[,idle]")
    try:
        cpu_idle = float(response)
        cpu_usage = 100.0 - cpu_idle
        check_threshold(cpu_usage, warning_threshold, critical_threshold, "cpu_usage")
    except ValueError:
        print(f"CRITICAL: Invalid CPU response from agent: '{response}'")
        sys.exit(STATE_CRITICAL)

def get_memory_usage(host_ip, api_url, warning_threshold, critical_threshold):
    response = query_zabbix_agent(host_ip, "vm.memory.size[available]")
    try:
        memory_available = int(response) / (1024 ** 2)  # Convert to MB
        check_threshold(memory_available, warning_threshold, critical_threshold, "available_memory")
    except ValueError:
        print(f"CRITICAL: Invalid memory response from agent: '{response}'")
        sys.exit(STATE_CRITICAL)

def run_os_specific_check(host_ip, check_type, api_url, warning_threshold, critical_threshold):
    os_type = check_os()
    if os_type == 'windows':
        print("Windows checks are not implemented.")
        sys.exit(STATE_UNKNOWN)
    elif os_type in ['linux', 'macos']:
        if check_type == 'cpu':
            get_cpu_usage(host_ip, api_url, warning_threshold, critical_threshold)
        elif check_type == 'memory':
            get_memory_usage(host_ip, api_url, warning_threshold, critical_threshold)
        else:
            print(f"CRITICAL: Unsupported check type {check_type} for OS {platform.system()}")
            sys.exit(STATE_UNKNOWN)
    else:
        print(f"CRITICAL: Unsupported OS type {os_type}")
        sys.exit(STATE_UNKNOWN)

def main():
    parser = argparse.ArgumentParser(description="Nagios plugin to monitor Zabbix resources via agent or system checks")
    parser.add_argument("-H", "--host", required=True, help="Host IP to monitor")
    parser.add_argument("--check", choices=["cpu", "memory"], required=True, help="Type of resource to check")
    parser.add_argument("--api-url", required=True, help="Zabbix API URL (e.g., http://192.168.0.233/zabbix/api_jsonrpc.php)")
    parser.add_argument("--warning-threshold", type=float, help="Warning threshold for the monitored resource")
    parser.add_argument("--critical-threshold", type=float, help="Critical threshold for the monitored resource")

    args = parser.parse_args()

    run_os_specific_check(args.host, args.check, args.api_url, args.warning_threshold, args.critical_threshold)

if __name__ == "__main__":
    main()
