#!/usr/bin/env python3

import socket
import argparse
import time
import sys

def check_port(host, ports, timeout, content_check=None):
    results = []
    for port in ports:
        start_time = time.time()
        try:
            # Attempt connection
            with socket.create_connection((host, port), timeout=timeout) as s:
                latency = time.time() - start_time
                result = f"OK - Port {port} on {host} is open | latency={latency:.3f}s"
                # Optional: Content Check (HTTP/HTTPS Example)
                if content_check:
                    s.sendall(f"HEAD / HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
                    response = s.recv(1024).decode()
                    if content_check not in response:
                        result = f"WARNING - Port {port} open but content mismatch (missing: {content_check})"
                results.append(result)
        except socket.timeout:
            results.append(f"CRITICAL - Port {port} on {host} timed out | latency={timeout}s")
        except Exception as e:
            results.append(f"CRITICAL - Port {port} on {host} is closed or unreachable: {e}")
    return results

def main():
    parser = argparse.ArgumentParser(description="Enhanced Nagios plugin to check if ports are open")
    parser.add_argument("-H", "--host", required=True, help="Host to check (IP or hostname)")
    parser.add_argument("-P", "--ports", required=True, help="Comma-separated list of port numbers")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Connection timeout in seconds")
    parser.add_argument("-c", "--content-check", help="Optional string to verify in the server response")
    args = parser.parse_args()

    # Parse ports into a list
    ports = [int(p) for p in args.ports.split(",")]

    # Run checks
    results = check_port(args.host, ports, args.timeout, args.content_check)
    for result in results:
        print(result)
    
    # Exit with appropriate code
    if any("CRITICAL" in r for r in results):
        sys.exit(2)
    elif any("WARNING" in r for r in results):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
