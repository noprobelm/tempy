from ward import test
from tempy.parser import parse_rc

tempyrc_permutations = {
    "empty": {},
    "location": {"location": "nyc"},
    "location_units": {"location": "nyc", "units": "imperial"},
    "location_units_api": {
        "location": "nyc",
        "units": "imperial",
        "api_key": "jlskdjfaklejaeglkw",
    },
    "units_api": {"units": "imperial", "api_key": "jlskdjfaklejaeglkw"},
    "api": {"location": "", "units": "", "api_key": "jlskdjfaklejaeglkw"},
    "units": {"location": "", "units": "imperial", "api_key": ""},
    "location_api": {
        "location": "nyc",
        "api_key": "jlskdjfaklejaeglkw",
    },
}

for fname in tempyrc_permutations:

    @test(f"Sample tempyrc file '{fname}' parses to {tempyrc_permutations[fname]}")
    def _():
        with open(f"sample_tempyrcs/{fname}", "r") as fp:
            parsed = parse_rc(fp)
        assert parsed == tempyrc_permutations[fname]
