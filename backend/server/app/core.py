from server import ServerHandler
from app import app
import register


class ATC(object):

    def __init__(self):
        self.server = ServerHandler().build_server(
            server_args={
                'app': app,
                'host': '127.0.0.1',
                'port': 8000,
            }
        )
        register.server = self.server  # injection

    def run(self) -> None:
        import asyncio
        asyncio.run(
            self.server.serve()
        )
        return None

atc = ATC()
atc.run()

