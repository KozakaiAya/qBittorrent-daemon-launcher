# qBittorrent-daemon-launcher
A simple python3 script to restart qBittorrent when libtorrent f*cked up, including segmentation fault and memory leak.

This script launches qBittorrent as a python `subprocess` and polls its status every `args.poll_interval` seconds. During each poll, the script checks whether qBittorrent has been terminalted abnormally (SIGSEGV, etc.) or has encountered a memory leak (used more than `args.threshold` of the system physical memory). If qBittorrent has entered the states above, it will be killed and relaunched.

If X server exists in the execution environment, the GUI version of qBittorrent will be launched by default. If the GUI version does not exist, it will automatically fallback to the CLI version (qbittorrent-nox).

This script is a perfect complement to the unstable and ill-written [libtorrent](https://github.com/arvidn/libtorrent) and [qBittorrent](https://github.com/qbittorrent/qBittorrent) code.

## Usage
1. Prepare a Linux machine

2. Install qBittorrent on that machine

3. Put `launch.py` to whatever the place you like

4. If you would like to run qBittorrent under Xfce or silimar desktop environment, modify and copy the `.desktop` file provided in this repo and place it in your autostart directory (something like `~/.config/autostart`).

5. If you would like to run qBittorrent under a headless environment, simply write a systemd service and run the script inside.