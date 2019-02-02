import subprocess
import sys
import threading
import os
import argparse
import time
import pathlib
import contextlib

parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=float, default=0.75)
parser.add_argument('--poll_interval', type=int, default=60)
args = parser.parse_args()

def X_is_running():
    p = subprocess.Popen(["xset", "-q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    return p.returncode == 0

def get_memory_usage(pid):
    """Memory usage of the current process in kilobytes."""
    status = None
    result = {'rss': 0}
    try:
        status = open('/proc/' + str(pid) + '/status')
        for line in status:
            parts = line.split()
            key = parts[0][2:-1].lower()
            if key in result:
                result[key] = int(parts[1])
    finally:
        if status is not None:
            status.close()
    return result

# Avoid 'ICE default IO error handler doing an exit()' error
def deleteICEauthority():
    home_dir = str(pathlib.Path.home())
    ICE_path = os.path.join(home_dir, '.ICEauthority')
    with contextlib.suppress(FileNotFoundError):
        os.remove(ICE_path)

def main():
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

    # Start qBittorrent
    qb_proc = subprocess.Popen([QB_BIN], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
                print("Current qBittorrent killed, wait 5 seconds before restart...")
                time.sleep(5)
                print("Restarting qBittorrent...")
                qb_proc = subprocess.Popen([QB_BIN], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qb_pid = qb_proc.pid
        elif ret == 0:
            print('qBittorrent normally exited...')
            sys.exit(0)
        else:
            print("Fuck libtorrent: Exit Code =", ret)
            time.sleep(5)
            if have_X:
                deleteICEauthority()
            print("Restarting qBittorrent...")
            qb_proc = subprocess.Popen([QB_BIN], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            qb_pid = qb_proc.pid

        # Wait args.poll_interval seconds before next poll
        time.sleep(args.poll_interval)

if __name__ == "__main__":
    main()
