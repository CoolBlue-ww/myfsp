import tomllib
import asyncio
import deepmerge
from pathlib import Path
from aiopath import AsyncPath
from typing import Dict, Any, Union, Optional


class Config(object):
    suffix = '.toml'
    mode = 'rb'
    encoding = None

    __slots__ = (
        'config_file',
    )

    def __init__(self) -> None:
        self.config_file = Path(__file__).parent.joinpath(
            'config', 'config'
        ).with_suffix(Config.suffix)

    @staticmethod
    def _merge_settings(settings: Dict, custom_settings: Dict):
        merger = deepmerge.Merger(
            [(dict, ['merge'])],
            ['override'],
            ['override'],
        )
        merge_settings = merger.merge(
            settings,
            custom_settings,
        )
        return merge_settings

    def _load_config_toml(self):
        with self.config_file.open(mode=Config.mode, encoding=Config.encoding) as cfgf:
            settings = tomllib.load(cfgf)
            return settings
    
    @staticmethod
    def _load_custom_config_toml(custom_config_file: Path):
        with custom_config_file.open(mode=Config.mode, encoding=Config.encoding) as ccfgf:
            settings = tomllib.load(ccfgf)
            return settings

    async def load_config(self,
                     config_file: Optional[str] = None
                     ) -> Union[Dict[str, Any], str]:
        custom_config_file = AsyncPath(
            config_file if config_file else ''
        ) 
        try:
            if await custom_config_file.exists() and \
                    await custom_config_file.is_file() and \
                        custom_config_file.suffix == Config.suffix:
                
                    settings = await asyncio.to_thread(
                        self._load_config_toml,
                    )
                    custom_settings = await asyncio.to_thread(
                        self._load_custom_config_toml,
                        Path(
                            custom_config_file
                        )
                    )
                    merge_settings = await asyncio.to_thread(
                        self._merge_settings,
                        settings,
                        custom_settings,
                    )
                    return merge_settings
                
            else:
                settings = await asyncio.to_thread(
                    self._load_config_toml,
                )
                return settings
        except Exception as e:
            error_message = {
                'message': f"ERROR: {e}"
            }
            return error_message
    
CONFIG = Dict[str, Any]
GET_SETTINGS = Any

class ConfigPerser(object):
    __slots__ = ()

    def __init__(self):
        pass

    def get_lifespan_settings(self, config: CONFIG) -> GET_SETTINGS:
        lifespan_settings = config.get('lifespan', '')
        return lifespan_settings
    
    def get_automation_settings(self, config: CONFIG) -> GET_SETTINGS:
        automation_settings = config.get('automation', '')
        return automation_settings
    
    def get_proxy_settings(self, config: CONFIG) -> GET_SETTINGS:
        proxy_settings = config.get('proxy', '')
        return proxy_settings
    
    def get_request_settings(self, config: CONFIG) -> GET_SETTINGS:
        request_settings = config.get('request', '')
        return request_settings


__all__ = [
    'Config',
    'ConfigPerser',
]



# {'lifespan': {'lifespan': 10, 'wait': 5}, 'routers': {'routers': ['cvx', 'run', 'shutdown', 'request', 'headers']}}
# {'lifespan': {'lifespan': 50, 'wait': 100, 'sleep': 0.25}, 'routers': {'routers': ['cvx', 'run', 'shutdown', 'request', 'headers']}}