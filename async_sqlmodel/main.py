from typing import Any, ClassVar, Coroutine, Dict, Tuple, Type

from pydantic._internal._repr import Representation
from sqlalchemy.util.concurrency import greenlet_spawn
from sqlmodel import SQLModel
from sqlmodel._compat import get_annotations
from sqlmodel.main import SQLModelMetaclass


class AwaitableFieldInfo(Representation):
    def __init__(self, *, field: str):
        self.field = field


def AwaitableField(*, field: str) -> Any:
    return AwaitableFieldInfo(field=field)


class AsyncSQLModelMetaclass(SQLModelMetaclass):
    __async_sqlmodel_awaitable_fields__: Dict[str, AwaitableFieldInfo]

    def __new__(
        cls,
        name: str,
        bases: Tuple[Type[Any], ...],
        class_dict: Dict[str, Any],
        **kwargs: Any
    ) -> Any:
        awaitable_fields: Dict[str, AwaitableFieldInfo] = {}
        dict_for_sqlmodel = {}
        original_annotations = get_annotations(class_dict)
        sqlmodel_annotations = {}
        awaitable_fields_annotations = {}
        for k, v in class_dict.items():
            if isinstance(v, AwaitableFieldInfo):
                awaitable_fields[k] = v
            else:
                dict_for_sqlmodel[k] = v
        for k, v in original_annotations.items():
            if k in awaitable_fields:
                awaitable_fields_annotations[k] = v
            else:
                sqlmodel_annotations[k] = v

        dict_used = {
            **dict_for_sqlmodel,
            "__async_sqlmodel_awaitable_fields__": awaitable_fields,
            "__annotations__": sqlmodel_annotations,
        }
        return super().__new__(cls, name, bases, dict_used, **kwargs)

    def __init__(
        cls, classname: str, bases: Tuple[type, ...], dict_: Dict[str, Any], **kw: Any
    ) -> None:
        for field_name, field_info in cls.__async_sqlmodel_awaitable_fields__.items():

            def get_awaitable_fields(self) -> Coroutine[Any, Any, Any]:
                return greenlet_spawn(getattr, self, field_info.field)

            setattr(cls, field_name, property(get_awaitable_fields))  # type: ignore

        SQLModelMetaclass.__init__(cls, classname, bases, dict_, **kw)


class AsyncSQLModel(SQLModel, metaclass=AsyncSQLModelMetaclass):
    __async_sqlmodel_awaitable_fields__: ClassVar[Dict[str, AwaitableFieldInfo]]
