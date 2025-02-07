#!/usr/bin/env python3

import sys
import requests
import argparse

def check_website_health(url, warning_threshold, critical_threshold):
    try:
        response = requests.get(url, timeout=10)
        load_time = response.elapsed.total_seconds() * 1000  # convert to milliseconds

        if response.status_code != 200:
            return (2, f"Website is down. Status Code: {response.status_code}")

        if load_time >= critical_threshold:
            return (2, f"CRITICAL - Response time {load_time:.2f} ms exceeds critical threshold of {critical_threshold} ms")
        elif load_time >= warning_threshold:
            return (1, f"WARNING - Response time {load_time:.2f} ms exceeds warning threshold of {warning_threshold} ms")
        else:
            return (0, f"OK - Response time {load_time:.2f} ms")
    except requests.exceptions.RequestException as e:
        return (3, f"Error checking website: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Check website response time")
    parser.add_argument("-H", "--host", required=True, help="Host URL")
    parser.add_argument("-w", "--warning", type=int, required=True, help="Warning threshold in ms")
    parser.add_argument("-c", "--critical", type=int, required=True, help="Critical threshold in ms")
    args = parser.parse_args()

    url = args.host
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    status, message = check_website_health(url, args.warning, args.critical)
    print(message)
    sys.exit(status)

if __name__ == '__main__':
    main()