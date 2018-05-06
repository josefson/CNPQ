from lattes.pages import Preview, Curriculum, Xml
from fake_useragent import UserAgent
import tempfile
import pytest

UA = UserAgent()


@pytest.mark.parametrize('short_id, expected_date', [
    ('K4130902J7', '25/03/2005'),
    ('K4130301E5', '28/03/2005'),
    ('K4138503E6', '07/03/2005')]
    )
def test_preview(short_id, expected_date):
    assert Preview.date(short_id) == expected_date


@pytest.mark.parametrize('short_id, user_agent, long_id', [
    ('K4130902J7', None, '2253022128647589'),
    ('K4130902J7', UA.random, '2253022128647589'),
    ('K4130301E5', None, '7397201484989375'),
    ('K4130301E5', UA.random, '7397201484989375'),
    ('K4138503E6', None, '1156552473591486')]
    )
def test_curriculum(short_id, user_agent, long_id):
    curriculum = Curriculum(short_id, user_agent=user_agent)
    assert curriculum
    assert curriculum.long_id == long_id


@pytest.mark.parametrize('long_id, user_agent', [
    ('2253022128647589', None),
    ('7397201484989375', None),
    ('1156552473591486', None),
    ('2253022128647589', UA.random),
    ('7397201484989375', UA.random),
    ('1156552473591486', UA.random)]
    )
def test_xml(long_id, user_agent):
    with tempfile.TemporaryDirectory() as temp_dir:
        xml = Xml(long_id, temp_dir, user_agent=user_agent)
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
def test_xml_invalid_long_id(long_id):
    if type(long_id) is not str:
        with pytest.raises(TypeError) as terror:
            with tempfile.TemporaryDirectory() as temp_dir:
                Xml(long_id, temp_dir)
            assert 'ParamError' in str(terror.value)
    else:
        with pytest.raises(ValueError) as terror:
            with tempfile.TemporaryDirectory() as temp_dir:
                Xml(long_id, temp_dir)
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
