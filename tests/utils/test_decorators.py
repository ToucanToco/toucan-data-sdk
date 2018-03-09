import pytest
import pandas as pd

from toucan_data_sdk.utils.decorators import (
    log_time, log_shapes, log_message, domain,
    logger as catch_logger
)


def test_log_time(mocker):
    logger = mocker.MagicMock()

    @log_time(logger)
    def foo():
        pass

    foo()
    logger.info.assert_called_once()
    args = logger.info.call_args[0]
    assert 'foo' in args[0]

    logger.info.side_effect = ZeroDivisionError
    mock_warning = mocker.patch.object(catch_logger, 'warning')
    foo()
    mock_warning.assert_called_once()
    args = mock_warning.call_args[0]
    assert 'Exception raised in decorator' in args[0]


def test_log_shapes(mocker):
    logger = mocker.MagicMock()

    @log_shapes(logger)
    def foo(df):
        pass

    df = pd.DataFrame({'values': [1, 2, 3]})
    foo(df)
    logger.info.assert_called_once()
    args = logger.info.call_args[0]
    assert 'foo' in args[0]
    assert repr(df.shape) in args[0]


def test_log_message(mocker):
    logger = mocker.MagicMock()

    @log_message(logger, "yolo")
    def foo():
        pass

    foo()
    logger.info.assert_called_once()
    args = logger.info.call_args[0]
    assert 'foo' in args[0]
    assert 'yolo' in args[0]


def test_domain(mocker):
    @domain('domain1')
    def process_domain1(df):
        return df + df

    dfs = {'domain1': pd.DataFrame({'x': [1, 2, 3]})}
    dfs = process_domain1(dfs)
    assert list(dfs['domain1'].x) == [2, 4, 6]

    with pytest.raises(TypeError):
        process_domain1(42)
