import inspect
import linecache
import locale
import logging
import re
import shutil
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
)

from joblib._store_backends import CacheItemInfo, StoreBackendBase
from slugify import slugify as _slugify

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)
LOCALE_LOCK = threading.Lock()
CURRENT_LOCALE = locale.getlocale()


def get_temp_column_name(df: "pd.DataFrame") -> str:
    """Small helper to get a new column name that does not already exist"""
    temp_column_name = "__tmp__"
    while temp_column_name in df.columns:
        temp_column_name += "_"
    return temp_column_name


@contextmanager
def setlocale(name: Optional[str]) -> Generator[str, None, None]:
    """
    Context manager to set a locale ('en', 'fr', 'de', ...)
    """
    if name is not None:
        name = locale.normalize(f"{name}.UTF-8")
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        except Exception:
            logger.warning(f"Impossible to set locale from {name!r}")
            yield saved
        finally:
            locale.setlocale(locale.LC_ALL, saved)


def get_orig_function(f: Callable[..., Any]) -> Callable[..., Any]:
    """Make use of the __wrapped__ attribute to find the original function
    of a decorated function."""
    try:
        while True:
            f = f.__wrapped__  # type: ignore[attr-defined]
    except AttributeError:
        return f


def get_param_value_from_func_call(
    param_name: str, func: Callable[..., Any], call_args: Sequence[Any], call_kwargs: Dict[str, Any]
) -> Any:
    """
    Get the value of a function's parameter based on its signature
    and the call's args and kwargs.

    Example:
        >>> def foo(a, b, c=3, d=4):
        ...    pass
        ...
        >>> # what would be the value of "c" when calling foo(1, b=2, c=33) ?
        >>> get_param_value_from_func_call('c', foo, [1], {'b': 2, 'c': 33})
        33
    """
    signature = inspect.signature(func)
    params_list = signature.parameters.keys()
    if param_name not in params_list:
        raise TypeError(
            f"'{param_name}' not found in {func.__name__} parameters list ([{params_list}])"
        )
    call = signature.bind(*call_args, **call_kwargs)
    call.apply_defaults()
    return call.arguments[param_name]


def get_func_sourcecode(func: Callable[..., Any]) -> str:
    """
    Try to get sourcecode using standard inspect.getsource().
    If the function comes from a module which has been created dynamically
    (not from the filesystem), then it tries to read the sourcecode on the
    filesystem anyway.
    WARNING: can do weird things if the filesystem code slightly differs from
             the original module code.
    """

    def getsource(func: Callable[..., Any]) -> str:
        lines, lnum = getsourcelines(func)
        return "".join(lines)

    def getsourcelines(func: Callable[..., Any]) -> Tuple[Sequence[str], int]:
        lines, lnum = findsource(func)
        return inspect.getblock(lines[lnum:]), lnum + 1

    def findsource(func: Callable[..., Any]) -> Tuple[List[str], int]:
        file = getfile(func)  # file path
        module = inspect.getmodule(func, file)
        lines = linecache.getlines(file, module.__dict__)
        code = func.__code__
        lnum = code.co_firstlineno - 1
        pat = re.compile(r"^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)")
        while lnum > 0:
            if pat.match(lines[lnum]):
                break
            lnum = lnum - 1  # pragma: no cover
        return lines, lnum

    def getfile(func: Callable[..., Any]) -> str:
        module = inspect.getmodule(func)
        return module.__file__  # type: ignore

    try:
        return inspect.getsource(func)
    except Exception:
        return getsource(func)


def check_params_columns_duplicate(cols_name: List[str]) -> bool:
    params = [column for column in cols_name if column is not None]
    if len(set(params)) != len(params):
        duplicates = set([x for x in params if params.count(x) > 1])
        raise ParamsValueError(f"Duplicate declaration of column(s) {duplicates} in the parameters")
    else:
        return True


def slugify(name: str, separator: str = "-") -> str:
    """Returns a slugified name (we allow _ to be used)"""
    return _slugify(name, regex_pattern="[^-_a-z0-9]+", separator=separator)


def resolve_dependencies(func_name: str, dependencies: Dict[str, List[str]]) -> List[str]:
    """Given a function name and a mapping of function dependencies,
    returns a list of *all* the dependencies for this function."""

    def _resolve_deps(func_name: str, func_deps: List[str]) -> None:
        """Append dependencies recursively to func_deps (accumulator)"""
        if func_name in func_deps:
            return

        func_deps.append(func_name)
        for dep in dependencies.get(func_name, []):
            _resolve_deps(dep, func_deps)

    func_deps: List[str] = []
    _resolve_deps(func_name, func_deps)
    return sorted(func_deps)


def clean_cachedir_old_entries(cachedir: StoreBackendBase, func_name: str, limit: int) -> int:
    """Remove old entries from the cache"""
    if limit < 1:
        raise ValueError("'limit' must be greater or equal to 1")

    cache_entries = get_cachedir_entries(cachedir, func_name)
    cache_entries = sorted(
        cache_entries, key=lambda e: e.last_access, reverse=True  # type: ignore[no-any-return]
    )
    cache_entries_to_remove = cache_entries[limit:]
    for entry in cache_entries_to_remove:
        shutil.rmtree(entry.path, ignore_errors=True)

    return len(cache_entries_to_remove)


def get_cachedir_entries(cachedir: StoreBackendBase, func_name: str) -> List[CacheItemInfo]:
    entries = cachedir.get_items()
    return [e for e in entries if Path(e.path).parent.name == func_name]


class ParamsValueError(Exception):
    """
    Exception raised when some parameters value are wrong
    """
