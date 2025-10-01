import time
import asyncio
from fastapi import FastAPI
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Tuple
from config import Config, ConfigPerser


class MyHandler(FileSystemEventHandler):
    def __init__(self,
                 queue: asyncio.Queue,
                 loop: asyncio.AbstractEventLoop,
                 config_file: str
                 ) -> None:
        self.queue = queue
        self.loop = loop
        self.config_file = config_file
        self.last_event_time = {}

    def on_modified(self, event) -> None:
        if not event.is_directory:
            current_time = time.time() 
            inerval = current_time - self.last_event_time.get(event.src_path, 0)
            if inerval <= 0.1:
                self.last_event_time[event.src_path] = current_time
                return
            if event.src_path == self.config_file:
                asyncio.run_coroutine_threadsafe(
                    coro=self.put_item(event.src_path),
                    loop=self.loop,
                )
        return None

    async def put_item(self, item):
        try:
            self.queue.put_nowait(item)
        except asyncio.QueueFull:
            pass


class Monitor(object):
    def __init__(self,
                 app: FastAPI,
                 monitoring_directory: str,
                 config_file: str,
                 ) -> None:
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(maxsize=256)
        self.app = app
        self.monitoring_directory = monitoring_directory
        self.config_file = config_file
    

    async def queue_get_iter(self):
        while True:
            item = await self.queue.get()
            if item == "__STOP__":
                break
            yield item

    async def file_monitor_task(self,
                                config_handler: Config
                                ) -> None:
        try:
            async for filepath in self.queue_get_iter():
                self.app.state.config = await config_handler.load_config(
                    config_file=self.config_file
                )
        except asyncio.CancelledError:
            raise asyncio.CancelledError()
        finally:
            pass
        return None

    async def start_file_monitoring(self) -> Tuple[Observer, asyncio.Task]:
        config_handler = Config()
        self.app.state.config = await config_handler.load_config(
            config_file=self.config_file,
        )
        self.app.state.config_perser = ConfigPerser()
        
        handler = MyHandler(loop=self.loop, queue=self.queue, config_file=str(config_handler.config_file))
        observer = Observer()
        observer.schedule(handler, self.monitoring_directory, recursive=True)
        observer.start()
        
        monitor_task = asyncio.create_task(self.file_monitor_task(config_handler=config_handler))
        return observer, monitor_task

    async def stop_file_monitoring(self,
                                   observer: Observer,
                                   monitor_task: asyncio.Task
                                   ) -> None:
        try:
            self.queue.put_nowait("__STOP__")
        except asyncio.QueueFull:
            try:
                await self.queue.get()
                self.queue.put_nowait("__STOP__")
            except:
                pass

        try:
            await asyncio.wait_for(monitor_task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass

        if observer.is_alive():
            observer.stop()
            observer.join()
        
        return None

__all__ = [
    'Monitor',
]

    
