from tempy import config
from ward import test, raises
from pathlib import Path
import shutil
import os


@test("Valid options are 'location', 'units', 'api_key'")
def _():
    assert config.VALID_OPTIONS == ("location", "units", "api_key")


@test("config.TempyRC will ignore invalid config options")
def _():
    tempyrc = config.TempyRC("sample_tempyrcs/invalid")
    assert "invalid" not in tempyrc.keys()


@test("config.TempyRC will ignore commented lines")
def _():
    tempyrc = config.TempyRC("sample_tempyrcs/commented")
    assert tempyrc == {
        "location": "",
        "units": "imperial",
        "api_key": "jlskdjfaklejaeglkw",
    }


@test(
    "config.TempyRC will create a new path with a tempyrc skel if the arg 'path' does not exist"
)
def _():
    parent_path = os.path.join(Path(__file__).parent, "sample_tempyrcs/new_path")
    tempyrc_path = os.path.join(parent_path, "tempyrc")
    assert os.path.isdir(parent_path) == False

    config.TempyRC(tempyrc_path)
    assert os.path.isdir(parent_path) == True
    assert os.path.isfile(tempyrc_path) == True

    shutil.rmtree(parent_path, ignore_errors=True)


@test(
    "config.TempyRC will not create a new path with a tempyrc skel if the parent path's parent does not exist (to prevent recursive mkdir)"
)
def _():
    parent_path = os.path.join(
        Path(__file__).parent, "sample_tempyrcs/new_path_1/new_path_2"
    )
    tempyrc_path = os.path.join(parent_path, "tempyrc")
    assert os.path.isdir(parent_path) == False

    with raises(SystemExit) as err:
        config.TempyRC(tempyrc_path)

    assert os.path.isdir(parent_path) == False
