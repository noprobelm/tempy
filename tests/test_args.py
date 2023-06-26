from tempy import config
from ward import test, raises


@test("config.Args accepts any number of arguments for location")
def _():
    unparsed = []
    args = config.Args(unparsed)
    assert args["location"] == ""

    unparsed = ["nyc"]
    args = config.Args(unparsed)
    assert args["location"] == "nyc"

    unparsed = ["new york city"]
    args = config.Args(unparsed)
    assert args["location"] == "new york city"


@test("config.Args will only accept 'metric' or 'imperial' for --units")
def _():
    unparsed = ["--units", "lkf"]
    with raises(SystemExit) as err:
        args = config.Args(unparsed)

    unparsed = ["--units", "imperial"]
    args = config.Args(unparsed)
    assert args["units"] == "imperial"

    unparsed = ["--units", "metric"]
    args = config.Args(unparsed)
    assert args["units"] == "metric"
