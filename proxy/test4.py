import subprocess

sudo_1 = [
    'sudo', 'apt', 'update'
]
sudo_2 = [
    'sudo', 'mkdir', '/usr/local/share/ca-certificates'
]
sudo_3 = [
    'sudo', 'echo', 'Hello, World!'
]

sudo_4 = [
    'mkdir', '/home/ckr-ubuntu/桌面/ttpy'
]

sudo_5 = [
    'google-chrome', '--version'
]

cmd = [
    'gnome-terminal', '--wait', '--'
] + sudo_1

# result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
# print(result.stdout)
# print(result.stderr)
# print(result.returncode)

a = [1, 3, 4]
if a.filter_args:
    print()

