"""
    Run the scrapy web crawler.

    Look at how to make the multiprocessing faster:
    - https://www.cloudcity.io/blog/2019/02/27/things-i-wish-they-told-me-about-multiprocessing-in-python/
"""
import asyncio
import random
import string
import time
from multiprocessing import Process

from screaper.core.main import Main
from screaper_resources.resources.db import Database


class AsyncProcessWrapper:

    def __init__(self):
        self.name = 'PROC:' + ''.join(random.choice(string.ascii_uppercase) for _ in range(4))

    def run_main_loop(self):

        # You are stupid. You replaced the engine-pool creation in the main thread,
        # not the child process (because the __init__ was called in the parent, not by the Process.).
        # Don't repeat this stupid mistake again lol

        self.resource_database = Database()  # TODO Make database async!
        # time.sleep(10.)
        self.resource_database.engine.dispose()
        self.main = Main(name=self.name, database=self.resource_database)

        asyncio.run(self.main.run_main_loop())

class Runner:
    """
        Threaded Wrapper around the engine
    """

    def __init__(self):
        self.max_time = 12 * 3600 # 3600  # 60
        self.number_processes = 7  # 6  # 32  # 32  # Number of processes to spawn. Each process will have a different proxy for a long while
        self.ping_interval = 120  # 120  # Ping threads every 2 minutes to make sure that the threads are not dead yet

    def run(self):

        # Now do this in a for-loop
        # Create one engine to populate the database
        print("Create one engine to populate the database")

        # Now do this in a for-loop
        processes = dict()

        try:

            while True:

                # Spawn additional processes if there are not enough processes
                for i in range(self.number_processes - len(processes)):
                    p = Process(target=AsyncProcessWrapper().run_main_loop)
                    time.sleep(0.3)
                    p.start()
                    start_time = time.time()
                    # a bit disgusting, but that's fine
                    name = str(p.name) + str(p._identity)
                    print("Spawning process nr: {} name: {} len: {}".format(i, name, len(processes)))
                    processes[name] = {
                        "process": p,
                        "time": start_time
                    }

                print("MAIN : Sleep until next Ping...")
                time.sleep(self.ping_interval)

                # Kill any process that has been alive for too long
                tokill = set()

                for name, proc_obj in processes.items():
                    proc = proc_obj["process"]
                    proc_time = proc_obj["time"]

                    # Try to join with a timeout
                    # proc.join(timeout=0)
                    if (time.time() - proc_time) > self.max_time:
                        print("Time is: ", (time.time() - proc_time), self.max_time, (time.time() - proc_time) > self.max_time)
                        print("Process {} will now be terminated".format(name))
                        tokill.add(name)
                    elif proc.is_alive():
                        print("Job is not finished!")
                    else:
                        print("Process {} is dead.".format(name))
                        tokill.add(name)

                for proc_name in tokill:
                    processes[proc_name]['process'].terminate()
                    del processes[proc_name]

        finally:
            for name, proc_obj in processes.items():
                proc_obj['process'].terminate()

engine = Runner()

if __name__ == "__main__":
    print("Starting the engine ...")
    # engine = Engine()
    # engine.run()

    runner = Runner()
    runner.run()
