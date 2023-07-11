#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAPE: PSM step
Created on Thursday August 25 2022
@author: patricia-ternes
"""
from random import choices
import zipfile
from causalinference import CausalModel
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import yaml
import seaborn as sns
import matplotlib.pyplot as plt
import os
import io
from matplotlib.ticker import MaxNLocator


class EnrichingPopulation:
    """Class to enrich a synthetic population.

    To create a enriched synthetic population, this class combines two
    pandas.DataFrames using the Propensity Score Matching approach.
    """

    def __init__(self) -> None:
        """Initialise an EnrichingPopulation class."""
        # Configure PSM related parameters from "config/config.yaml"
        psm_yaml = open("config/config.yaml")
        parsed_psm = yaml.load(psm_yaml, Loader=yaml.FullLoader)
        self.n_neighbors = parsed_psm.get("n_neighbors")
        self.overlap_columns = parsed_psm.get("overlap_columns")
        self.matches_columns = parsed_psm.get("matches_columns")

    @staticmethod
    def set_treatment(df0, df1):
        """Create a "Treatment" column in each dataframe.

        :param df0: SPENSER dataset
        :type df0: pandas.DataFrame
        :param df1: EPC dataset
        :type df1: pandas.DataFrame
        :return: Two dataframes, first the SPENSER data + new column
            ("Treatment" = 0), second the EPC data + new column ("Treatment" = 1)
        :rtype: pandas.DataFrame, pandas.DataFrame
        """

        df0["Treatment"] = 0
        df1["Treatment"] = 1

        return df0, df1

    @staticmethod
    def set_area_factor(df) -> pd.DataFrame:
        """Add a new `Area_factor` column by factorizing the OA codes.

        This step transform O
        :param df: Dataset with a OA column.
        :type df: pandas.DataFrame
        :return: Input dataset + new factorized Area column
        :rtype: pandas.DataFrame
        """
        Area_factor = df.OA.factorize()
        df["Area_factor"] = Area_factor[0]

        return df

    @staticmethod
    def get_propensity_score(df, overlap_columns):
        """Return the propensity score values.

        :param df: complete dataframe
        :type df: pandas.DataFrame
        :param overlap_columns: list of columns names that are present in both
            datasets (EPC and SPENSER).
        :type overlap_columns: list
        :return: list of propensity score for all rows.
        :rtype: numpy.ndarray
        """

        ## Isolate the Y, X and the covariates
        Y = df["Treatment"].copy()  # 1-Dimension outcome - arbitrary values
        X = df["Treatment"].copy()  # 1-Dimension treatment
        C = df[overlap_columns].copy()  # n-Dimension covariates

        # Transform pandas dataframe into numpy.ndarray (CausalModel requisite)
        Y = Y.values
        X = X.values
        C = C.values

        # Create the Causal Model
        model = CausalModel(Y, X, C)

        # Propensity score calculation
        model.est_propensity_s()
        return model.propensity["fitted"]

    @staticmethod
    def get_neighbors(df1, df2, n_neighbors):
        """For each SPENSER row get a list of EPC rows with the closest propensity score values.

        :param df1: SPENSER dataset
        :type df1: pandas.DataFrame
        :param df2: EPC dataset
        :type df2: pandas.DataFrame
        :param n_neighbors: Number of neighbors.
        :type n_neighbors: integer
        :return: The propensity score difference and the indices of the closest neighbors.
        :rtype: list, list
        """
        # create the neighbors object (p=2 means Euclidean distance)
        knn = NearestNeighbors(n_neighbors=n_neighbors, p=2).fit(df2[["ps"]])

        # for each household in df1 dataframe, find the nearest df2 neighbors
        distances, indices = knn.kneighbors(df1[["ps"]])
        return distances, indices

    @staticmethod
    def get_matches(distances, indices, n_neighbors):
        """From the neighbors list get one match for each SPENSER row.

        EPC rows with the same propensity score value have the same probability
        of being matched with a SPENSER row. The greater the difference between
        the propensity score values, the lower the probability of being drawn.
        The weight function used, is a step function.

        :param distances: List of propensity score difference between the closest neighbors.
        :type distances: list
        :param indices: List of the closest neighbors indices.
        :type indices: list
        :param n_neighbors: Number of neighbors.
        :type n_neighbors: integer
        :return: List of assigned pairs.
        :rtype: list
        """
        pairs = []
        for index1, candidates2 in enumerate(indices):
            is_zero = np.flatnonzero(distances[index1] == 0)
            if is_zero.size < n_neighbors:
                weight = 100 - (distances[index1] / distances[index1][-1] * 95)
                index2 = choices(candidates2, weights=weight)[0]
            else:
                index2 = choices(candidates2)[0]
            pairs.append([index1, index2])

        return pairs

    @staticmethod
    def get_enriched_pop(pairs, df1, df2, matches_columns):
        """Returns the SPENSER enriched population.

        Combine the EPC data with the SPENSER data to generated a enriched
        synthetic population. To combine the datasets, the propensity score
        matching method is used.

        :param pairs: List of assigned pairs.
        :type pairs: list
        :param df1: SPENSER dataset.
        :type df1: pandas.DataFrame
        :param df2: EPC dataset.
        :type df2: pandas.DataFrame
        :param matches_columns: List of columns name from EPC to be incorporated
            into SPENSER dataset.
        :type matches_columns: list
        :return: The enriched synthetic population
        :rtype: pandas.DataFrame
        """
        # Add matched df2 index id in df1 dataframe
        matches = pd.DataFrame(pairs)
        df1["EPCid"] = matches[1]

        drop_list = [
            "tenure",
            "ps",
            "Treatment",
            "Area_factor",
            *matches_columns,
        ]
        df1.drop(drop_list, axis=1, inplace=True)

        df2 = df2[matches_columns].copy()
        df2["EPCid"] = df2.index

        df1 = pd.merge(df1, df2, on="EPCid", how="left")
        df1.drop(["EPCid"], axis=1, inplace=True)

        return df1

    @staticmethod
    def save_csv_files(list_df_names, list_df, zip_name):
        """Save pandas.DataFrames as `.csv` files compressed in a `.zip` file.

        Save the dataset into a zip file.
        Each local authority is stored in a different csv file.

        :param list_df_names: Names of each csv file.
        :type list_df_names: list
        :param list_df: List of pandas.DataFrames.
        :type list_df: list
        :param zip_name: Desired name to store the zipped .csv files
        :type zip_name: string
        """
        save_dir = "data/output/"
        if not (os.path.exists(save_dir)):
            os.makedirs(save_dir)

        # save final population
        with zipfile.ZipFile(os.path.join(save_dir, zip_name), "w") as csv_zip:
            for i in range(len(list_df_names)):
                csv_zip.writestr(
                    list_df_names[i], list_df[i].to_csv(index=False, header=True)
                )

    @staticmethod
    def save_validation_fig(SHAPE, EPC):
        """Save the internal validation image.

        Floor Area distribution and Accommodation age codes distribution
        comparison between original EPC data and SHAPE population.

        :param df1: SHAPE dataset list.
        :type df1: list of pandas.DataFrame
        :param df2: EPC dataset list.
        :type df2: list of pandas.DataFrame
        """
        bins1 = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            [0, 1, 2],
        ]

        constraints = ["ACCOM_AGE", "FLOOR_AREA", "GAS"]
        xlabels = ["Accommodation age", "Floor area", "Gas Availability"]

        colours = sns.color_palette()

        save_dir = "data/output/"
        if not (os.path.exists(save_dir)):
            os.makedirs(save_dir)

        zip_png_name = os.path.join(save_dir, "SHAPE_distribution-images.zip")
        with zipfile.ZipFile(zip_png_name, "w") as png_zip:
            for i in range(len(SHAPE)):
                df1 = EPC[i]
                df2 = SHAPE[i]

                j = 0
                sns.set(color_codes=True)
                fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(16, 15))
                for constraint in constraints:

                    y_epc = (
                        df1[constraint]
                        .value_counts(bins=bins1[j], normalize=True)
                        .sort_index()
                    )
                    y_msm = (
                        df2[constraint]
                        .value_counts(bins=bins1[j], normalize=True)
                        .sort_index()
                    )

                    sns.barplot(ax=ax[j][0], x=bins1[j][1:], y=y_epc, color=colours[0])
                    sns.barplot(ax=ax[j][1], x=bins1[j][1:], y=y_msm, color=colours[3])

                    for k in range(2):
                        ax[j][k].set_xlabel(xlabels[j])
                        ax[j][k].set_ylabel("Frequency")

                    j = j + 1

                ax[0][0].set_title("EPC")
                ax[0][1].set_title("SHAPE")
                fig.tight_layout(pad=3.0)
                buf = io.BytesIO()
                plt.savefig(buf)
                plt.close()

                lad_name = df2.LADNM[0]
                lad_code = df2.LADCD[0]
                fig_name = "_".join([lad_code, lad_name, "distribution.png"])
                png_zip.writestr(fig_name, buf.getvalue())

    def step(self, df0, df1):
        """Enriching population main step.

        In this step the EPC data and the SPENSER data are combined to generate
        an enriched synthetic population for a given local authority.

        :param df0: SPENSER dataset.
        :type df0: pandas.DataFrame
        :param df1: EPC dataset.
        :type df1: pandas.DataFrame
        :param lad_code: Local authority district code.
        :type lad_code: string
        :param psm_fig: Boolean to save the propensity score distribution image, defaults to True.
        :type psm_fig: bool, optional
        :param validation_fig: Boolean to save the internal validation image, defaults to True.
        :type validation_fig: bool, optional
        :return: Enriched synthetic population
        :rtype: pandas.DataFrame
        """
        df0, df1 = self.set_treatment(df0, df1)
        dataset = pd.concat([df0, df1], ignore_index=True, sort=False)
        dataset = self.set_area_factor(dataset)
        dataset["ps"] = self.get_propensity_score(dataset, self.overlap_columns)

        # Separating EPC data from MSM data
        df0 = dataset.loc[dataset.Treatment == 0].reset_index(drop=True)
        df1 = dataset.loc[dataset.Treatment == 1].reset_index(drop=True)
        del dataset

        # Get neighbors and matched pairs
        distances, indices = self.get_neighbors(df0, df1, self.n_neighbors)
        pairs = self.get_matches(distances, indices, self.n_neighbors)
        del distances, indices

        # Get enriched population
        rich_df = self.get_enriched_pop(pairs, df0, df1, self.matches_columns)

        return rich_df
