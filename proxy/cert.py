import platform as pf
import httpx, aiopath


class MitmproxyCertificate(object):
    __slots__ = ('url', 'proxy', 'cert_links')

    def __init__(self):
        self.url = "http://mitm.it/"
        self.proxy = "http://127.0.0.1:8080"
        self.cert_links = {
            "windows": "http://mitm.it/cert/p12",
            "linux": "http://mitm.it/cert/pem",
            "ios": "http://mitm.it/cert/pem",
            "macos": "http://mitm.it/cert/pem",
            "android": "http://mitm.it/cert/cer",
            "firefox": "http://mitm.it/cert/pem",
            "other-platforms": {
                "p12": "http://mitm.it/cert/p12",
                "pem": "http://mitm.it/cert/pem",
            }
        }

    async def install_cert(self,
                                   platform: str | None = None,
                                   other_platform_format: str | None = None,
                                   save_dir: str | None = None) -> str:
        cert_platform = platform or pf.system()
        if cert_platform and cert_platform.lower() not in self.cert_links.keys():
            raise ValueError(
                f'Platform "{platform}" is not supported. The platform must be "windows", "linux", "ios", "macos", "android", "firefox" or "other-platforms".'
            )
        if cert_platform == 'Darwin':
            cert_platform = 'macOS'
        cert_save_dir = aiopath.AsyncPath(save_dir)
        if not await cert_save_dir.is_dir():
            cert_save_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
        cert_url = self.cert_links[cert_platform.lower()]
        if isinstance(cert_url, dict):
            if not other_platform_format or other_platform_format not in {'pem', 'p12'}:
                cert_url = cert_url["pem"]
            else:
                cert_url = cert_url[other_platform_format]
        cert_file = cert_save_dir.joinpath(
            f'mitmproxy-ca-cert-{cert_platform.lower()}.{cert_url.rsplit(
                sep="/", maxsplit=1)[-1]}'
        )
        async with httpx.AsyncClient(
            proxy=self.proxy,
            verify=False,
            timeout=10,
        ) as client:
            response = await client.get(url=cert_url)
            response.raise_for_status()
            text = response.text
            async with cert_file.open(mode='wt', encoding='utf-8') as file:
                await file.write(text)  # Download pem file
        return str(cert_file)

__all__ = [
    'MitmproxyCertificate',
]
