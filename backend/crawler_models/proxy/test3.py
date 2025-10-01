from pathlib import Path
from command.Terminal import Terminal

# Ubuntu/Debian
            #     1> mv mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
            #     2> sudo update-ca-certificates

source_path = Path('/home/ckr-ubuntu/桌面/mitmproxy-ca-cert-None.pem')
target_dir = Path('/usr/local/share/ca-certificates')
# if not target_dir.exists():
#     target_dir.mkdir(
#         parents=True,
#         exist_ok=True
#     )
target_file = target_dir / 'mitmproxy.crt'
terminal = Terminal()
terminal.pop_terminal(
        [
            'sudo',  'mv',  str(source_path), str(target_file),
        ]
)
terminal.pop_terminal(
        [
            'sudo',  'update-ca-certificates',
        ]
)
