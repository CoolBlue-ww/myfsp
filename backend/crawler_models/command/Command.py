import subprocess, shutil, getpass, pexpect, inspect
import platform, random, re, os, sys, shlex
from pathlib import Path
from typing import List, Mapping, Optional, Union, Tuple, Set, Sequence, Any, Dict
import tempfile
from locale import getlocale


class Command(object):
    __slots__ = (
        '_terminal',
        '_terminal_args',
        '_shell',
        '_shell_args',
        '_command',
        '_args',
        '_args',
        '_username',
        '_system',
        '_language',
        '_encoding',
    )
    def __init__(self,
                 terminal: bool = False,  # Is open terminal
                 terminal_args: Optional[List[str]] = None,  # Is terminal arguments
                 shell: bool = False,  # Using shell
                 shell_args: Optional[List[str]] = None,  # Is shell arguments
                 command: Optional[Union[str, List[str]]] = None,  # command
                 args: Optional[Dict[str, Any]] = None,  # subprocess args
                 ) -> None:
        self._terminal = terminal  # init terminal
        self._terminal_args = ['--wait'] if not terminal_args \
            else terminal_args # init terminal arguments
        self._shell = shell # init shell
        self._shell_args = ['-c'] if not shell_args \
            else shell_args  # init shell arguments
        self._command = command  # init command
        self._args = args  # init args
        self._username = getpass.getuser()  # init user
        self._system = platform.system().lower()  # Darwin -> macOS
        if self._system == 'darwin':  # darwin -> macos
            self._system = 'macos'
        self._language, self._encoding = getlocale()  # language and encoding

# =======================================================================
    # Get Shells (Windows, Linux, macOS)
    def _get_shells(self) -> Optional[Dict[str, Any]]:
        """
        {
            "sh", "dash", "rbash", "bash", "zsh", "fish", "ksh", "mksh", "csh", "tcsh", "rc"  # Linux Shells
        }
        :return:
        """
        if self._system == 'windows':
            windows_shells = {'cmd', 'powershell'}
            shells = {}
            for windows_shell in windows_shells:
                shell_path = shutil.which(windows_shell)
                if shell_path:
                    shells[windows_shell] = shell_path
            return shells

        if self._system == 'linux':
            def _write_shells(
                    _shell: str,
                    _current_login_shell_name: str,
                    _shells: Dict[str, Union[List[str], bool]]
            ) -> None:
                shell_name = Path(_shell).name
                login_shell = True if _current_login_shell_name == shell_name else False
                if shell_name not in _shells.keys():
                    shells[shell_name] = {
                        'current_login_shell': login_shell,
                        'shell_path': [_shell],
                    }
                else:
                    shells[shell_name]['shell_path'].append(_shell)
                return None

            shells = {}  # Key -> Shell Name Value -> Is login Shell and Shell Path
            current_login_shell_name = Path(os.environ.get('SHELL', 'unknown')).name
            shells_file = Path('/etc/shells')
            if shells_file.exists() and shells_file.is_file() and shells_file.stat().st_size > 0:
                try:
                    with shells_file.open(mode='rt', encoding='utf-8') as ssf:
                        shells_strings = ssf.read()
                        shell_lines = shells_strings.splitlines()
                        for shell in shell_lines:
                            if shell.startswith('#'):
                                continue
                            else:
                                _write_shells(shell, current_login_shell_name, shells)
                    return shells
                except Exception as e:
                    print(f'Error: {e}')
                    return None

            else:  # Not exists shells file
                common_shells = {
                    "sh", "dash", "rbash", "bash", "zsh", "fish", "ksh", "mksh", "csh", "tcsh", "rc"  # Linux Shells
                }
                current_login_shell_name = Path(os.environ.get('SHELL', 'unknown')).name
                for shell in common_shells:
                    which_shell = shutil.which(shell)
                    if which_shell:
                        _write_shells(
                            _shell=which_shell,
                            _current_login_shell_name=current_login_shell_name,
                            _shells=shells)
                    else:
                        continue
                return shells

        if self._system == 'macos':
            return None

        return None

# =======================================================================
    # Get Available terminals （Windows， Linux， maxOS）
    def _get_terminals(self) -> Optional[Dict[str, str]]:
        if self._system == 'windows':  # Windows
            pass

        if self._system == 'linux':  # Linux
            terminals = {}
            for term in ("gnome-terminal",  # possible linux terminal
                         "konsole",
                         "xfce4-terminal",
                         "mate-terminal",
                         "lxterminal",
                         "xterm"
                         ):  # Terminal Name
                terminal_path = shutil.which(term)
                if terminal_path:
                    terminals[term] = terminal_path # Find available terminals Break loop
                else:  # run pexpect
                    continue
            return terminals  #  Find available terminals

        if self._system == 'macos':
            pass

# ============================================================
    # Split sub commands (Windows, Linux, macOS)
    def _split_command(self) -> Optional[List[str]]:
        """
        Parse the command (Windows, Linux, macOS)
        :return:
        """
        if self._system == 'windows':
            pass

        if self._system == 'linux':
            if isinstance(self._command, str):
                self._command = shlex.split(self._command)  # shlex split command
                return self._command
            if not isinstance(self._command, List):
                return self._command  # It's already a list

        if self._system == 'macos':
            pass
        return None

# ===================================================================
    # join command aegs (Windows, Linux, macOS)
    def _join_command(self) -> Optional[str]:
        if isinstance(self._command, str):
            return self._command
        if isinstance(self._command, List):
            return ' '.join(self._command)
        return None

    def _parse_args(self) -> Dict[str, Any]:
        """
        parsed args
        :return:
        """
        keys = self._args.keys()
        if 'shell' in keys and self._args['shell'] == True:
            if self._terminal:  # Terminal / Shell
                self._args['shell'] = False

        if 'capture_output' in keys and self._args['capture_output'] == True:
            for std in {'stdin', 'stdout', 'stderr'}:  # Useless parameters
                if std in keys:
                    del self._args[std]  # Delete

        if 'shell' in keys and self._args['shell'] == True:
            if self._shell:
                self._args['shell'] = False
        return self._args

# =========================================================
    # Temp File
    @staticmethod
    def _create_temp_files() -> Tuple[Path, Dict[str, str]]:
        """
        Save Terminal output to a temporary file
        :return:
        """
        temp_dir = Path().home().joinpath(
            '.atc',
            'temp',
        )  # temp dir
        if not temp_dir.exists():
            temp_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
        temp_file = {}
        with tempfile.NamedTemporaryFile(  # output temp file
            mode='w',
            encoding='utf-8',
            dir=temp_dir,
            delete=False,
            delete_on_close=False) as stdout:
            temp_file['stdout'] = stdout.name
        with tempfile.NamedTemporaryFile(  # output temp file
            mode='w',
            encoding='utf-8',
            dir=temp_dir,
            delete=False,
            delete_on_close=False) as stderr:
            temp_file['stderr'] = stderr.name
        with tempfile.NamedTemporaryFile(  # exist code temp file
            mode='w',
            encoding='utf-8',
            dir=temp_dir,
            delete=False,
            delete_on_close=False
        ) as exist_code:
            temp_file['exist_code'] = exist_code.name
        return temp_dir, temp_file

    @staticmethod
    def _delete_temp_files(temp_dir: Path, temp_files: Dict[str, str]) -> None:
        for file in temp_files.values():
            file_path = Path(file)
            file_path.unlink(
                missing_ok = True
            )
        shutil.rmtree(  # remove temp dir
            temp_dir,
        )
        return None

    def _pipeline(self,
            temp_files: Dict[str, str],
            mode: str = 'text',
            encoding: Optional[str] = None,
    ) -> Dict[str, Any]:  # [text, bytes]
        read_mode, read_encoding = '', ''
        if mode == 'text':
           read_mode = 'rt'
        if mode == 'bytes':
            read_mode = 'rb'
        if read_mode == 'rt':
            if encoding:
                read_encoding = encoding
            else:
                read_encoding = self._encoding or 'utf-8'
        if read_mode == 'rb':
            if encoding:
                read_encoding = None
        return_value = {}
        with (
            Path(temp_files['stdout']).open(mode=read_mode, encoding=read_encoding) as stdout,
            Path(temp_files['stderr']).open(mode=read_mode, encoding=read_encoding) as stderr,
            Path(temp_files['exist_code']).open(mode=read_mode, encoding=read_encoding) as exist_code,
        ):
            stdout = stdout.read()
            stderr = stderr.read()
            exist_code = exist_code.read()
            return_value['stdin'] = f'{self._join_command()}'
            return_value['stdout'] = stdout
            return_value['stderr'] = stderr
            return_value['exist_code'] = exist_code
        return return_value

# =========================================================
    # Windows
    def _run_ordinary_windows_command(self):
        pass

    def _run_terminal_windows_command(self):
        pass

# =========================================================
    # Linux
    def _run_ordinary_linux_command(self) -> Dict[str, Any]:
        args = self._parse_args()
        complete_command = []  # init complete command
        if not self._shell:
            if 'shell' in args and self._args['shell'] == True:
                complete_command = self._join_command()
            else:
                complete_command = self._split_command()
        else:
            shells = self._get_shells()
            shell = ''
            if 'bash' in shells.keys():
                shell = 'bash'
            else:
                for shell_name, shell_info in shells.items():
                    if shell_info['current_login_shell']:
                        shell = shell_name
                    else:
                        continue
            complete_command = [
                shell, *self._shell_args, self._join_command()
            ]
        result = subprocess.run(
            complete_command,
            **args,
        )
        return_value = {
            'stdin': self._join_command(),
            'stdout': result.stdout,
            'stderr': result.stderr,
            'exist_code': result.returncode,
        }
        return return_value

    def _run_terminal_linux_command(self) -> Optional[Dict[str, Any]]:
        """
        open os terminal run command
        :return:
        """
        args= self._parse_args()
        shell, terminal = '', ''
        shells, terminals = self._get_shells(), self._get_terminals()
        if 'bash' in shells.keys():
            shell = 'bash'
        else:
            for shell_name, shell_info in shells.items():
                if shell_info['current_login_shell']:
                    shell = shell_name
                else:
                    continue
        if len(terminals) > 0:
            terminal = list(terminals.keys())[0]
        complete_command = []
        if self._shell:
            open_terminal_command = [
                terminal, *self._terminal_args, '--', shell, *self._shell_args,
            ]
            temp_dir, temp_files = self._create_temp_files()  # create temp files
            output_redirect_command = f" >'{temp_files['stdout']}' 2>'{temp_files['stderr']}' ; echo $? >'{temp_files["exist_code"]}'"
            complete_command = open_terminal_command + [
                self._join_command() + output_redirect_command,
            ]
            subprocess.run(
                complete_command,
                **args,
            )
            return_value = self._pipeline(
                temp_files=temp_files,
                mode='text',
                encoding='utf-8',
            )
            self._delete_temp_files(
                temp_dir=temp_dir,
                temp_files=temp_files,
            )
            return return_value
        else:
            message = 'Need to open shell parameters'
            raise NotImplementedError(message)

# ==================================================
    # macOS
    def _run_ordinary_macos_command(self):
        pass

    def _run_terminal_macos_command(self):
        pass

# ===================================================
    # Run core api
    def run(self) -> Optional[Dict[str, Any]]:
        """
        Exposed core interfaces
        :return:
        """
        if self._system == 'windows':
            pass
        if self._system == 'linux':
            if not self._terminal:
                return self._run_ordinary_linux_command()
            else:
                return self._run_terminal_linux_command()
        if self._system == 'macos':
            pass


__all__ = [
    "Command"
]
