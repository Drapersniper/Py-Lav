from __future__ import annotations

import inspect
import pathlib
import sys
from typing import Callable, TypeVar, get_type_hints

from pylav.ext.bundled_node.utils import get_true_path
from pylav.type_hints.generics import ANY_GENERIC_TYPE, PARAM_SPEC_TYPE

T = TypeVar("T")


def _get_path(path: T | pathlib.Path) -> str | T | None:

    return get_true_path(path, fallback=path)


def update_event_loop_policy() -> None:
    if sys.implementation.name == "cpython":
        # Let's not force this dependency, uvloop is much faster on cpython
        try:
            import uvloop  # type: ignore
        except ImportError:
            pass
        else:
            import asyncio

            if not isinstance(asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy):
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def check_annotated(
    func: Callable[PARAM_SPEC_TYPE, ANY_GENERIC_TYPE]  # type: ignore
) -> Callable[PARAM_SPEC_TYPE, ANY_GENERIC_TYPE]:  # type: ignore
    hints = get_type_hints(func, include_extras=True)
    spec = inspect.getfullargspec(func)

    def wrapper(*args: PARAM_SPEC_TYPE.args, **kwargs: PARAM_SPEC_TYPE.kwargs) -> ANY_GENERIC_TYPE:
        for idx, arg_name in enumerate(spec[0]):
            hint = hints.get(arg_name)
            validators = getattr(hint, "__metadata__", None)
            if not validators:
                continue
            for validator in validators:
                validator.validate_value(args[idx])

        return func(*args, **kwargs)

    return wrapper
