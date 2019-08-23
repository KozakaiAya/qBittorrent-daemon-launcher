import subprocess
import pathlib
import os
import contextlib

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

def safe_mkdir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    