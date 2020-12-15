#!/usr/bin/env bash
# Runs multiple instances of the python program to collect data
import subprocess
import time

n_processes = 2

cmd = ['python', '-m', 'screaper.engine.run']
procs_list = [
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for _ in range(n_processes)
]

break_flag = dict((i, False) for i in range(n_processes))
c = 0
while True:
    c += 1
    print("iter", c)

    for idx, proc in enumerate(procs_list):

        try:
            print("Unbuffered lines for {} are: ".format(proc.pid))

            for line in proc.stdout:
                print(line.replace('\n', ''))

            print("Iterated through lines")
            poll = proc.poll()
            if poll is not None:
                print("Polling is: ", poll)
                break_flag[idx] = True
            # if stdout:
            #     print(stdout.strip())
            # if stderr:
            #     print(stdout.strip())
        finally:
            proc.terminate()

    if all(break_flag.values()):
        print("Breaking", break_flag)
        break
    else:
        time.sleep(int(1))


# Poll all of the processes
