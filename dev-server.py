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
processes.append(Popen(['pelican', '-s', 'publishconf_en.py', '-r']))
processes.append(Popen(['pelican', '-s', 'publishconf_de.py', '-r'], stderr=DEVNULL))
processes.append(Popen(['http-server', 'output', '-c-1', '--gzip']))
processes.append(Popen(['gulp', 'watch']))

live = True
while live:
    sleep(1)
    live = False
    for process in processes:
        if process.poll() is None:
            live = True
