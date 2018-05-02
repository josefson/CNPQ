from lattes.pages import Preview, Curriculum, Xml
from conftest import xml_folder
import pytest


@pytest.mark.parametrize('short_id, expected_date', [
    ('K4130902J7', '25/03/2005'),
    ('K4130301E5', '28/03/2005'),
    ('K4138503E6', '07/03/2005')]
    )
def test_preview(short_id, expected_date):
    assert Preview.date(short_id) == expected_date


@pytest.mark.parametrize('short_id, long_id', [
    ('K4130902J7', '2253022128647589'),
    ('K4130301E5', '7397201484989375'),
    ('K4138503E6', '1156552473591486')]
    )
def test_curriculum(short_id, long_id):
    curriculum = Curriculum(short_id)
    assert curriculum
    assert curriculum.long_id == long_id


@pytest.mark.parametrize('long_id', [
    '2253022128647589', '7397201484989375', '1156552473591486'
    ])
def test_xml(long_id, xml_folder):
    xml = Xml(long_id, xml_folder)
    assert xml


@pytest.mark.parametrize('short_id', [None, False, '', 'Something'])
def test_curriculum_invalid_short_ids(short_id):
    if type(short_id) is not str:
        with pytest.raises(TypeError) as terror:
            Curriculum(short_id)
        assert 'ParamError' in str(terror.value)
    else:
        with pytest.raises(ValueError) as verror:
            Curriculum(short_id)
        assert 'ParamError' in str(verror.value)


@pytest.mark.parametrize('long_id', [
    None, False, '', '12345ASDF1234567'
    ])
def test_xml_invalid_long_id(long_id, xml_folder):
    if type(long_id) is not str:
        with pytest.raises(TypeError) as terror:
            Xml(long_id, xml_folder)
            assert 'ParamError' in str(terror.value)
    else:
        with pytest.raises(ValueError) as terror:
            Xml(long_id, xml_folder)
            assert 'ParamError' in str(terror.value)


@pytest.mark.parametrize('short_id', [None, False, '', 'Something'])
def test_preview_date_invalid_short_id(short_id):
    if type(short_id) is not str:
        with pytest.raises(TypeError) as terror:
            Preview.date(short_id)
            assert 'ParamError' in str(terror.value)
    else:
        with pytest.raises(ValueError) as terror:
            Preview.date(short_id)
            assert 'ParamError' in str(terror.value)
