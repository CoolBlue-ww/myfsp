from fastapi import APIRouter, File, UploadFile, Form
from pathlib import Path
from pydantic import BaseModel
from typing import Union
from io import BytesIO
from PIL import Image
from pathlib import Path
import platform
import aiofiles
from aiopath import AsyncPath
from aiofile import AIOFile
from ..config import Config


ROUTERS = Config().get_settings(
    name='routers',
    unite=(True, '-r')
).get('routers', '')

SORTED_IMAGES_SAVE_DIR = Path(ROUTERS.get(
    'cvx', ''
).get('SORTED_IMAGES_SAVE_DIR', '')
)

TEMP_SYSTEM = ROUTERS.get(
    'system', ''
).lower() 

SYSTEM = TEMP_SYSTEM if TEMP_SYSTEM else platform.system().lower()

cvx_router = APIRouter(
    prefix='/cvx',
    tags=['cvx'],
)

async def cvx_img_sort(
        image_name: str,
        suffix: str = '.jpg',
        image: Union[BytesIO, bytes] = b'',
    ) -> None:
    img = image if isinstance(image, BytesIO) else BytesIO(image)
    pil_img = Image.open(img)
    width, height = pil_img.size
    aspect_ratio = width / height
    deep_dir = AsyncPath(SORTED_IMAGES_SAVE_DIR.joinpath(
        str(aspect_ratio),
        f'{width}x{height}',
    ))
    if not await deep_dir.exists():
        await deep_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
    save_file = deep_dir.joinpath(
        image_name
    ).with_suffix(
        suffix=suffix
    )

    if SYSTEM == 'linux':
        async with AIOFile(filename=save_file, mode='wb') as file:
            await file.write(image)
    if SYSTEM in {'windows', 'macos', 'darwin'}:
        async with aiofiles.open(file=save_file, mode='wb') as file:
            await file.write(image)
    return None

@cvx_router.post('/img_sort')
async def img_sort(
    file: UploadFile = File(...),
    suffix: str = Form('.jpg'),
):
    image_name = file.filename
    image = await file.read()
    await cvx_img_sort(
        image_name=image_name,
        image=image,
        suffix=suffix
    )
    message = {
        'message': 'success'
    }
    return message

async def cvx_normalize():
    pass

class NormalizeItem(BaseModel):
    pass

@cvx_router.post('/nurmalize')
async def normalize():
    pass
