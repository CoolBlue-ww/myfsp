import lxml, io, asyncio
from aiopath import AsyncPath
from lxml.etree import _ElementTree
from lxml.html import HtmlElement

HtmlElementTree = lxml.etree._ElementTree
HtmlElement = HtmlElement
HtmlTree = HtmlElementTree | HtmlElement

class HTML(object):
    __slots__ = (
        '_element',
    )

    def __init__(self, element: HtmlTree = None) -> None:
        """
        LOad and parse HTML.
        :param :
        :param :
        """
        self._element = element

    @property
    def tree(self) -> HtmlElementTree | HtmlElement | list[HtmlElement] | None:
        return self._element

    @staticmethod
    async def _fragment_parser(
            source,
            complete_level,
            parent_container,
    ):
        if complete_level == 'fragments':
            _element = await asyncio.to_thread(
                lxml.html.fragments_fromstring,
                source,
            )
            element = []
            for i_element in _element:
                if isinstance(i_element, HtmlElement):
                    element.append(i_element)
                else:
                    continue
            return element
        elif complete_level == 'fragment':
            if parent_container:
                element = await asyncio.to_thread(
                    lxml.html.fragment_fromstring,
                    source,
                    parent_container,
                )
                return element
            else:
                element = await asyncio.to_thread(
                    lxml.html.fromstring,
                    source,
                )
                return element
        else:
            raise NotImplementedError(
                'fragment level must be "fragment" or "fragments"'
            )

    @staticmethod
    async def _string_source_parser(
            source,
            complete_level,
            parent_container,
    ):
        if complete_level == 'element_tree':  # document
            memory_file = io.StringIO(source)
            element = await asyncio.to_thread(
                lxml.html.parse,
                memory_file,
            )
            return element
        elif complete_level == 'element':
            element = await asyncio.to_thread(
                lxml.html.document_fromstring,
                source,
            )
            return element
        elif complete_level in {'fragment', 'fragments'}:
            element = await HTML._fragment_parser(
                source=source,
                complete_level=complete_level,
                parent_container=parent_container,
            )
            return element
        else:
            raise RuntimeError(
                'complete_level must be "element_tree, "element", "fragment"'
            )

    @staticmethod
    async def _file_source_parser(
            source,
            encoding,
            complete_level,
            parent_container,
    ):
        if await AsyncPath(source).exists():
            if complete_level == 'element_tree':
                element = await asyncio.to_thread(
                    lxml.html.parse,
                    source,
                )
                return element
            elif complete_level == 'element':
                _element = await asyncio.to_thread(
                    lxml.html.parse,
                    source,
                )
                element = _element.getroot()
                return element
            elif complete_level in {'fragment', 'fragments'}:
                async with AsyncPath(source).open(mode='rt', encoding=encoding) as f:
                    _source = await f.read()
                    element = await HTML._fragment_parser(
                        source=_source,
                        complete_level=complete_level,
                        parent_container=parent_container,
                    )
                    return element
            else:
                raise RuntimeError(
                    'complete_level must be "element_tree, "element", "fragment"'
                )
        else:
            raise FileNotFoundError()

    @classmethod
    async def build_tree(cls,
                     source: str = '<html></html>',  # source
                     source_type: str = '',  # str or file
                     encoding: str = 'utf-8',
                     complete_level: str = 'element_tree',  # element_tree or element or fragment
                     parent_container: str = '',  # parent container name
                     ) -> 'HTML':
        """
        创建BaseHTML类的实例
        :param encoding:
        :param source:
        :param source_type:
        :param complete_level:
        :param parent_container:
        :return:
        """
        # 判断string的来源类型（string和file）
        _source_type = 'string'  # 初始化默认类型为str
        if source_type in {'string', 'file'}:
            _source_type = source_type
        else:
            if '<' in source or '>' in source:
                pass
            else:
                _source_type = 'file'
        # 初始化element为None
        element = None
        if _source_type == 'string':  # source str
            element = await cls._string_source_parser(
                source=source,
                complete_level=complete_level,
                parent_container=parent_container,
            )
        if _source_type == 'file':
            element = await cls._file_source_parser(
                source=source,
                encoding=encoding,
                complete_level=complete_level,
                parent_container=parent_container,
            )
        return cls(element=element)

    def xpath(self, xpath: str | None = None) -> list:
        if isinstance(self._element, HtmlElement | _ElementTree):
            query_result = self._element.xpath(xpath)
            return query_result
        else:
            return []

    def cssselect(self, css_selector: str | None = None) -> list:
        if isinstance(self._element, HtmlElement):
            query_result = self._element.cssselect(css_selector)
            return query_result
        elif isinstance(self._element, HtmlElementTree):
            root_element = self._element.getroot()
            query_result = root_element.cssselect(css_selector)
            return query_result
        else:
            return []

    def tostring(self,
                 pretty: bool = True,
                 ) -> str | list[str]:
        if isinstance(self._element, HtmlTree):
            return lxml.html.tostring(self._element,
                                 encoding='unicode',
                                 pretty_print=pretty)
        elif isinstance(self._element, list):
            elements = []
            for element in self._element:
                pretty_element = lxml.html.tostring(element,
                              encoding='unicode',
                              pretty_print=pretty)
                elements.append(pretty_element)
            return elements
        else:
            return ''

    async def save(self,
             save_path: str,
             pretty: bool = True,
             encoding='utf-8',
             ) -> None:
        pretty_html = self.tostring(pretty=pretty)
        _save_path = AsyncPath(save_path)
        if not await _save_path.parent.is_dir():
            await _save_path.mkdir(
                parents=True,
                exist_ok=True,
            )
        if _save_path.suffix != '.html':
            raise FileNotFoundError(
                'save_path must end with ".html"',
            )
        if await _save_path.is_file():
            stat_object = await _save_path.stat()
            if stat_object.st_size > 0:
                await _save_path.write_text('')
            else:
                pass
        else:
            await _save_path.touch(
                exist_ok=True,
            )
        async with _save_path.open(mode='w', encoding=encoding) as f:
            if isinstance(pretty_html, list):
                pretty_html = ''.join(pretty_html)
            elif isinstance(pretty_html, str):
                pass
            else:
                raise RuntimeError('pretty_html must be "element_tree" or "element"')
            for line in pretty_html.splitlines():
                if line.strip() != '':
                    await f.write(line + '\n')
                else:
                    continue
        return None


class XML(object):
    def __init__(self) -> None:
        pass


__all__ = [
    'HTML',
    'XML'
]

