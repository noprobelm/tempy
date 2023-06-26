from tempy import config
from ward import test

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
