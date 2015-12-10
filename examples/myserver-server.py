#!/bin/env python

import os
import psutil
import socket
import ssl

from SocketServer import ThreadingMixIn

from jrpc import SimpleTCPServer
from jrpc import SimpleTCPRequestHandler

from jrpc.functions import execute
from jrpc.functions import parseProcesses
from jrpc.functions import parseNetstat
from jrpc.functions import parseIfcfg
from jrpc.functions import parseIO
from jrpc.Logger import Logger
from jrpc.utils import deamonize

__author__ = 'umairghani'

LOG = Logger("/var/log/myserver", "myserver").get_logger()

class MyServerRequestHandler(SimpleTCPRequestHandler):
    """
    Override Logging
    """
    def log_request(self, code="-", size="-"):
        message = "%s - %s %s %s" % \
                  (self.client_address[0],
                   self.requestline, str(code), str(size))
        if code == 200:
            LOG.info(message)
        else:
            LOG.error(message)

    def log_error(self, format, *args):
        message = "%s - %s" % \
                  (self.client_address[0],
                  format%args)
        LOG.error(message)


class MyServer(ThreadingMixIn,SimpleTCPServer):
    def __init__(self, bindaddr):
        SimpleTCPServer.__init__(self, bindaddr,
                                 MyServerRequestHandler)
        self.register_function(ping)
        self.register_function(mount)
        self.register_function(iostat)
        self.register_function(uptime)
        self.register_function(get_env)
        self.register_function(netstat)
        self.register_function(cpuinfo)
        self.register_function(meminfo)
        self.register_function(ifconfig)
        self.register_function(disk_usage)
        self.register_function(check_process)
        self.register_function(running_process)



def ping():
    """
    :return: response to ping
    """
    return "pong"


def uptime():
    """
    :return uptime of the system
    :return {"output": output, "error": error}
    """
    LOG.info("Checking uptime")
    output = ""
    try:
        output, error = execute("uptime")
    except Exception, e:
        LOG.exception(e)
        error = str(e)
    return {"output": output, "error": error}


def mount():
    """
    :return mount information of the system
    :return {"output": <array>, "error": error}
    """
    LOG.info("Getting mount")
    output = []
    try:
        mounts = psutil.disk_partitions()
        for mount in mounts:
            output.append({
                "device": mount.device,
                "mountpoint": mount.mountpoint,
                "fstype": mount.fstype,
                "opts": mount.opts
            })
        return {"output": output, "error": ""}
    except Exception, e:
        LOG.exception(e)
        return {"output": output, "error": str(e)}


def iostat():
    """
    :return iostat information of the system
    :return {"output": <array>, "error": error}
    """
    LOG.info("Getting iostat")
    try:
        iostat = psutil.disk_io_counters(perdisk=True)
        output = parseIO(iostat)
        return {"output": output, "error": ""}
    except Exception, e:
        LOG.exception(e)
        return {"output": [], "error": str(e)}


def ifconfig():
    """
    :return ifconfig information of the system
    :return {"output": <array>, "error": error}
    """
    LOG.info("Getting ifconfig info")
    try:
        ifcfg = psutil.network_io_counters(pernic=True)
        output = parseIfcfg(ifcfg)
        return {"output": output, "error": ""}
    except Exception, e:
        LOG.exception(e)
        return {"output": [], "error": str(e)}


def cpuinfo():
    """
    :return cpu information of the system
    :return {"output": <dict>, "error": error}
    """
    LOG.info("Getting cpu info")
    try:
        percent_per_cpu = psutil.cpu_percent(percpu=True)
        avg_cpu_percent = psutil.cpu_percent()
        no_of_cpu = psutil.NUM_CPUS
        cpu_time = psutil.cpu_times()
        output = {
            "no_of_cpu": no_of_cpu,
            "cpu_percent": avg_cpu_percent,
            "percent_per_cpu": percent_per_cpu,
            "cputimes": {
                "user": cpu_time.user,
                "nice": cpu_time.nice,
                "system": cpu_time.system,
                "idle": cpu_time.idle,
                "iowait": cpu_time.iowait,
                "irq": cpu_time.irq,
                "softirq": cpu_time.softirq
            }
        }
        return {"output": output, "error": ""}
    except Exception, e:
        LOG.exception(e)
        return {"output": {}, "error": str(e)}


def meminfo():
    """
    :return memory information of the system
    :return {"output": <dict>, "error": error}
    """
    LOG.info("Getting memory info")
    try:
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        output = {
            "memory": {
                "total": ram.total,
                "available": ram.available,
                "percent": ram.percent,
                "used": ram.used,
                "free": ram.free,
                "active": ram.active,
                "inactive": ram.inactive,
                "buffers": ram.buffers,
                "cached": ram.cached
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent,
                "sin": swap.sin,
                "sout": swap.sout
            }
        }    
        return {"output": output, "error": ""}
    except Exception, e:
        LOG.exception(e)
        return {"output": {}, "error": str(e)}


def disk_usage():
    """
    :return disk usage of the system
    :return {"output": <array>, "error": error}
    """
    LOG.info("Getting disk usage of the system")
    output = []
    try:
        disks = psutil.disk_partitions()
        for disk in disks:
            mountpoint = disk.mountpoint
            usage = psutil.disk_usage(mountpoint)
            output.append({
                mountpoint: {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                },
            })
        return {"output": output, "error": ""}
    except Exception ,e:
        LOG.exception(e)
        return {"output": output, "error": str(e)}


def netstat():
    """
    :return netstat output of the system
    :return {"output": <array>, "error": error}
    """
    LOG.info("Getting netstat/ss output")
    ## TO DO 
    #cmd = "netstat -antp"
    try:
        cmd = "ss -t -u -a"
        out, err = execute(cmd)
        if out:
            stats = out.strip().split("\n")
            output = parseNetstat(stats) 
            return {"output": output, "error": err}
        else:
            LOG.error("[%s] command failed" %cmd)
            return {"output":[], "error": err}
    except Exception, e:
        return {"output": [], "error": str(e)}
  

def running_process():
    """
    Get all the process running on the system
    :return: array of process
    :return {"output": <array>, "error": error}
    """
    LOG.info("Getting all the process running")
    try:
        cmd = "ps -eo args"
        output, error = execute(cmd)
        plist = output.strip().split("\n")
        return {"output": plist, "error": error}
    except Exception, e:
        return {"output": [], "error": str(e)}


def check_process(process):
    """
    :param process
    :return usage of the process on the system
    :return {"output": <array>, "error": error}
    """
    LOG.info("Getting [%s] process information from ps" % process)
    try:
        cmd = "ps -eo user,pid,pcpu,pmem,lstart,args | grep -i %s | grep -v grep" % \
              process
        out, err = execute(cmd)
        if out:
            plist = out.strip().split("\n")
            output = parseProcesses(plist)
            return {"output": output, "error": err}
        else:
            LOG.error("[%s] process not found" %process)
            return {"output":[], "error": err}
    except Exception, e:
        LOG.exception(e)
        return {"output": [], "error": str(e)}


def get_env():
    """
    Return the systems environment variable
    :return dict of env variables
    :return {"output": <dict>, "error": error}
    """
    LOG.info("Getting environment variables")
    return {"output": str(os.environ), "error": ""}


def main():
    """
    Main
    """
    deamonize("myserver-server")
    HOST, PORT = "localhost", 9999
    LOG.info("** Starting myserver server on https://%s:%d **" % (HOST, PORT))
    server = MyServer((HOST, PORT))
    # For SSL - uncomment the following line
    #server.socket = ssl.wrap_socket(server.socket, keyfile='<path_to_keyfile>', certfile='<path_to_cert>', server_side=True)
    server.serve_forever()


if __name__ == "__main__":
    main()