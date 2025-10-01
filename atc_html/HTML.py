from pathlib import Path
from lxml import html
from io import StringIO
from typing import  Optional, Union, TypeVar, List, Any
import hashlib


T = TypeVar('T')

class HTMLStorage(object):
    __slots__ = ()

    def __init__(self) -> None:
        pass

    @staticmethod
    def save_html(url: Optional[str] = None,
                  html_text: Optional[str] = None,
                  save_dir: Optional[Union[str, Path]] = None,
                  encoding: str = 'utf-8'
                  ) -> None:

        save_dir = save_dir if isinstance(save_dir, Path) else Path(save_dir)

        if not save_dir.exists():
            save_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

        filename = hashlib.sha256(url.encode('utf-8')).hexdigest()

        save_file = save_dir.joinpath(
            filename,
        ).with_suffix('.atc_html')

        memory_file = StringIO(html_text)

        tree = html.parse(memory_file)

        html_text = html.tostring(tree, encoding='unicode', pretty_print=True)

        with save_file.open(mode='wt', encoding=encoding) as file:
            file.write(html_text)

        return None


class HTMLParse(object):
    __slots__ = (
        '_element',
    )

    def __init__(self,
                 html_text: Optional[str] = None,
                 html_path: Optional[Union[str, Path]] = None,
                 encoding: str = 'utf-8',
                 ) -> None:
        self._element = T
        if html_text:
            self._element = html.document_fromstring(html_text)
        elif html_path:
            html_path = html_path if isinstance(html_path, Path) else Path(html_path)
            with html_path.open(mode='rt', encoding=encoding) as file:
                element_tree = html.parse(file)
                self._element = element_tree.getroot()
        else:
            raise RuntimeError(
                'html_text or html_path must be given'
            )

    def xpath(self,
              xpath: Optional[str] = None,
              ) -> List[Any]:
        query_result = self._element.xpath(xpath)
        return query_result

    def cssselect(self,
                  css_selector: Optional[str] = None,
                  ) -> List[Any]:
        query_result = self._element.cssselect(css_selector)
        return query_result


__all__ = [
    'HTMLStorage',
    'HTMLParse'
]
