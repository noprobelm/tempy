from tempy import config
from ward import test, raises
from pathlib import Path
import shutil
import os


@test("Valid options are 'location', 'units', 'api_key'")
def _():
    assert config.VALID_OPTIONS == ("location", "units", "api_key")


tempyrc_permutations = {
    "empty": ("", "", ""),
    "location": ("nyc", "", ""),
    "location_units": ("nyc", "imperial", ""),
    "location_units_api": ("nyc", "imperial", "jlskdjfaklejaeglkw"),
    "units_api": ("", "imperial", "jlskdjfaklejaeglkw"),
    "api": ("", "", "jlskdjfaklejaeglkw"),
    "units": ("", "imperial", ""),
    "location_api": ("nyc", "", "jlskdjfaklejaeglkw"),
}

for fname in tempyrc_permutations:

    @test(
        f"config.TempyRC will parse location={tempyrc_permutations[fname][0]}, units={tempyrc_permutations[fname][1]}, api_key={tempyrc_permutations[fname][2]}"
    )
    def _():
        tempyrc = config.TempyRC(f"sample_tempyrcs/{fname}")
        assert tempyrc_permutations[fname] == (
            tempyrc["location"],
            tempyrc["units"],
            tempyrc["api_key"],
        )


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
    "config.TempyRC will convert arg 'path' to a pathlib.Path object at the specified path"
)
def _():
    tempyrc = config.TempyRC(f"sample_tempyrcs/location")
    assert isinstance(tempyrc.path, Path)
    assert tempyrc.path == Path("sample_tempyrcs/location")


@test(
    "config.TempyRC will create a new path with a tempyrc skel if the arg 'path' does not exist"
)
def _():
    parent_path = "sample_tempyrcs/new_path"
    tempyrc_path = os.path.join(parent_path, "tempyrc")
    assert os.path.isdir(parent_path) == False

    config.TempyRC(os.path.join(parent_path, "tempyrc"))
    assert os.path.isdir(parent_path) == True
    assert os.path.isfile(tempyrc_path) == True

    shutil.rmtree(parent_path, ignore_errors=True)


@test(
    "config.TempyRC will not create a new path with a tempyrc skel if the parent path's parent does not exist (to prevent recursive mkdir)"
)
def _():
    parent_path = "sample_tempyrcs/new_path_1/new_path_2"
    tempyrc_path = os.path.join(parent_path, "tempyrc")
    assert os.path.isdir(parent_path) == False

    with raises(SystemExit) as err:
        tempyrc = config.TempyRC(os.path.join(parent_path, "tempyrc"))

    assert os.path.isdir(parent_path) == False
