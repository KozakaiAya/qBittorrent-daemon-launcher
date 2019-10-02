import subprocess
import sys
import threading
import os
import argparse
import time
import pathlib
import contextlib

from utils import X_is_running, get_memory_usage, deleteICEauthority
from logger import Logger

parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=float, default=0.75)
parser.add_argument('--poll_interval', type=int, default=60)
parser.add_argument('--config', type=str, default='')
args = parser.parse_args()

def main():
    logger_obj = Logger()
    # Detect qBittorrent is installed
    have_X = X_is_running()
    QB_BIN = None
    if have_X:
        # Detect QB GUI version first
        proc = subprocess.Popen(['which', 'qbittorrent'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = proc.communicate()
        QB_GUI_BIN = outs.decode(sys.stdout.encoding).rstrip('\n')
        if len(QB_GUI_BIN) > 0:
            QB_BIN = QB_GUI_BIN
            # Need delete the ~/.ICEauthority
            deleteICEauthority()
    if QB_BIN is None:
        # Detect QB-nox
        proc = subprocess.Popen(['which', 'qbittorrent-nox'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = proc.communicate()
        QB_NOX_BIN = outs.decode(sys.stdout.encoding).rstrip('\n')
        if len(QB_NOX_BIN) > 0:
            QB_BIN = QB_NOX_BIN
    if QB_BIN is None:
        # qBittorrent not installed
        print("Cannot find qBittorrent, please install it first.")
        sys.exit(0)
    
    # Get memory in KiB
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_kib = mem_bytes / 1024.0

    # Build qB bin start path
    if args.config == '':
        qb_exec_cmd = [QB_BIN]
    else:
        qb_exec_cmd = [QB_BIN, '--configuration=' + args.config]

    # Start qBittorrent
    qb_proc = subprocess.Popen(qb_exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    qb_pid = qb_proc.pid

    while True:
        ret = qb_proc.poll()
        if ret is None:
            # qBittorrent is still running
            cur_mem_usage = get_memory_usage(qb_pid)['rss']
            if cur_mem_usage > (mem_kib * args.threshold):
                # Memory Leak
                print("Fuck libtorrent: Memory Leak")
                qb_proc.kill()
                outs, err = qb_proc.communicate()
                logger_obj.log(outs)
                print("Current qBittorrent killed, wait 5 seconds before restart...")
                time.sleep(5)
                print("Restarting qBittorrent...")
                qb_proc = subprocess.Popen(qb_exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qb_pid = qb_proc.pid
        elif ret == 0:
            print('qBittorrent normally exited...')
            sys.exit(0)
        else:
            print("Fuck libtorrent: Exit Code =", ret)
            outs, err = qb_proc.communicate()
            logger_obj.log(outs)
            time.sleep(5)
            if have_X:
                deleteICEauthority()
            print("Restarting qBittorrent...")
            qb_proc = subprocess.Popen(qb_exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            qb_pid = qb_proc.pid

        # Wait args.poll_interval seconds before next poll
        time.sleep(args.poll_interval)

if __name__ == "__main__":
    main()
