import pytest

from ocdeployer.images import import_images


@pytest.fixture
def mock_oc(mocker):
    _mock_oc = mocker.patch("ocdeployer.images.oc")
    yield _mock_oc


def _check_oc_calls(mocker, mock_oc):
    assert mock_oc.call_count == 2
    calls = [
        mocker.call(
            "import-image",
            "image1:tag",
            "--from=docker.url/image1:sometag",
            "--confirm",
            "--scheduled=True",
            _reraise=True,
        ),
        mocker.call(
            "import-image",
            "image2:tag",
            "--from=docker.url/image2:sometag",
            "--confirm",
            "--scheduled=True",
            _reraise=True,
        ),
    ]
    mock_oc.assert_has_calls(calls)


def test_old_style_syntax(mocker, mock_oc):
    config_content = {
        "images": [
            {"image1:tag": "docker.url/image1:sometag"},
            {"image2:tag": "docker.url/image2:sometag"},
        ]
    }

    import_images(config_content, [])

    _check_oc_calls(mocker, mock_oc)


def test_new_style_syntax(mocker, mock_oc):
    config_content = {
        "images": [
            {"istag": "image1:tag", "from": "docker.url/image1:sometag"},
            {"istag": "image2:tag", "from": "docker.url/image2:sometag"},
        ]
    }

    import_images(config_content, [])

    _check_oc_calls(mocker, mock_oc)


def test_mixed_style_syntax(mocker, mock_oc):
    config_content = {
        "images": [
            {"image1:tag": "docker.url/image1:sometag"},
            {"istag": "image2:tag", "from": "docker.url/image2:sometag"},
        ]
    }

    import_images(config_content, [])

    _check_oc_calls(mocker, mock_oc)


def test_conditional_images(mocker, mock_oc):
    config_content = {
        "images": [
            {"istag": "image1:tag", "from": "docker.url/image1:sometag", "envs": ["qa", "prod"]},
            {"istag": "image2:tag", "from": "docker.url/image2:sometag"},
        ]
    }
    import_images(config_content, ["prod"])

    _check_oc_calls(mocker, mock_oc)


def test_conditional_ignore_image(mocker, mock_oc):
    config_content = {
        "images": [
            {"istag": "image1:tag", "from": "docker.url/image1:sometag", "envs": ["qa", "prod"]},
            {"istag": "image2:tag", "from": "docker.url/image2:sometag"},
        ]
    }
    import_images(config_content, ["foo"])

    assert mock_oc.call_count == 1
    calls = [
        mocker.call(
            "import-image",
            "image2:tag",
            "--from=docker.url/image2:sometag",
            "--confirm",
            "--scheduled=True",
            _reraise=True,
        )
    ]
    mock_oc.assert_has_calls(calls)
