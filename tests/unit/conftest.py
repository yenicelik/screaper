import pytest

from screaper.resources.entities import Markup, UrlTaskQueue


@pytest.fixture
def mock_url_task_queue_object():
    obj = UrlTaskQueue(
        url="https://www.trulia.com/p/ny/brooklyn/327-101st-st-1a-brooklyn-ny-11209–2180131215",
        referrer_url="https://www.twitter.com",
        crawler_processing_sentinel=False,
        crawler_processed_sentinel=False,
        crawler_skip=False,
        engine_version="test-0.0.1"
    )
    return obj

@pytest.fixture
def mock_markup_object():
    obj = Markup(
        url="https://www.trulia.com/p/ny/brooklyn/327-101st-st-1a-brooklyn-ny-11209–2180131215",
        markup="<div></div>",
        spider_processing_sentinel=False,
        spider_processed_sentinel=False,
        spider_skip=False,
        engine_version="test-0.0.1"
    )
    return obj

@pytest.fixture
def mock_get_sqlalchemy(mocker):
    # TODO: How to overwrite sqlalchemy connection?
    mock = mocker.Mock()
    return mock
