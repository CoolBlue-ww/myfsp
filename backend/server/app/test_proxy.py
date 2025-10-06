from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from mitmproxy import http
class MyProxy:
    def __init__(self):
        pass

    @staticmethod
    def request(flow: http.HTTPFlow) -> None:
        if flow.request.host == 'www.baidu.com':
            flow.request.url = 'https://jd.com/'


class ProxyLauncher(object):
    def __init__(self,
                 listen_host: str = '127.0.0.1',
                 listen_port: int = 8080,
                 ) -> None:
        self.listen_host = listen_host
        self.listen_port = listen_port
        self._options = None
        self._dump_master = None

    @property
    def options(self) -> Options | None:
        return self._options

    @property
    def dump_master(self) -> DumpMaster | None:
        return self._dump_master

    async def launch(self, addons = MyProxy()) -> None:
        self._options = Options(
            listen_host=self.listen_host,
            listen_port=self.listen_port,
        )
        self._dump_master = DumpMaster(self._options)
        self._dump_master.addons.add(addons)
        await self._dump_master.run()
        return None

    def shutdown(self) -> None:
        if isinstance(self._dump_master, DumpMaster):
            self._dump_master.shutdown()
            return None
        else:
            return None

