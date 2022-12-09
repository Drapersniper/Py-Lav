from __future__ import annotations

import functools
from collections.abc import Awaitable
from typing import Callable

from pylav.constants.config import READ_CACHING_ENABLED
from pylav.storage.database.caching.cache import CACHE
from pylav.storage.database.caching.functions import key_builder
from pylav.type_hints.generics import ANY_GENERIC_TYPE, PARAM_SPEC_TYPE


def maybe_cached(func: Callable[[PARAM_SPEC_TYPE], ANY_GENERIC_TYPE]) -> Callable[[], ANY_GENERIC_TYPE]:
    @functools.wraps(func)
    async def wrapper(
        *args: PARAM_SPEC_TYPE.args, **kwargs: PARAM_SPEC_TYPE.kwargs
    ) -> Awaitable[Callable[[PARAM_SPEC_TYPE], ANY_GENERIC_TYPE]]:
        if READ_CACHING_ENABLED:
            return await CACHE(ttl=None, key=key_builder(func, *args, **kwargs))(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper
