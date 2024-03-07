from tempy import config
from ward import test, raises


@test("Command line arguments take priority over tempyrc (if it exists in tempyrc)")
def _():
    tempyrc = config.TempyRC("sample_tempyrcs/location_units_api")
    args = config.Args(["beijing", "--units", "metric"])

    tempy_config = config.Config(tempyrc, args)

    # Args take priority
    assert tempy_config["location"] == "beijing"
    # Args take priority
    assert tempy_config["units"] == "metric"

    # Missing args for api_key, so tempyrc takes priority
    assert tempy_config["api_key"] == tempyrc["api_key"]


@test("Tempy terminates if no location is found in tempyrc or command line args")
def _():
    tempyrc = config.TempyRC("sample_tempyrcs/empty")
    args = config.Args([])

    with raises(SystemExit):
        config.Config(tempyrc, args)
