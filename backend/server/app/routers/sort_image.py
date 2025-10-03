from PIL import Image
from io import BytesIO
import os
from PIL.ImageFile import ImageFile
from pathlib import Path


class ImageSize(object):
    __slots__ = ["_response_"]
    def __init__(self) -> None:
        self._response_: bytes = b""

    @property
    def image_size(self) -> tuple[int, int]:
        _image: ImageFile = Image.open(
            BytesIO(
                self._response_
            )
        )
        _image_size: tuple[int, int] = _image.size
        return _image_size

    @property
    def response(self) -> bytes:
        return self._response_

    @response.setter
    def response(self, value) -> None:
        self._response_: bytes = value

class IsExistDir(DefaultOutput):
    __slots__ = ["_default_dir_"]
    def __init__(self) -> None:
        super().__init__()
        self._default_dir_: str =  super().default_output

    @property
    def to_dir(self) -> str:
        return self._default_dir_

    @to_dir.setter
    def to_dir(self, value) -> None:
        if bool(value):
            if os.path.exists(value):
                self._default_dir_: str = value
            else:
                os.makedirs(value, exist_ok=True)
                self._default_dir_: str = value
        else:
            self._default_dir_: str = self._default_dir_

class ModelExtraction(object):
    pass


class SortImages(object):
    __slots__ = ["_change_dir", "_default", "_image_parent", "_response"]
    def __init__(self, response) -> None:
        self._response: bytes = response
        self._image_parent: ImageSize = ImageSize()

    def sort_image(self) -> tuple[float, tuple[int, int]]:
        self._image_parent.response = self._response
        size: tuple[int, int] = self._image_parent.image_size
        aspect_ratio: float = size[0] / size[1]
        return aspect_ratio, size


class MakeImagePath(IsExistDir):
    def __init__(self) -> None:
        super().__init__()
        self._change_dir: str = ""
        self.to_dir: str = self._change_dir
        self._default: str = self._default_dir_

        self._image_class: str = ""
        self._aspect_ratio: float = 0
        self._image_size: tuple[int, int] = (0, 0)
        self._image_name: str = ""

    def update_init_default(self) -> None:
        self._default: str = self.to_dir
        return None

    def join_image_out_dir(self) -> str:
        self.update_init_default()
        image_out_dir: str = os.path.join(
            self._default,
            "images",
            self._image_class,
            f"aspect_ratio--{self._aspect_ratio}",
            "*".join([str(self._image_size[0]), str(self._image_size[1])]),
        )
        return image_out_dir

    def make_out_dir(self) -> None:
        image_out_dir: str = self.join_image_out_dir()
        os.makedirs(image_out_dir, exist_ok=True)
        return None

    @property
    def out_dir(self) -> str:
        return self._change_dir

    @out_dir.setter
    def out_dir(self, value) -> None:
        self._change_dir: str = value
        self.to_dir: str = value
        self.make_out_dir()

    @property
    def image_class(self) -> str:
        return self._image_class

    @image_class.setter
    def image_class(self, value) -> None:
        self._image_class = value

    @property
    def aspect_ratio(self) -> float:
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, value) -> None:
        self._aspect_ratio = value

    @property
    def image_size(self) -> tuple[int, int]:
        return self._image_size

    @image_size.setter
    def image_size(self, value) -> None:
        self._image_size = value

    @property
    def image_name(self):
        return self._image_name

    @image_name.setter
    def image_name(self, value) -> None:
        self._image_name = value


class SaveImage(object):
    __slots__ = ["_image_response", "_image_out_path"]
    def __init__(self,
                 image_response: ImageFile,
                 image_out_path: str
        ) -> None:
        self._image_response = image_response
        self._image_out_path = image_out_path

    def save_image(self) -> None:
        self._image_response.save(self._image_out_path)
        return None


class Trunk(object):
    pass



abc = MakeImagePath()
abc.out_dir = "/home/SayMyName/桌面/GitHub/among_the_cobwebs/among_the_cobwebs/AtcCV/https"
abc.image_class = "cat"
abc.aspect_ratio = 1.5
abc.image_size = (30, 30)
abc.image_name = "可爱的金色泰迪小狗图片"

abc.make_out_dir()

# self._image_name