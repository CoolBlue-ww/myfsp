import pexpect, getpass, shlex
from typing import Union, List

def backup_terminal(self, command: Union[str, List[str]]) -> None:
    """
    Linux or macOS -> pexpect
    :param command:
    :return:
    """
    if self._system in {'linux', 'macos'}:
        child = pexpect.spawn(command=command if isinstance(command, str) else shlex.join(command),
                              timeout=None,
                              encoding=None
                              )
        for attempt in range(1):
            idx = child.expect([
                "SUDO_PASSWD_PROMPT:",
                pexpect.EOF
            ], timeout=15)
            if idx == 0:  # 又要密码
                pwd = getpass.getpass("sudo 密码：")
                child.sendline(pwd)
            else:
                break  # apt 跑完了
        child.close()
        print("\n" + "exit status:", child.exitstatus)
    return None