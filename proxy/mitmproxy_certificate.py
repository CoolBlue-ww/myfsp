import locale
import shutil

import requests
import subprocess
import platform
from pathlib import Path
from typing import Optional, Union, List, Mapping, Tuple, Dict, Any
from atc_html.HTML import HTMLParse
from command.Command import Command


# Debian 系 (apt/apt-get/snap/deb 家族)
Debian = {
    'ubuntu', 'kubuntu', 'xubuntu', 'lubuntu', 'ubuntu gnome', 'ubuntu mate',
    'ubuntu studio', 'ubuntu kylin', 'edubuntu', 'linux mint', 'elementary os',
    'zorin os', 'pop!_os', 'deepin', 'kali linux', 'parrot os', 'tails',
    'raspberry pi os', 'mx linux', 'antix', 'devuan', 'ubuntu server',
    'proxmox ve', 'turnkey linux', 'vyos', 'steamos', 'endless os', 'pureos'
}

# Red Hat 系（rpm/yum/dnf 家族）
RedHat = {
    'rhel', 'centos', 'centos stream', 'fedora', 'almalinux', 'rocky linux',
    'oracle linux', 'amazon linux', 'clearos', 'scientific linux', 'eurolinux',
    'springdale', 'miracle linux', 'berry linux'
}

# Arch 系（pacman 家族）
Arch = {
    'arch linux', 'archbang', 'archex', 'archman', 'arch linux 32',
    'arch linux arm', 'archstrike', 'arcolinux', 'artix linux',
    'blackarch linux', 'bluestar linux', 'cachyos', 'chimeraos',
    'ctlos linux', 'crystal linux', 'endeavouros', 'garuda linux',
    'hyperbola', 'instantos', 'kaos', 'manjaro linux', 'msys2',
    'obarun', 'parabola', 'parchlinux', 'rebornos', 'snal linux',
    'steamos 3', 'systemrescue', 'tearch linux', 'ubos'
}


class MitmproxyCertificate(object):
    def __init__(self):
        self._platform = platform.system().lower()
        self._language, self._encoding = locale.getlocale()  # Get language and encoding
        self._url = 'http://mitm.it/'
        self._proxy = {
            'http': '127.0.0.1:8080',
            'https': '127.0.0.1:8080',
        }
        self._headers = {
            "accept": "text/atc_html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            # "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "host": "mitm.it",
            # "proxy-connection": "keep-alive",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
        self._div_xpath = "//ul[contains(@class, 'list-unstyled')]/li[contains(@class, 'media')]/div[contains(@class, 'media-body')]"
        self._platform_xpath = "./h5[contains(@class, 'mt-0')]/text()"
        self._href_xpath = "./a[contains(@class, 'btn-success')]/@href"
        self._suffix_xpath = "./a[contains(@class, 'btn-success')]/text()"

    def get_links(self) -> Dict[Any, Any]:
        """
        Get mitmproxy certificate install links.
        Add self._resources
        :return:
        """
        response = requests.get(
            url=self._url,
            headers=self._headers,
            proxies=self._proxy,
            verify=False,
            allow_redirects=True,
            timeout=10,
        )
        response.raise_for_status()
        html_text = response.text
        div_elements = HTMLParse(html_text=html_text).xpath(self._div_xpath)
        resources = {}
        for div_element in div_elements:
            platforms = [
                platform.lower() \
                for platform in div_element.xpath(self._platform_xpath)
            ]
            urls = [
                self._url + href \
                for href in div_element.xpath(self._href_xpath)
            ]
            suffixes = [
                '.' + suffix.rsplit('.', 1)[-1] \
                for suffix in div_element.xpath(self._suffix_xpath)
            ]
            resources[
                tuple(platforms) if len(platforms) > 1 else platforms[0] if len(platforms) == 1 else ''
            ] = [
                urls if len(urls) > 1 else urls[0] if len(urls) == 1 else '',
                suffixes if len(suffixes) > 1 else suffixes[0] if len(suffixes) == 1 else '',
            ]
        return resources

    @ staticmethod
    def _strip_colon(text: str) -> str:
        if text.startswith('"') and text.endswith('"') or \
                text.startswith("'") and text.endswith("'"):
            if len(text) > 0:
                outer_layer = text[0]
                current_char = text[0]
                indexes = []
                for i, v in enumerate(text[1:]):
                    if current_char == outer_layer and v != current_char or \
                        current_char != v and v == outer_layer:
                        indexes.append(i + 1)
                    current_char = v
                start, end = indexes[0], indexes[-1]
                return text[start:end]
            else:
                return ''
        else:
            return text

    def _add_os_release(self,
            kv_pairs: List[str],
    ) -> Dict[str, str]:
        os_release = {}
        for kv_pair in kv_pairs:
            key, value = kv_pair.split(sep='=', maxsplit=1)
            pretty_key = self._strip_colon(key)
            pretty_value = self._strip_colon(value)
            os_release[pretty_key] = pretty_value
        return os_release

    def _read_os_release_file(self,
                              os_release_file: Path = Path('/etc/os-release')
                              ) -> Dict[str, str]:
        with os_release_file.open(mode='rt', encoding=self._encoding) as orn:
            os_release_info = orn.read()  # Read os-release file
            kv_pairs = os_release_info.splitlines()
            os_release = self._add_os_release(
                kv_pairs=kv_pairs,
            )
            return os_release

    def _cat_os_release_file(self,
                             os_release_file: Path = Path('/etc/os-release')) -> Dict[str, str]:
        command = ['cat', os_release_file]  # Using cat look os-release file
        result = subprocess.run(
            args=command,
            text=True,
            capture_output=True,
            check=True,
        )
        kv_pairs = result.stdout.splitlines()
        os_release = self._add_os_release(
            kv_pairs=kv_pairs,
        )
        return os_release

    def get_os_release(self) -> Dict[str, str]:
        """
        Get linux release name
        :return: Mapping[str, str]
        """
        try:
            return self._read_os_release_file()
        except FileNotFoundError:
            return self._cat_os_release_file()

# =======================================================================
    # Install certificate
    def _download_certificate(self,
                              target_url,
                              cert_file,
                              ) -> None:
        response = requests.get(
            url=target_url,
            headers=self._headers,
            proxies=self._proxy,
            verify=False,
            allow_redirects=True,
            timeout=10,
        )
        response.raise_for_status()
        text = response.text
        with cert_file.open(mode='wt', encoding='utf-8') as file:
            file.write(text)  # Download pem file
        return None

# =========================================================================
    # Windows install
    @staticmethod
    def windows_install(cert_file: Path) -> Tuple[str, str, int]:
        """
        # ["powershell", '-NoProfile', '-ExecutionPolicy', 'Bypass', "-Command", ps_command],
         # ["powershell", "-NoProfile", '-ExecutionPolicy', 'Bypass', "-Command", f'& "{exe_path}"']
        :param cert_file:
        :return:
        """
        script_name = Path(__file__).parent.joinpath('windows_certificate')
        powershell_script = script_name.with_suffix('.ps1')
        cmd_script = script_name.with_suffix('.cmd')
        powershell_command = [
            'powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(powershell_script),
            '-Path', str(cert_file),
        ]
        cmd_command = [
            str(cmd_script),
            str(cert_file),
        ]

        def _run_terminal_script(command: List[str]) -> Tuple[str, str, int]:
            """
            Run PowerShell Script on Windows or Cmd Script on Windows.
            :param command:
            :return: Tuple[str, str, int]:
            """
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr
            status = result.returncode
            return stdout, stderr, status

        try:
            return _run_terminal_script(command=powershell_command)
        except subprocess.CalledProcessError:
            return _run_terminal_script(command=cmd_command)

# ========================================================================
    # Linux install
    @staticmethod
    def _debian_family_install(cert_file) -> Dict[str, str]:
        ca_certificates_dir = Path('/usr/local/share/ca-certificates')
        mitmproxy_crt_file = ca_certificates_dir.joinpath('mitmproxy').with_suffix('.crt')
        mkdir_command = [
            'sudo', 'mkdir', str(ca_certificates_dir)
        ]
        cp_command = [
            'sudo', 'cp', str(cert_file), str(mitmproxy_crt_file),
        ]
        update_command = [  # os update
            'sudo', 'update-ca-certificates'
        ]
        last_command = mkdir_command + ['&&'] + cp_command + ['&&'] + update_command
        if ca_certificates_dir.exists():
            last_command = cp_command + ['&&'] + update_command
        return_value = Command(
            shell=True,
            terminal=True,
            command=last_command,
            args={},
        ).run()
        return return_value

    @staticmethod
    def _red_hat_family_install(cert_file) -> Dict[str, str]:
        ca_certificates_dir = Path('/etc/pki/ca-trust/source/anchors/')
        mkdir_command = [
            'sudo', 'mkdir', str(ca_certificates_dir)
        ]
        cp_command = [
            'sudo', 'cp', str(cert_file), str(ca_certificates_dir),
        ]
        update_command = [  # os update
            'sudo', 'update-ca-trust'
        ]
        last_command = mkdir_command + ['&&'] + cp_command + ['&&'] + update_command
        if ca_certificates_dir.exists():
            last_command = cp_command + ['&&'] + update_command
        return_value = Command(
            shell=True,
            terminal=True,
            command=last_command,
            args={},
        ).run()
        return return_value

    @staticmethod
    def _arch_linux_install(cert_file) -> Dict[str, str]:
        main_command = [
            'sudo', 'trust', 'anchor', '--store', str(cert_file),
        ]
        return_value = Command(
            shell=True,
            terminal=True,
            command=main_command,
            args={},
        ).run()
        return return_value

    def linux_install(self,
                       cert_file: Path
                       ) -> Optional[Dict[str, str]]:
        """
        Debian, Red Hat, Arch family
        :param cert_file:
        :return:
        """
        os_release = self.get_os_release()
        linux_name = os_release.get('NAME', '').lower()
        if linux_name in Debian:
            return self._debian_family_install(cert_file=cert_file)
        elif linux_name in RedHat:
            return self._red_hat_family_install(cert_file=cert_file)
        elif linux_name in Arch:
            return self._arch_linux_install(cert_file=cert_file)
        else:  # scalable
            return None

# =========================================================================
    # macOS install
    @staticmethod
    def macos_install():
        pass

# =========================================================================
    # Core installation logic
    def install(self,
                save_dir: Optional[Union[str, Path]] = None,
                platform: Optional[str] = None,
                ) -> Optional[Dict[str, str]]:
        save_dir = save_dir if isinstance(save_dir, Path) else \
            Path(save_dir) if isinstance(save_dir, str) else save_dir
        if not save_dir.exists():
            save_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
        resources = self.get_links()  # Get certificate download links
        if not platform and self._platform == 'darwin':
            self._platform = 'macos'
        elif platform and platform.lower() not in resources.keys():
            self._platform = 'other platforms'
        else:
            pass
        target_url, suffix = resources.get(self._platform, '')
        if isinstance(target_url, List) and isinstance(suffix, List):
            choice = input(f"Please choose a certificate format [{' / '.join(["'" + i_suffix + "'" \
            for i_suffix in suffix])}] | (default='{suffix[0]}'): ")
            if choice in suffix:
                for i_target_url, i_suffix in zip(target_url, suffix):
                    if choice == i_suffix:
                        target_url = i_target_url
                        suffix = i_suffix
                        break  # Break loop
            elif not choice:
                target_url = target_url[0]
                suffix = suffix[0]
            else:
                raise ValueError(f'Error: Invalid choice: {choice}  (In the install function)')
        cert_file = save_dir.joinpath(f'mitmproxy-ca-cert-{self._platform}').with_suffix(suffix)  # Creat save path
        if cert_file.exists() and cert_file.stat().st_size > 0:  # cert file already exists pass
            pass
        else:  # Download cert file
            self._download_certificate(
                target_url=target_url,
                cert_file=cert_file,
            )  # Download certificate

        if self._platform == 'windows':
            return None
        elif self._platform == 'macos':
            return None
        elif self._platform == 'linux':
            return self.linux_install(cert_file=cert_file)
        else:  # scalable
            return None

    @staticmethod
    def install_certutil(linux_name: str) -> Optional[Dict[str, str]]:
        """
        Install linux import cert tool
        :return:
        """
        certutil_path = shutil.which('certutil')
        if not certutil_path:  # Not exists certutil tool
            install_command = []
            if linux_name in Debian:
                install_command = [
                    'sudo', 'apt', 'update', '&&',
                    'sudo',  'apt', 'install', 'libnss3-tools'
                ]
            if linux_name in RedHat:
                install_command = [
                    'sudo', 'dnf', 'update', '&&',
                    'sudo', 'dnf', 'install', 'nss-tools'
                ]
            if linux_name in Arch:
                install_command = [
                    'sudo', 'pacman', '-S', 'nss'
                ]
            return_value = Command(
                shell=True,
                terminal=True,
                command=install_command,
                args={},
            ).run()
            return return_value
        return None

    @staticmethod
    def import_cert(cert_file: Path) -> Optional[Dict[str, str]]:
        """
        :param cert_file:
        :return:
        """
        chromium_db = Path().home().joinpath(
            '.pki',
            'nssdb',
        )
        if not chromium_db.exists():
            chromium_db.mkdir(
                parents=True,
                exist_ok=True,
            )
        init_command = [
            'certutil',
            '-N',
            '-d', f'sql:{chromium_db}',
            '--empty-password',
        ]

        import_command = [
            'certutil',
            '-d', 'sql:/home/ckr-ubuntu/.pki/nssdb',
            '-A',
            '-t', 'C,',
            '-n', 'mitmproxy',
            '-i', '/home/ckr-ubuntu/桌面/mitmproxy-ca-cert-linux.pem'
        ]

        check_command = [
            'certutil',
            '-L',
            '-d', f'sql:{chromium_db}',
            '-n', 'mitmproxy',
        ]
        return_value = Command(
            shell=True,
            terminal=True,
            command=init_command,
        )


__all__ = [
    'MitmproxyCertificate',
]

m = MitmproxyCertificate()
m.install_certutil(linux_name='ubuntu')


# print(ca)
# print(m.get_os_release()['NAME'].lower())


# Ubuntu/Debian
#     1> mv mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
#     2> sudo update-ca-certificates
# Fedora
#     1> mv mitmproxy-ca-cert.pem /etc/pki/ca-trust/source/anchors/
#     2> sudo update-ca-trust
# Arch Linux
#     1> sudo trust anchor --store mitmproxy-ca-cert.pem