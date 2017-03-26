# ptt-autoPushBoo
A robot that can help you push or boo continuously under a certain post.
* Inspired by [this repo](https://github.com/twtrubiks/PttAutoLoginPost).

## Features
* You can just put what you want to push in a text file and feed it into the robot.
* The robot detects server latency and adjust its pushing speed.
* The robot can detect board settings and adjust the length of each push.

## Usage
    python pttAutoPushBoo.py

You will be prompted to input the followings in the beginning:
* user ID
* password
* board name
* post ID
* name of your input text file 
* to push or to boo

## Environment
* Linux 4.10.1-1-ARCH
* Python 3.6.0

## Issues
Sometimes the sleep time is not long enough so the task fails. Seeking a better way to detemine it.