from importlib import util
from pathlib import Path
import asyncio, inspect


class Container(object):
    pass

class Loader(object):
    __slots__ = ('load_path',)

    def __init__(self, load_path: str) -> None:
        self.load_path = load_path

    def sync_load_module(self):
        if not Path(self.load_path).is_file():
            raise FileNotFoundError(f'{self.load_path} is not a file')
        load_path = Path(self.load_path)
        spec = util.spec_from_file_location(
            load_path.name.split(
                sep=".", maxsplit=1)[0],
            str(self.load_path),
        )
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    async def async_load_module(self):
        module = await asyncio.to_thread(
            self.sync_load_module,
        )
        return module

class AddonInstances(object):
    def __init__(self, load_path: str) -> None:
        self.loader = Loader(load_path=load_path)
        self._addon_instances = {}

    @property
    def addon_instances(self) -> dict:
        return self._addon_instances

    @staticmethod
    def _is_local_sync_obj(name, obj, module) -> tuple[bool, str]:
        if getattr(obj, "__module__", None) == module.__name__:
            if inspect.isfunction(obj) and not inspect.iscoroutinefunction(obj):
                if not name.startswith("_"):
                    return True, "function"
            if inspect.isclass(obj):
                return True, "class"
        return False, "unknow"

    async def _async_process_attrs(self) -> tuple[dict, dict]:
        addons_module = await self.loader.async_load_module()
        attrs = addons_module.__dict__
        functions, classes = {}, {}
        for name, obj in attrs.items():
            in_module, object_type = self._is_local_sync_obj(name, obj, addons_module)
            if in_module:
                if object_type == "function":
                    functions[name] = obj
                if object_type == "class":
                    classes[name] = obj
        return functions, classes

    async def create_addons_instances(self):
        functions, classes = await self._async_process_attrs()
        if functions:
            for name, function in functions.items():
                setattr(Container, name, function)
        self._addon_instances["container"] = Container()
        if classes:
            for name, class_ in classes.items():
                self._addon_instances[name] = class_()
        return self.addon_instances


__all__ = [
    "AddonInstances",
]
