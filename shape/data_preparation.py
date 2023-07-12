#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAPE: data wrangling
Created on Thursday August 25 2022
@author: patricia-ternes
"""
import numpy as np
import yaml
import pandas as pd
import zipfile


def geo_lookup():
    """Return geographic lookup dicts and local authority list.

    Three lookup dictionaries are generated:
    - From Postcodes to Output Areas (oacd_lookup).
    - From Output Areas to Local Authority names (ladnm_lookup).
    - From Output Areas to Local Authority codes (ladcd_lookup).

    :return: local authority list, oacd_lookup, ladnm_lookup, ladcd_lookup
    :rtype: list, dict, dict, dict
    """

    # Configure lookups from "config/lookups.yaml" file
    lookup_yaml = open("config/lookups.yaml")
    parsed_lookup = yaml.load(lookup_yaml, Loader=yaml.FullLoader)
    lookup_path = parsed_lookup.get("area_path")

    # Open file as Pandas DataFrame
    area_lookup = pd.read_csv(
        lookup_path,
        compression="zip",
        usecols=["ladnm", "ladcd", "oa11cd", "pcds"],
        encoding="unicode_escape",
        engine="python",
    )

    # Clean empty and non-England areas
    area_lookup.dropna(subset=["ladcd"], inplace=True)
    discard = ["S", "W", "N", "L", "M"]
    area_lookup = area_lookup[~area_lookup.ladcd.str.contains("|".join(discard))]
    lads = area_lookup.ladcd.unique()

    # Make lookup dictionaries
    oacd_lookup = area_lookup.set_index("pcds", drop=True).loc[:, "oa11cd"].to_dict()
    ladnm_lookup = area_lookup.set_index("oa11cd", drop=True).loc[:, "ladnm"].to_dict()
    ladcd_lookup = area_lookup.set_index("oa11cd", drop=True).loc[:, "ladcd"].to_dict()

    return lads, ladnm_lookup, ladcd_lookup, oacd_lookup


def augment(x, lookup):
    """Simple dictionary translate function to use with lambda function.

    Return a value for a given key.
    If the key is not listed in the dictionary, the function will return `None`.

    :param x: dictionary key
    :type x: Any
    :param lookup: dictionary
    :type lookup: dict
    :return: dictionary value
    :rtype: Any or empty
    """
    # This looks redundant, but ensures that the function works even for
    # missing values (returning empty code).
    try:
        return lookup[x]
    except:
        return


class Epc:
    """Class to represent the EPC data and related parameters/methods."""

    def __init__(self, oacd_lookup, ladnm_lookup, ladcd_lookup) -> None:
        """Initialise an EPC class."""

        # Configure epc api related parameters from "config/config.yaml"
        epc_yaml = open("config/config.yaml")
        parsed_epc = yaml.load(epc_yaml, Loader=yaml.FullLoader)
        self.path = parsed_epc.get("epc_path")
        self.desired_headers = parsed_epc.get("epc_headers")

        # Configure lookups
        ## Lookups from "config/lookups.yaml" file
        lookup_yaml = open("config/lookups.yaml")
        parsed_lookup = yaml.load(lookup_yaml, Loader=yaml.FullLoader)
        self.accommodation_lookup = parsed_lookup.get("accommodation")
        self.age_categorical_lookup = parsed_lookup.get("age_categorical")
        self.age_numerical_lookup = parsed_lookup.get("age_numerical")
        self.floor_area_lookup = parsed_lookup.get("floor_area")
        self.gas_lookup = parsed_lookup.get("gas")
        self.tenure_lookup = parsed_lookup.get("tenure")

        # Get EPC data as DataFrame
        self.df = self.get_epc_dataframe()

        # Set LADNM, LADCD and OA columns
        self.set_geo_lookups(oacd_lookup, ladnm_lookup, ladcd_lookup)

    def get_epc_dataframe(self) -> pd.DataFrame:
        """Get EPC data for all available England Local Authorities.

        Note 1: You need a valid EPC zipped dataset.

        Note 2: The code was organized for the following .zip tree:
        ```
        all-domestic-certificates.zip
        |__ LICENCE.txt
        |__ domestic-XYYYYYYYY-LADname
        |   |__ recommendations.csv
        |   |__ certificates.csv
        |__ domestic-XYYYYYYYY-LADname
        |    |__ recommendations.csv
        |    |__ certificates.csv
        .
        .
        .
        ```
        :return: A data frame with all England EPC collected data.
        :rtype: pandas.DataFrame
        """
        epc_zip_file = zipfile.ZipFile(self.path)  # .zip file location

        # Get the name/path of all available `certificate` files
        files = [
            text_file.filename
            for text_file in epc_zip_file.infolist()
            if text_file.filename.endswith("certificates.csv")
        ]

        # Keep just England file names, i.e. LAD codes that start with "E"
        ## Also include unknown local authority certificates, i.e.  LAD codes that start with "_"
        files = [
            folder
            for folder in files
            if folder.split("-")[1][0] == "E" or folder.split("-")[1][0] == "_"
        ]

        # Create a dataframe for every England certificate file
        dfs = [
            pd.read_csv(
                epc_zip_file.open(file), usecols=self.desired_headers, low_memory=False
            )
            for file in files
        ]

        # Return a unique EPC dataframe
        return pd.concat(dfs)

    def set_geo_lookups(self, oacd_lookup, ladnm_lookup, ladcd_lookup):
        """Add geographic information using postcode.

        1. Transform the postcode column into Output Area (new column name: "OA")
        2. Create a new column "LADNM" with the Local Authority name
        3. Create a new column "LADCD" with the Local Authority code

        :param oacd_lookup: lookup from postcode to Output Area
        :type oacd_lookup: dict
        :param ladnm_lookup: lookup from  Output Area to Local Authority name
        :type ladnm_lookup: dict
        :param ladcd_lookup: lookup from  Output Area to Local Authority code
        :type ladcd_lookup: dict
        """
        # Area: change area from postcode to output area
        self.set_categorical_code(self.df, "POSTCODE", oacd_lookup, rename="OA")

        # Create new column: Local authority name
        self.df["LADNM"] = self.df["OA"].apply(func=lambda x: augment(x, ladnm_lookup))

        # Create new column: Local authority code
        self.df["LADCD"] = self.df["OA"].apply(func=lambda x: augment(x, ladcd_lookup))

    @staticmethod
    def remove_duplicates(df) -> pd.DataFrame:
        """Remove EPC Duplicate Certificates

        When using the EPC datasets we need to be careful with duplicate EPCs
        for the same property. While not an enormous issue as an EPC is valid
        for up to 10 years unless the property is renovated or retrofitted,
        there may be multiple records especially for rental properties which are
        improved to meet recent regulations.

        This function removing duplicates with the same BUILDING REFERENCE
        NUMBER by selecting the most recent record and discarding others.

        :param df: Raw EPC dataset.
        :type df: pandas.DataFrame
        :return: EPC dataset without duplicate Certificates.
        :rtype: pandas.DataFrame
        """
        df["LODGEMENT_DATETIME"] = pd.to_datetime(df["LODGEMENT_DATETIME"])
        df = df.sort_values(by=["BUILDING_REFERENCE_NUMBER", "LODGEMENT_DATETIME"])
        df.drop_duplicates(
            subset=["BUILDING_REFERENCE_NUMBER"], keep="last", inplace=True
        )
        df.sort_index(inplace=True)
        df.reset_index(drop=True, inplace=True)
        drop_list = ["BUILDING_REFERENCE_NUMBER", "LODGEMENT_DATETIME"]
        df.drop(drop_list, axis=1, inplace=True)
        return df

    @staticmethod
    def set_categorical_code(df, df_col, lookup, rename=False):
        """Apply the lookup to a categorical column.

        Transform the values in a dataframe column using a lookup dictionary.
        This method is valid when the column values are categorical.

        :param df:  The input dataframe.
        :type df: pandas.DataFrame
        :param df_col: The column in df that represents the categorical values.
        :type df_col: string
        :param lookup: A dictionary from categorical values to categorical codes.
        :type lookup: dict
        :param rename: The new column name after transformation (if false, keep
            the current name), defaults to False.
        :type rename: bool, optional
        :return: Returns the data with the updated column.
        :rtype: pandas.DataFrame
        """

        # setting new values according the rename_dict
        df[df_col] = df[df_col].apply(func=lambda x: augment(x, lookup))

        # remove empty rows
        df.dropna(subset=[df_col], inplace=True)

        # rename column
        if rename:
            df.rename({df_col: rename}, axis=1, inplace=True)

    @staticmethod
    def set_numerical_code(df, df_col, lookup, rename=False):
        """Apply the lookup to a numerical column

        Transform the values in a dataframe column using a lookup dictionary.
        This method is valid when the column values are numerical, following
        the rule:

        if (j < value <= k), then, (value = i).

        :param df: The input dataframe.
        :type df: pandas.DataFrame
        :param df_col: The column in df that represents the numerical values.
        :type df_col: string
        :param lookup: A dictionary from numerical values to numerical codes;
            The dictionary structure is [[i1, j1, k1], [i2, j2, k2], ...,
            [iN, jN, kN]], where: iN is the desired code for band N, jN is the
            minimum value of the band N (not included), kN is the maximum value
            of the band N (included), and N is the number of bands.
        :type lookup: dict
        :param rename: The new column name after transformation (if false, keep
            the current name), defaults to False.
        :type rename: bool, optional
        """
        for band in lookup:
            df.loc[(df[df_col] > band[1]) & (df[df_col] <= band[2]), df_col] = band[0]

        # remove out bound and empty rows
        df.dropna(subset=[df_col], inplace=True)

        if rename:
            df.rename({df_col: rename}, axis=1, inplace=True)

    def set_lookups(self, df):
        """Update columns using the lookups dictionaries.

        Update the information related with `area`, `tenure`, `accommodation
        type`, `construction age band`, `main gas flag`, and `floor area`,
        by using the lookup variables (`accommodation_lookup`,
        `age_categorical_lookup`, `age_numerical_lookup`, `floor_area_lookup`,
        `gas_lookup`, `tenure_lookup`, `area_lookup`) and the
        `set_categorical_code` and `set_numerical_code` functions.

        :param df: Dataframe with EPC information.
        :type df: pandas.Dataframe
        """

        # Tenure: change the tenure from EPC to SPENSER classification
        self.set_categorical_code(df, "TENURE", self.tenure_lookup, rename="tenure")

        # Accommodation type:
        # - create an EPC accommodation type by combining "PROPERTY_TYPE" and "BUILT_FORM"
        # - change the accommodation type from EPC to SPENSER classification
        # - discard "PROPERTY_TYPE" and "BUILT_FORM" columns
        df["LC4402_C_TYPACCOM"] = df["PROPERTY_TYPE"] + ": " + df["BUILT_FORM"]
        self.set_categorical_code(df, "LC4402_C_TYPACCOM", self.accommodation_lookup)
        df.pop("PROPERTY_TYPE")
        df.pop("BUILT_FORM")

        # Construction age band:
        # - initially is a combination of categorical and numeric values
        # - convert all categorical values into absolute ages
        # - groups the absolute build age into bands
        self.set_categorical_code(
            df,
            "CONSTRUCTION_AGE_BAND",
            self.age_categorical_lookup,
            rename="ACCOM_AGE",
        )
        df["ACCOM_AGE"] = df["ACCOM_AGE"].apply(pd.to_numeric)
        self.set_numerical_code(df, "ACCOM_AGE", self.age_numerical_lookup)

        # Main gas flag: change the values (N, Y) to numerical codes
        self.set_categorical_code(df, "MAINS_GAS_FLAG", self.gas_lookup, rename="GAS")

        # Floor Area: groups the absolute area into bands
        area_max_lim = self.floor_area_lookup[-1][2]
        df.rename({"TOTAL_FLOOR_AREA": "FLOOR_AREA"}, axis=1, inplace=True)
        df.drop(df[df.FLOOR_AREA > area_max_lim].index, inplace=True)
        self.set_numerical_code(df, "FLOOR_AREA", self.floor_area_lookup)

    def step(self, df) -> pd.DataFrame:
        """EPC data preparation main step.

        This function return a processed EPC dataset by:

        1. Removing EPC Duplicate Certificates
        2. Performing variables re-categorisation

        :param df: EPC DataFrame per Local Authority
        :type df: pandas.DataFrame
        :return: processed EPC data
        :rtype: pandas.DataFrame
        """

        df = self.remove_duplicates(df)

        # Apply all lookups
        self.set_lookups(df)

        # Change selected columns to integer values
        cols = ["FLOOR_AREA", "ACCOM_AGE", "GAS", "tenure", "LC4402_C_TYPACCOM"]
        df[cols] = df[cols].applymap(np.int64)

        return df


class Spenser:
    """Class to represent the SPENSER data and related parameters/methods."""

    def __init__(self, ladnm_lookup, ladcd_lookup) -> None:
        """Initialise a Spenser class."""
        # Configure SPENSER related parameters from "config/config.yaml"
        spenser_yaml = open("config/config.yaml")
        parsed_spenser = yaml.load(spenser_yaml, Loader=yaml.FullLoader)
        self.path = parsed_spenser.get("spenser_path")
        drop_list = parsed_spenser.get("drop_list")

        # Create SPENSER dataframe
        self.df = self.get_spenser_dataframe()

        # Set Local Autority code and name columns
        self.set_geo_lookups(ladnm_lookup, ladcd_lookup)

        # Drop unnecessary columns
        self.df.drop(drop_list, axis=1, inplace=True)

        # Sort Columns: aesthetic purpose only
        column_sort = [
            "HID",
            "LADNM",
            "LADCD",
            "OA",
            "LC4402_C_TYPACCOM",
            "LC4402_C_TENHUK11",
            "LC4408_C_AHTHUK11",
            "LC4404_C_SIZHUK11",
            "LC4404_C_ROOMS",
            "LC4405EW_C_BEDROOMS",
            "LC4402_C_CENHEATHUK11",
            "LC4605_C_NSSEC",
            "LC4202_C_ETHHUK11",
            "LC4202_C_CARSNO",
        ]
        self.df = self.df[column_sort]

    def get_spenser_dataframe(self) -> pd.DataFrame:
        """Get EPC data for all available local authorities.

        Note 1: You need a valid EPC zipped dataset

        :return: A data frame with all England EPC collected data.
        :rtype: pandas.DataFrame
        """

        spenser_zip_file = zipfile.ZipFile(self.path)
        # Create a dataframe for every Household SPENSER file
        ## TIP: Household files finish with "_OA11_2020.csv"
        dfs = [
            pd.read_csv(spenser_zip_file.open(file))
            for file in spenser_zip_file.namelist()
            if file.endswith("_OA11_2020.csv")
        ]
        # Return a unique SPENSER dataframe
        return pd.concat(dfs)

    def set_geo_lookups(self, ladnm_lookup, ladcd_lookup):
        """Add geographic information using Output Area.

        1. Rename "Area" to "OA"
        2. Create a new column "LADNM" with the Local Authority name
        3. Create a new column "LADCD" with the Local Authority code

        :param ladnm_lookup: lookup from  Output Area to Local Authority name
        :type ladnm_lookup: dict
        :param ladcd_lookup: lookup from  Output Area to Local Authority code
        :type ladcd_lookup: dict
        """

        self.df.rename({"Area": "OA"}, axis=1, inplace=True)

        # Local authority name
        self.df["LADNM"] = self.df["OA"].apply(func=lambda x: augment(x, ladnm_lookup))

        # Local authority code
        self.df["LADCD"] = self.df["OA"].apply(func=lambda x: augment(x, ladcd_lookup))

    def set_new_tenure(self, df) -> pd.DataFrame:
        """Create new temporary tenure column

        This method creates a new tenure column (following EPC values) where
        the sub-categories
        - "Owned outright"(=2)
        - shared ownership" (=3)
        are merged into a general "Owner-occupied" (=1) category.

        :param df: original SPENSER data frame
        :type df: pandas.Dataframe
        :return: SPENSER data frame with a new column
        :rtype: pandas.DataFrame
        """
        df["tenure"] = df["LC4402_C_TENHUK11"].copy()
        df.loc[(df["tenure"] == 2), "tenure"] = 1
        df.loc[(df["tenure"] == 3), "tenure"] = 1

        return df

    def step(self, df) -> pd.DataFrame:
        """SPENSER data preparation main step.

        For each given local authority, this function return a processed SPENSER
        dataset by:

        1. Removing empty or non valid rows
        2. Re-categorisation of tenure to match with EPC tenure

        :param df: SPENSER DataFrame per Local Authority
        :type df: pandas.DataFrame
        :return: processed SPENSER data
        :rtype: pandas.DataFrame
        """

        # Remove "empty" rows:
        # - empty codes (here, negative values) are a problem for PSM method.
        # TODO: store the "empty" rows in other variable to be possible append
        # then at the end.
        df.drop(df[df.LC4402_C_TENHUK11 < 0].index, inplace=True)
        df.drop(df[df.LC4402_C_TYPACCOM < 0].index, inplace=True)

        # Create new tenure
        df = self.set_new_tenure(df)

        # Change selected columns to integer values
        cols = [
            "LC4402_C_TYPACCOM",
            "LC4402_C_TENHUK11",
            "LC4408_C_AHTHUK11",
            "LC4404_C_SIZHUK11",
            "LC4404_C_ROOMS",
            "LC4405EW_C_BEDROOMS",
            "LC4402_C_CENHEATHUK11",
            "LC4605_C_NSSEC",
            "LC4202_C_ETHHUK11",
            "LC4202_C_CARSNO",
            "tenure",
        ]
        df[cols] = df[cols].applymap(np.int64)

        return df
