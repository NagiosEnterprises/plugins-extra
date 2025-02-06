#!/usr/bin/env python3
import sys
import requests
import time
import argparse

'''
This website is to monitor the usage of websites
This is done by measuring the response time
Louie Mattia Jan 2025
'''

parser = argparse.ArgumentParser()

# Add the website name when calling
parser.add_argument( '-H',
                    '--host',
                    required=True,
                    type=str,
                    help='The website that will be checked')

args = parser.parse_args()

# Assign website name as variable fo use
website = args.host

# Set timeout timer (allow the program to give up)
TIMEOUT = 10 # Seconds

# Threshold times for Warning and Critical
### Try to add for editable values in XI later, get this working first
WARN_START = 2
CRIT_START = 5

# Output parameters, defaults for Nagios
# DONT CHANGE, IT WILL NOT WORK OTHERWISE
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

def check_response():
    # Test to make sure my code is grabbing what I want it to, delete later when shown it does
    print(website)
    # Make sure it can grab the time properly
    try:
        start = time.time()
        response = requests.get(website, timeout=TIMEOUT)
        # How long did it take to respond
        response_time = time.time() - start

        # Status code 200 means its reachable
        if response.status_code == 200:
            # At this point, check if the repsonse time is critial
            if response_time >= CRIT_START:
                print(f"Response time {response_time:.2f}s exceeds {CRIT_START}s, this site is busy")
                return CRITICAL
            # If not, is it at the warning?
            elif response_time >= WARN_START:
                print(f"Response time {response_time:.2f}s exceeds {WARN_START}s, this site is getting active")
                return WARNING
            # Looks like its fine if it makes it here
            else:
                print(f"This website is calm for now, response time is {response_time:.2f}")
                return OK
        # If different status code, something is up
        else:
            code = response.status_code
            print(f"Status code returned {code:.2f}")
            return CRITICAL
    except requests.exceptions.RequestException as e:
        print("Website cannot be reached")
        return CRITICAL

if __name__ == "__main__":
        exit = check_response()
        sys.exit(exit)

