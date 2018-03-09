import random
import shutil
import tempfile
import time

import pytest

from toucan_data_sdk.utils.decorators import (
    cache as etl_cache,
    method_cache,
    setup_cachedir
)


@pytest.fixture
def cache():
    cachedir = tempfile.mkdtemp(prefix='pytest_cache')
    setup_cachedir(cachedir)
    yield etl_cache
    shutil.rmtree(cachedir)
    del etl_cache.memories


def test_cache_typeerrors(cache):
    with pytest.raises(TypeError):
        @cache(check_param=42)
        def foo1():
            pass

    with pytest.raises(TypeError):
        @cache(limit='hey')
        def foo2():
            pass


def test_cache_basic(cache):
    @cache()
    def foo(x):
        return random.random()

    run_1 = foo(1)
    run_2 = foo(1)
    assert run_1 == run_2

    run_3 = foo(2)
    assert run_3 != run_2


def test_cache_check_param(cache):
    @cache(check_param=False)
    def foo(x):
        return x

    run_1 = foo(1)
    assert run_1 == 1
    run_2 = foo(2)
    assert run_2 == 1

    @cache(check_param='version')
    def bar(x, version=1):
        return x

    run_1 = bar(1)
    assert run_1 == 1
    run_2 = bar(2)
    assert run_2 == 1
    run_3 = bar(2, version=2)
    assert run_3 == 2


def test_cache_limit(cache):
    @cache(limit=2)
    def baz(x):
        return random.random()

    # sleeps are necessary so cache entries have different mtime
    run_1 = baz(1)
    time.sleep(0.05)
    assert baz(1) == run_1
    time.sleep(0.05)
    baz(2)
    time.sleep(0.05)
    assert baz(1) == run_1
    time.sleep(0.05)
    baz(3)  # it should delete run_1 result (because limit=2)
    time.sleep(0.05)
    assert baz(1) != run_1

    @cache(limit=0)
    def baz0():
        pass

    with pytest.raises(ValueError):
        baz0()


def test_cache_dependencies(cache):
    @cache()
    def foo2():
        return 2

    @cache(requires=[foo2, 'foo3'])
    def foo6():
        return foo2() * foo3()

    @cache(requires=foo2)
    def foo3():
        return foo2() + 1

    assert foo6() == 6

    @cache(requires=['nope'])
    def foo():
        pass

    with pytest.raises(Exception):
        foo()


def test_cache_disabled():
    @etl_cache()
    def foo():
        return random.random()

    assert foo() != foo()


def test_cache_on_method(cache):
    class Foo:
        @method_cache()
        def compute(self, x):
            return x + random.random()

    foo = Foo()

    assert foo.compute(42) == foo.compute(42)
