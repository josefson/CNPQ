import pytest


@pytest.fixture
def xml_folder(request):
    from pathlib import Path
    tmp_dir = '/tmp/xmls/'
    path = Path(tmp_dir)
    if not path.exists():
        path.mkdir()

    def tearDown():
        for xml in path.iterdir():
            xml.unlink()
        if path.exists():
            path.rmdir()
    request.addfinalizer(tearDown)
    return path
