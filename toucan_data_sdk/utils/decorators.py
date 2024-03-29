"""
Implements a series of decorators functions with decorator arguments (logger).
Decorators modify the behaviour of a function to execute code before and after
the original function.

They are a very useful pattern for logging, timing functions, retrying execution,
checking credentials, patching methods or caching for example.


Examples:

    # augment.py
    import logging
    from toucan_data_sdk.utils.decorators import log_message, log_time, log_shapes


    logger = logging.getLogger(__name__)

    @log_shapes(logger)
    @log_message(logger, "Replace affaires with parent affaires")
    @log_time(logger)
    def parse_reseau(df):
        # Do transformations
        return df

Output:
    >>> 2016-06-23 11:21 - INFO - small_apps.demo.preprocess.augment
                                | parse_reseau - time: 50.1 ms
    >>> 2016-06-23 11:21 - INFO - small_apps.demo.preprocess.augment
                                | parse_reseau - Replace affaires with parent affaires
    >>> 2016-06-23 11:21 - INFO - small_apps.demo.preprocess.augment
                                | parse_reseau - [(5821, 210)] -> [(662, 15)]

Note:
    You can apply multiple decorators to the same function.
    The decorators get applied in order from bottom to top.

"""
import logging
import time
from functools import partial, wraps
from hashlib import md5
from threading import current_thread
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import joblib
import pandas as pd

from .helpers import (
    clean_cachedir_old_entries,
    get_func_sourcecode,
    get_orig_function,
    get_param_value_from_func_call,
    resolve_dependencies,
)

_logger = logging.getLogger(__name__)


def catch(logger: logging.Logger) -> Callable[..., Any]:
    """
    Decorator to catch an exception and don't raise it.
    Logs information if a decorator failed.

    Note:
        We don't want possible exceptions during logging to be raised.
        This is used to decorate any function that gets executed
        before or after the execution of the decorated function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.warning(f"Exception raised in decorator: {func.__name__}")

        return wrapper

    return decorator


def _get_dfs(*args: Any, **kwargs: Any) -> List[pd.DataFrame]:
    values = args + tuple(kwargs.values())
    return [value for value in values if isinstance(value, pd.DataFrame)]


@catch(_logger)
def _get_dfs_shapes(*args: Any, **kwargs: Any) -> List[Tuple[int, int]]:
    return [df.shape for df in _get_dfs(*args, **kwargs)]


@catch(_logger)
def _log_shapes(
    logger: logging.Logger,
    func_name: str,
    input_shapes: List[Tuple[int, int]],
    output_shapes: List[Tuple[int, int]],
) -> None:
    logger.info(f"{func_name} - {input_shapes} -> {output_shapes}")


@catch(_logger)
def _log_time(logger: logging.Logger, func_name: str, start: int, end: int) -> None:
    duration = (end - start) * 1000
    logger.info(f"{func_name} - time: {duration:0.1f} ms")


@catch(_logger)
def _log_message(logger: logging.Logger, func_name: str, message: str) -> None:
    logger.info(f"{func_name} - {message}")


def log_message(logger: logging.Logger, message: str = "") -> Callable[..., Any]:
    """
    Decorator to log a message before executing a function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _log_message(logger, func.__name__, message)
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def log_time(logger: logging.Logger) -> Callable[..., Any]:
    """
    Decorator to log the execution time of a function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            _log_time(logger, func.__name__, start, end)
            return result

        return wrapper

    return decorator


def log_shapes(logger: logging.Logger) -> Callable[..., Any]:
    """
    Decorator to log the shapes of input and output dataframes

    It considers all the dataframes passed either as arguments or keyword arguments as inputs
    and all the dataframes returned as outputs.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            input_shapes = _get_dfs_shapes(*args, **kwargs)
            result = func(*args, **kwargs)
            output_shapes = _get_dfs_shapes(result)
            _log_shapes(logger, func.__name__, input_shapes, output_shapes)
            return result

        return wrapper

    return decorator


def log(
    logger: Optional[logging.Logger] = None,
    start_message: str = "Starting...",
    end_message: str = "Done...",
) -> Callable[[Callable[..., Any], logging.Logger], Callable[..., Any]]:
    """
    Basic log decorator
    Can be used as :
    - @log (with default logger)
    - @log(mylogger)
    - @log(start_message='Hello !", logger=mylogger, end_message='Bye !')
    """

    def actual_log(
        f: Callable[..., Any], real_logger: Optional[logging.Logger] = logger
    ) -> Callable[..., Any]:
        logger = real_logger or _logger

        @wraps(f)
        def timed(*args, **kwargs):
            logger.info(f"{f.__name__} - {start_message}")
            start = time.time()
            res = f(*args, **kwargs)
            end = time.time()
            logger.info(f"{f.__name__} - {end_message} (took {end - start:.2f}s)")
            return res

        return timed

    if callable(logger):
        return actual_log(logger, real_logger=None)  # type: ignore[unreachable]
    return actual_log


def domain(domain_name: str) -> Callable[..., Any]:
    """
    Allow to apply a function f(df: DataFrame) -> DataFrame) on dfs by specifying the key
    E.g instead of writing:
        def process_domain1(dfs):
            df = dfs['domain1']
            # actual process
            dfs['domain1'] = df
            return dfs

    You can write:
        @domain('domain1')
        def process_domain1(df):
            #actual process
            return df
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Dict[str, pd.DataFrame]:
            dfs, *args = args  # type: ignore[assignment]
            if not isinstance(dfs, dict):
                raise TypeError(f"{dfs} is not a dict")
            df = dfs.pop(domain_name)
            df = func(df, *args, **kwargs)
            return {domain_name: df, **dfs}

        return wrapper

    return decorator


# ~~~ @cache decorator related stuff ~~~


def cache(  # noqa: C901
    requires: Union[None, Callable[..., Any], List[Union[str, Callable[..., Any]]]] = None,
    disabled: bool = False,
    applied_on_method: bool = False,
    check_param: Union[bool, str] = True,
    limit: Optional[int] = None,
) -> Callable[..., Any]:
    """Avoid to recompute a function if its parameters and its source code doesnt have changed.

    Args:
        requires: list of dependencies (functions or function names)
        disabled (bool): disable the cache mecanism for this function (useful if you
                             only want to use the dependency mecanism)
        applied_on_method (bool): ignore the first argument (useful to ignore "self")
        check_param (True, False or a str): the name of the parameter to check.
                                                False to not check any of them.
                                                True (default) to check all of them.
        limit (int or None): number of cache entries to keep (no limit by default)
    """
    requires_list: List[Union[str, Callable[..., Any]]]
    if not requires:
        requires_list = []
    elif callable(requires):
        requires_list = [requires]
    else:
        requires_list = requires

    if not isinstance(check_param, (bool, str)):
        raise TypeError("'check_param' must be a str (name of the param to check) or a bool")
    if limit is not None and not isinstance(limit, int):
        raise TypeError("'limit' must be an int (number of cache entries to keep) or None")

    # We keep data in the function attributes so that this data
    # is not erased between two calls:
    if not hasattr(
        cache, "funcs_references"
    ):  # dict of {function_name -> function_object (or None)}
        cache.funcs_references = {}  # type: ignore[attr-defined]
    if not hasattr(cache, "dependencies"):  # dict of {function_name -> [list of function names]}
        cache.dependencies = {}  # type: ignore[attr-defined]
    if not hasattr(cache, "memories"):  # dict of {thread_id -> joblib.Memory object}
        cache.memories = {}  # type: ignore[attr-defined]

    def decorator(func):
        """This code is executed when the augment module is read (when decorator is applied).
        Here we populate cache.funcs_references and cache.dependencies to use them later."""
        cache.funcs_references[func.__name__] = get_orig_function(func)  # type: ignore
        dependencies_names = []
        for requirement in requires_list:
            if callable(requirement):
                req_name = requirement.__name__
                cache.funcs_references[req_name] = get_orig_function(requirement)  # type: ignore[attr-defined]
            elif requirement not in cache.funcs_references:  # type: ignore[attr-defined]
                req_name = requirement
                cache.funcs_references[req_name] = None  # type: ignore[attr-defined]
            dependencies_names.append(req_name)

        cache.dependencies[func.__name__] = dependencies_names  # type: ignore[attr-defined]

        @wraps(func)
        def wrapper(*args, **kwargs):
            """This code is executed when a decorated function is actually executed.
            It uses the previously built dependency tree (see above)."""
            current_memory = cache.memories.get(current_thread().name)  # type: ignore[attr-defined]
            if disabled is True or current_memory is None:
                return func(*args, **kwargs)

            # if cache is enabled, we compute the md5 hash of the concatenated source codes
            # of all the dependencies.
            concatenated_source_code = ""
            dependencies = resolve_dependencies(func.__name__, cache.dependencies)  # type: ignore[attr-defined]
            for func_name in dependencies:
                function = cache.funcs_references[func_name]  # type: ignore[attr-defined]
                if function is None:
                    raise Exception(f"Can't get source code of function {func_name!r}")
                source_code = get_func_sourcecode(function)
                concatenated_source_code += source_code
            md5_hash = md5(str.encode(concatenated_source_code)).hexdigest()

            # Add extra parameters so that joblib checks they didnt have changed:
            tmp_extra_kwargs = {
                "__func_dependencies_hash__": md5_hash,
                "__original_func_name__": func.__name__,
            }

            if check_param is True:
                kwargs.update(tmp_extra_kwargs)

                if applied_on_method:
                    self_arg, args = args[0], args[1:]

                def f(*args, **kwargs):
                    # delete the extra parameters that the underlying function doesnt expect:
                    for k in tmp_extra_kwargs.keys():
                        del kwargs[k]

                    if applied_on_method:
                        args = (self_arg,) + args
                    return func(*args, **kwargs)

                f = current_memory.cache(f)
                result = f(*args, **kwargs)  # type: ignore[no-untyped-call]
            else:
                if isinstance(check_param, str):
                    check_only_param_value = get_param_value_from_func_call(
                        param_name=check_param, func=func, call_args=args, call_kwargs=kwargs
                    )
                    tmp_extra_kwargs["__check_only__"] = check_only_param_value

                def f(*a, **k):
                    return func(*args, **kwargs)

                f = current_memory.cache(f)
                result = f(**tmp_extra_kwargs)  # type: ignore[no-untyped-call]

            if limit is not None:
                clean_cachedir_old_entries(
                    f.store_backend,  # type: ignore[attr-defined]
                    f.__name__,
                    limit,
                )

            return result

        return wrapper

    return decorator


method_cache = partial(cache, applied_on_method=True)


def setup_cachedir(
    cachedir: str, mmap_mode: Optional[str] = None, bytes_limit: Optional[int] = None
) -> joblib.Memory:
    """This function injects a joblib.Memory object in the cache() function
    (in a thread-specific slot of its 'memories' attribute)."""
    if not hasattr(cache, "memories"):
        cache.memories = {}  # type: ignore[attr-defined]

    memory = joblib.Memory(
        location=cachedir, verbose=0, mmap_mode=mmap_mode, bytes_limit=bytes_limit
    )
    cache.memories[current_thread().name] = memory  # type: ignore[attr-defined]
    return memory
