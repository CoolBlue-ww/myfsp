from fastapi import APIRouter
from playwright.async_api import async_playwright
import asyncio
import sys, subprocess, logging, typing


class PlaywrightDependency(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def playwright_dependency(
              command: str = 'playwright',
              option: str = 'install',
              operand: str | list[str] = 'chromium',
    ) -> dict[str, str | int]:
        if isinstance(operand, str):
            operand = [operand]
        elif isinstance(operand, list):
            pass
        else:
            operand = []
        cmd = [sys.executable, '-m', command, option] + operand
        try:
            print("正在执行playwright install...")  # wait
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            output = {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
            }
            return output
        except subprocess.CalledProcessError as e:
            output = {
                'stdout': '',
                'stderr': e,
                'returncode': -1,
            }
            return output

class PlaywrightOptions(object):
    def __init__(self,
                 launch_options: typing.Optional[typing.Dict[str, typing.Any]] = None,
                 context_options: typing.Optional[typing.Dict[str, typing.Dict[str, typing.Any]]] = None,
                 ) -> None:
        self._launch_options = launch_options
        self._context_options = context_options

    @property
    def launch_options(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._launch_options

    @launch_options.setter
    def launch_options(self, value: typing.Optional[typing.Dict[str, typing.Any]]) -> None:
        self._launch_options = value

    @property
    def context_options(self) -> typing.Optional[typing.Dict[str, typing.Dict[str, typing.Any]]]:
        return self._context_options

    @context_options.setter
    def context_options(self, value: typing.Optional[typing.Dict[str, typing.Dict[str, typing.Any]]]):
        self._context_options = value

class PlaywrightPool(object):
    def __init__(self,
                 browser_type: str = 'chromium',
                 playwright_options: typing.Optional[PlaywrightOptions] = None,
                 context_pool_size: int = 1,
                 page_pool_size: typing.Optional[typing.List[int]] = None,
                 ) -> None:
        """
        {
            context_1: {
                        page: ...
                        }
            ...
        }
        :param browser_type:
        :param playwright_options:
        :param context_pool_size:
        :param page_pool_size:
        """
        self.browser_type = browser_type
        self.playwright_options = playwright_options
        self.context_pool_size = context_pool_size if context_pool_size >= 1 else 1
        self.context_ids = [f"context_{context_id}" for context_id in range(context_pool_size)]
        if context_pool_size != len(page_pool_size):
            page_pool_size = page_pool_size[0:context_pool_size:1]
        self.page_pool_size = page_pool_size if isinstance(page_pool_size, list) else [1]
        self.page_ids = [[f"context_{context_id}_page_{page}" for page in range(pages)] for context_id, pages in enumerate(page_pool_size)]
        self._playwright_pool = {
            'browser': None,
            'contexts': {},
            'pages': {}
        }

    @property
    def playwright_pool(self):
        return self._playwright_pool

    async def create_playwright_pool(self) -> dict[typing.Any, typing.Any]:
        """
        context_pool_size = 5
            context_ids = ['A', 'B', 'C', 'D', 'E'] \n
            page_pool_size = [1, 2, 4, 6, 3] \n
            page_ids = [
                ['A'], ['A', 'B'] ...
            ]
        :param :
        :return:
        """
        launch_options = self.playwright_options.launch_options
        context_options = self.playwright_options.context_options
        if self.browser_type in {'chrome', 'chromium'}:
            async_playwright_api = await async_playwright().start()
            browser = await async_playwright_api.chromium.launch(
                **launch_options,
            )
            self._playwright_pool['browser'] = browser
            for context_id in self.context_ids:
                context = await browser.new_context(
                    **context_options.get(context_id, {})
                )
                self._playwright_pool['contexts'][context_id] = context
                for i_page_ids in self.page_ids:
                    for page_id in i_page_ids:
                        page = await context.new_page()
                        self._playwright_pool['pages'][page_id] = page
        return self._playwright_pool

    def get_browser(self) -> typing.Any:
        return self._playwright_pool['browser']

    def get_contexts(self) -> dict[typing.Any, typing.Any]:
        return self._playwright_pool['contexts']

    def get_pages(self) -> dict[typing.Any, typing.Any]:
        return self._playwright_pool['pages']

    def get_pages_in_context(self, context_id: str):
        if context_id in

import time
a = time.time()
pp = PlaywrightPool(context_pool_size=5,
                    page_pool_size=[1, 2, 4, 6, 3, 10, 45, 5, 9, 17],
                    playwright_options=PlaywrightOptions({}, {})
)
# r = asyncio.run(pp.get_playwright_pool())
print(pp.playwright_pool)
# print(r)
# print(pp.playwright_pool)
b = time.time()
print((b-a)*1000)


class Playwright(object):

    def __init__(self) -> None:
        pass

    async def automation(self):
        async with async_playwright() as ap:
            browser = await ap.firefox.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto('https://www.baidu.com')
            html = await page.content()
            print(html)
            await asyncio.sleep(10)
            contexts = {}
            for i in range(10):
                contexts[i] = await browser.new_context()
            print(contexts)




# automation_router = APIRouter(
#     prefix='/automation',
#     tags=['automation']
# )



# # @automation_router.post('/')
# # async def assutomation():
# #     pass


# asyncio.run(_automation())
