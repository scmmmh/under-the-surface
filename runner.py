#!/usr/bin/env python3
import signal
import sys

from time import sleep
from subprocess import run, Popen, DEVNULL


def notification_handler(a, b):
    print('\nShutting down\n')

signal.signal(signal.SIGINT, notification_handler)

run(['rm', '-rf', 'output'])
processes = []
if len(sys.argv) > 1 and sys.argv[1] == '-d':
    processes.append(Popen(['pelican', '-s', 'publishconf_en.py', '-r'], stderr=DEVNULL))
    processes.append(Popen(['pelican', '-s', 'publishconf_de.py', '-r'], stderr=DEVNULL))
    processes.append(Popen(['http-server', 'output']))
    processes.append(Popen(['gulp', 'watch']))
else:
    processes.append(Popen(['pelican', '-s', 'publishconf_en.py']))
    processes.append(Popen(['pelican', '-s', 'publishconf_de.py']))

live = True
while live:
    sleep(1)
    live = False
    for process in processes:
        if process.poll() is None:
            live = True
