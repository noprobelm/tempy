from tempy import config
from ward import test, raises


@test("Config will instantiate with no command line arguments")
def _():
    tempyrc_path = "sample_tempyrcs/location_units_api"

    unparsed = []
    tempy_config = config.Config(tempyrc_path, unparsed)
    assert isinstance(tempy_config, config.Config)


@test("A valid config.TempyRC was parsed")
def _():
    tempyrc_path = "sample_tempyrcs/location_units_api"

    tempy_config = config.Config(tempyrc_path)
    assert all(key in tempy_config._tempyrc for key in config.VALID_OPTIONS)


@test("A valid config.Args was parsed")
def _():
    unparsed = ["nyc"]

    tempy_config = config.Config(unparsed=unparsed)
    assert all(key in tempy_config._args for key in config.VALID_OPTIONS)


@test("Command line arguments take priority over tempyrc (if it exists in tempyrc)")
def _():
    tempyrc_path = "sample_tempyrcs/location_units_api"
    tempyrc = config.TempyRC(tempyrc_path)
    unparsed = ["beijing", "--units", "metric"]

    tempy_config = config.Config(tempyrc_path, unparsed)

    # Args take priority
    assert tempy_config["location"] == "beijing"
    # Args take priority
    assert tempy_config["units"] == "metric"

    # Missing args for api_key, so tempyrc takes priority
    assert tempy_config["api_key"] == tempyrc["api_key"]


@test("Tempy terminates if no location is found in tempyrc or command line args")
def _():
    tempyrc_path = "sample_tempyrcs/empty"
    unparsed = []

    with raises(SystemExit):
        tempy_config = config.Config(tempyrc_path, unparsed)


@test("Config will set 'units' default to 'imperial' if no units are specified")
def _():
    tempyrc_path = "sample_tempyrcs/location"
    unparsed = []

    tempy_config = config.Config(tempyrc_path, unparsed)

    assert tempy_config["units"] == "imperial"
