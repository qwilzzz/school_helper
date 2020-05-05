#!/bin/sh
[[ $(pgrep -a python | grep 'main.py') ]] && kill $(pgrep -f 'python main.py'); python main.py
