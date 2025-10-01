# def _run_linux_terminal(self, command: Union[str, List[str]]) -> None:
    #     def _run_linux_terminal_command(_index, _command) -> None:
    #         result = subprocess.run(
    #             [term, "--wait", "--"] + _command,
    #             shell=False,  # term / shell
    #             check=True,
    #             capture_output=True,
    #             text=True,
    #         )
    #         core_info[f'command_{_index + 1}'] = {
    #             'command': shlex.join(_command),
    #             'stdout': result.stdout,
    #             'stderr': result.stderr,
    #             'returncode': result.returncode,
    #         }
    #         return None
    #
    #     def _terminal_message(_command) -> None:
    #         if 'sudo' in _command:
    #             copy_base_command = _command.copy()
    #             sudo_index = _command.index('sudo')
    #             start_insert_message_index = sudo_index + 1
    #             _command.insert(start_insert_message_index, '-p')
    #             _command.insert(start_insert_message_index + 1,
    #                              f'[sudo] Enter the password for {self._username} | (command: "{shlex.join(copy_base_command)}") :')
    #         else:
    #             pass
    #         return None
    #
    #     for term in ("gnome-terminal", "konsole", "xfce4-terminal",
    #                  "mate-terminal", "lxterminal", "xterm"):
    #         if shutil.which(term):
    #             if isinstance(command, str):
    #                 command = shlex.split(command)
    #             if isinstance(command, List):
    #                 pass
    #             if '&&' in command:
    #                 and_index = command.index('&&')
    #                 command = [
    #                     command[0:and_index],
    #                     command[and_index + 1::]
    #                 ]
    #             print(command)
    #
    #             if isinstance(command[random.randint(0, len(command) - 1)], List):
    #                 for i, _command in enumerate(command):
    #                     _terminal_message(_command)
    #             else:
    #                 _terminal_message(command)
    #             core_info = {}
    #
    #             if isinstance(command[random.randint(0, len(command) - 1)], List):
    #                 print('List')
    #                 for _index, _command in enumerate(command):
    #                     _run_linux_terminal_command(_index, _command)
    #                 return core_info
    #             else:
    #                 _run_linux_terminal_command(1, command)
    #                 return core_info
    #         else:
    #             return None

# ================================================================================
    # run api
# ================================================================================

    # def run(self, command: Union[str, List[str]]) -> Optional[Mapping]:
    #     """
    #     Open pop Terminal
    #     :param command:
    #     :return: None
    #     """
    #
    #     if self._system == "linux":
    #         pass
    #     elif self._system == "macos":  # macOS
    #         # AppleScript 最稳
    #         apple_script = f'''
    #         tell application "Terminal"
    #             do script "{shlex.join(command)}"
    #             activate
    #         end tell
    #         '''
    #         subprocess.run(["osascript", "-e", apple_script])
    #         return None
    #     elif self._system == "Windows":
    #         # Windows Terminal / cmd / powershell
    #         for term in ("powershell", "cmd"):
    #             if shutil.which(term):
    #                 if term == "powershell":
    #                     subprocess.run([term, "-wait", "--", "bash", "-c"] + command)
    #                     return None
    #                 if term == "cmd":
    #                     subprocess.run([term, "-wait", "--", "bash", "-c"] + command)
    #                     return None
    #     else:
    #         # 实在找不到，就提示用户手动操作
    #         print("未检测到可用终端，请手动在系统终端里执行：")
    #         print(" ".join(shlex.quote(c) for c in command))
    #         return None
    #     return None


"""
A ; B	分号	顺序执行：无论A成功与否，都执行B	cd /tmp; ls
A && B	逻辑与	成功才执行：A成功后，才执行B	mkdir dir && cd dir
A || B	逻辑或	失败才执行：A失败后，才执行B	cmd || echo "Failed"
A | B	管道	管道传输：将A的标准输出传给B的标准输入	ps aux | grep nginx
--------------------------------------------------------------------
符号	名称	功能描述	示例
`	反引号	命令替换：执行命令并用其输出替换掉整个部分。	echo "Hello `whoami`"
$(...)	命令替换(现代)	反引号的现代写法，功能相同，更推荐使用。	echo "Hello $(whoami)"
'...'	单引号	强引用：引号内所有字符都失去特殊含义，原样输出。	echo '$HOME && ls'
"..."	双引号	弱引用：引号内大部分字符原样输出，但会解析$变量和$(命令)。	echo "My home is $HOME"
&	后台运行符	让命令在后台运行，而不是“连接”两个命令。	python script.py &
"""
# separator = {
#     ';', '&&', '||', '|', '&'  # Currently supported symbols
# }
# if isinstance(self._command, str):  # str -> list[str]
#     self._command = shlex.split(self._command)
# if 'sudo' in self._command:  # Enter user password
#     self._terminal = True
# parsed_command, char, current_index = [], [], 0
# for index ,part_command in enumerate(self._command):
#     if part_command in separator:
#         parsed_command.append(self._command[current_index:index:1])
#         char.append(self._command[index])
#         current_index = index + 1
# rest = self._command[current_index::]
# if len(rest) > 0:  # [] X add
#     parsed_command.append(rest)
# return parsed_command, char