# ptt-autoPushBoo
A robot that can help you push or boo continuously under certain posts.

## Features
* You can just put what you want to push in a text file and feed it into the robot.
* The robot detects server latency and adjust its pushing speed.
* The robot can detect board settings and adjust the length of each push.

## Usage
    python3 pttAutoPushBoo.py

You will be prompted to input the followings in the beginning:
* user ID
* password
* board name
* post ID
* name of your input text file 
* to push or to boo

## Issues
Sometimes the sleep time is not long enough so the task fails. Seeking a better way to detemine it.