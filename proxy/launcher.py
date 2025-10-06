from mitmproxy.addonmanager import AddonManager
from mitmproxy.options import Options as MitmproxyOptions
from mitmproxy.tools.dump import DumpMaster as MitmproxyDumpMaster
from mitmproxy.exceptions import AddonManagerError as MitmproxyAddonManagerError
from mitmproxy import ctx
import asyncio, inspect, warnings
from collections.abc import Iterable
from typing import Any


# 这是默认的ddons
from mitmproxy import http


class MyProxy:
    def __init__(self):
        pass

    @staticmethod
    def request(flow: http.HTTPFlow) -> None:
        if flow.request.host == 'www.baidu.com':
            flow.request.url = 'https://jd.com/'

class YouProxy:
    def __init__(self):
        pass

    @staticmethod
    def request(flow: http.HTTPFlow) -> None:
        if flow.request.host == 'www.baidu.com':
            flow.request.url = 'https://jd.com/'

class Options(MitmproxyOptions):
    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 8080,
                 ) -> None:
        super().__init__(
            listen_host=host,
            listen_port=port,
        )

class Master(MitmproxyDumpMaster):
    def __init__(self,
                 options: Options,
                 loop: asyncio.AbstractEventLoop | None = None,
                 ) -> None:
        super().__init__(
            options=options,
            loop=loop,
            with_termlog=False,
            with_dumper=False,
        )

class AddonsChecker(object):
    def __init__(self, addons) -> None:
        self.addons = addons

    @staticmethod
    def _is_object(arg: Any) -> bool:
        attr = [a for a in dir(arg) if not a.startswith('_')]
        if len(attr) > 0:
            return True
        else:
            return False

    def checked(self) -> list:
        checked_addons = []
        if isinstance(self.addons, Iterable):
            for addon in self.addons:
                if self._is_object(addon):
                    checked_addons.append(addon)
                else:
                    warnings.warn(f'Addon "{addon}" is not an object.')
        else:
            if self._is_object(self.addons):
                checked_addons.append(self.addons)
            else:
                warnings.warn(f'Addon "{self.addons}" is not an object.')
        return checked_addons


class ProxyLauncher(object):
    useless_tasks = {
        'ClientPlayback.playback',
        'ProxyLauncher.launch',
        'Event.wait',
        'ConnectionHandler.wakeup',
        'ConnectionHandler.open_connection'
    }
    useful_tasks = {
        'RequestResponseCycle.run_asgi',
        'Server.serve',
        'LifespanOn.main',
        'ServerInstance.handle_stream',
        'TimeoutWatchdog.watch',
        'ConnectionHandler.handle_connection',
    }

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 8080,
                 ) -> None:
        self.host = host
        self.port = port
        self._options = None
        self._master = None
        self._proxy_task = None
        self._running = False
        self._default_addons = []
        self._customize_addons = []

    @property
    def options(self) -> Options | None:
        return self._options

    @property
    def master(self) -> Master | None:
        return self._master

    @property
    def addon_manager(self) -> AddonManager | None:
        if self.master:
            return self.master.addons
        else:
            return None

    @property
    def addons(self) -> list:
        if self.master:
            return self.master.addons.chain
        else:
            return []

    @property
    def lookup(self) -> dict:
        if self.master:
            return self.master.addons.lookup
        else:
            return {}

    @property
    def proxy_task(self) -> asyncio.Task | None:
        return self._proxy_task

    @property
    def running(self) -> bool:
        return self._running

    async def launch(self, addons = YouProxy()) -> None:
        if not self.proxy_task or self.proxy_task.done():
            if not self._default_addons:
                self._options = Options(
                    host=self.host,
                    port=self.port,
                )
                self._master = Master(
                    options=self._options,
                    loop=None,
                )
                self._default_addons = self._master.addons.chain.copy()
                checked_addons = AddonsChecker(addons).checked()
                self._customize_addons = checked_addons.copy()
                self._master.addons.add(*checked_addons)
                self._proxy_task = asyncio.create_task(self._master.run())
            else:
                again_addons = self._default_addons + self._customize_addons
                self._master.addons.add(*again_addons)
                self._proxy_task = asyncio.create_task(self._master.run())
            self._running = True
        else:
            if not self.running:
                self._running = True
        return None

    @staticmethod
    async def _cleanup_residue_tasks(loop: asyncio.AbstractEventLoop = None) -> bool:
        while True:
            tasks = asyncio.all_tasks(loop=loop)
            master_tasks = []
            print(master_tasks)
            for task in tasks:
                if not task.done() and str(task.get_coro().__qualname__) in ProxyLauncher.useless_tasks:
                    master_tasks.append(task)
                else:
                    continue
            if len(master_tasks) == 0:
                break
            for master_task in master_tasks:
                master_task.cancel()
                try:
                    await master_task
                except asyncio.CancelledError:
                    return False
            await asyncio.sleep(0.25)
        return True


    async def _cleanup_addons(self) -> bool:
        for addon in self.addons[::-1]:
            try:
                if hasattr(addon, 'done') and inspect.iscoroutinefunction(addon.done):
                    lookup_name = addon.__class__.__name__.lower()
                    if lookup_name in self.master.addons.lookup.keys():
                        del self.lookup[lookup_name]
                        self.addons.remove(addon)
                else:
                    self.master.addons.remove(addon=addon)
            except MitmproxyAddonManagerError as e:
                print(f"清理插件异常：{e}")
        if len(self.addons) == 0:
            return True
        else:
            return False

    async def land(self) -> None:
        if self.master:
            if self.proxy_task and not self.proxy_task.done() and not self.proxy_task.cancelled():
                self.master.shutdown()
                try:
                    await asyncio.wait_for(self.proxy_task, timeout=1)
                    if self._proxy_task.done():
                        self._proxy_task = None
                except (asyncio.CancelledError,
                        asyncio.TimeoutError):
                    pass
            cleanup_addons = await self._cleanup_addons()
            if cleanup_addons:
                cleanup_residue_tasks = await self._cleanup_residue_tasks()
                if cleanup_residue_tasks:
                    self._running = False
            else:
                pass


__all__ = [
    'ProxyLauncher',
]
