import os, sys
from mitmproxy.tools import main
from typing import Mapping, Any, Union, Sequence, Tuple, Optional, Dict

print(sys.executable)

class ProxyService(object):
    __slots__ = (
        '_mode',
        '_return_info',
    )

    def __init__(self) -> None:
        self._mode = {'mitmproxy', 'mitmdump', 'mitmweb'}
        self._return_info = None

    def get_message(self) -> Dict[str, Union[int, str]]:
        return self._return_info

    def _getattr(self,
                 mode: str = 'mitmproxy',
                 args: Optional[Dict[str, Any]] = None,
                 ) -> None:
        try:
            stdout = getattr(main, mode)(args)
            return_info = {
                'mode': mode,
                'stdout': stdout,
                'stderr': '',
                'returncode': 0,
            }
            self._return_info = return_info
        except Exception as e:
            return_info = {
                'mode': mode,
                'stdout': '',
                'stderr': e,
                'returncode': 1,
            }
            self._return_info = return_info
            return None
        return None

    def run(self,
            mode: str = 'mitmproxy',
            args: Optional[Sequence[str]] = None,
    ) -> None:
        if mode in self._mode:
            if mode in {'mitmdump', 'mitmweb'}:
                return self._getattr(mode=mode, args=args)
            else:
                if all([sys.stdin.isatty(),
                        sys.stdout.isatty(),
                        sys.stderr.isatty()
                    ]):
                    return self._getattr(mode=mode, args=args)
                else:
                    return_info = {
                        'mode': mode,
                        'stdout': '',
                        'stderr': "Error: mitmproxy's console interface requires a tty. Please run mitmproxy in an interactive shell environment.",
                        'returncode': 1,
                    }
                    self._return_info = return_info
                    return None
        else:
            raise RuntimeError(f"Unknown mode {mode}")

proxy_service = ProxyService()
proxy_service.run(
    mode='mitmweb',
    args=[
    '-s', 'proxy.py',
    '-p', '8080',
    '--set', 'block_global=false',
    ],
)

# print(proxy_service.get_message())

