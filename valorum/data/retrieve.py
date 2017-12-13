"""
This file is used to retrieve various datasets.

"""
import io
import pandas as pd
from .config import setup_logger
from .loader import load
from .bls import BLSData

LOGGER = setup_logger(__name__)


def _retrieve_test():
    df = pd.DataFrame({"A": [0, 1, 2],
                       "B": [3, 4, 5],
                       "C": [6, 7, 8]})

    return df


def _retrieve_state_fips():
    src = io.StringIO("""FIPS,Abbreviation,Name
    2,AK,Alaska
    28,MS,Mississippi
    1,AL,Alabama
    30,MT,Montana
    5,AR,Arkansas
    37,NC,North Carolina
    38,ND,North Dakota
    4,AZ,Arizona
    31,NE,Nebraska
    6,CA,California
    33,NH,New Hampshire
    8,CO,Colorado
    34,NJ,New jersey
    9,CT,Connecticut
    35,NM,New Mexico
    32,NV,Nevada
    10,DE,Delaware
    36,NY,New York
    12,FL,Florida
    39,OH,Ohio
    13,GA,Georgia
    40,OK,Oklahoma
    41,OR,Oregon
    15,HI,Hawaii
    42,PA,Pennsylvania
    19,IA,Iowa
    16,ID,Idaho
    44,RI,Rhode island
    17,IL,Illinois
    45,SC,South Carolina
    18,IN,Indiana
    46,SD,South Dakota
    20,KS,Kansas
    47,TN,Tennessee
    21,KY,Kentucky
    48,TX,Texas
    22,LA,Louisiana
    49,UT,Utah
    25,MA,Massachusetts
    51,VA,Virginia
    24,MD,Maryland
    23,ME,Maine
    50,VT,Vermont
    26,MI,Michigan
    53,WA,Washington
    27,MN,Minnesota
    55,WI,Wisconsin
    29,MO,Missouri
    54,WV,West Virginia
    56,WY,Wyoming
    """)
    return pd.read_csv(src)


def _retrieve_state_employment():
    b = BLSData()

    states = load("state_fips")

    dfs = []
    for state_fips in states["FIPS"]:
        code = str(state_fips).zfill(2)
        codes = [
            f"LASST{code}0000000000003",
            f"LASST{code}0000000000006",
        ]
        LOGGER.debug(f"Querying bls for {codes}")
        df = b.get(codes, startyear=2000, endyear=2017, nice_names=False)
        df["state"] = states.loc[states.FIPS == state_fips, "Name"].iloc[0]
        df.loc[df["variable"].str[-1] == "3", "variable"] = "UnemploymentRate"
        df.loc[df["variable"].str[-1] == "6", "variable"] = "LaborForce"
        df.set_index(["Date", "state", "variable"], inplace=True)
        df = df.unstack(level="variable")["value"]
        dfs.append(df)

    return pd.concat(dfs).sort_index()


def _retrieve_state_industry_employment():
    b = BLSData()

    states = load("state_fips")

    def get_codes(state_fips):
        code = str(state_fips).zfill(2)
        return {
            # f"SMS{code}000000000000001": "total",
            f"SMS{code}000001000000001": "mining and logging",
            f"SMS{code}000002000000001": "construction",
            f"SMS{code}000003000000001": "manufacturing",
            f"SMS{code}000004000000001": "trade, transportation and utilities",
            f"SMS{code}000005000000001": "information",
            f"SMS{code}000005500000001": "financial activities",
            f"SMS{code}000006000000001": "professional and business services",
            f"SMS{code}000006561000001": "education",
            f"SMS{code}000006562000001": "healthcare",
            f"SMS{code}000007000000001": "leisure and hospitality",
            f"SMS{code}000008000000001": "other services",
            f"SMS{code}000009000000001": "government"
        }

    dfs = []
    for state_fips in states["FIPS"]:
        codes = get_codes(state_fips)
        LOGGER.debug(f"Querying bls for {codes}")
        df = b.get(
            list(codes.keys()), startyear=2000, endyear=2017,
            nice_names=False
        )
        df.replace({"variable": codes}, inplace=True)
        df["state"] = states.loc[states.FIPS == state_fips, "Name"].iloc[0]
        df.set_index(["Date", "state", "variable"], inplace=True)
        df = df.unstack(level="variable")["value"]
        dfs.append(df)

    return pd.concat(dfs).sort_index()
