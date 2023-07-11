#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAPE: Core Model
Created on Thursday August 25 2022
@author: patricia-ternes
"""

from data_preparation import Epc, Spenser, geo_lookup
from enriching_population import EnrichingPopulation
from tqdm import tqdm
from time import time

if __name__ == "__main__":
    t0 = time()

    # Get Geographic Lookup information
    print("\nSetting up Geographic Lookups ...", end="\r")
    lad_codes, ladnm_lookup, ladcd_lookup, oacd_lookup = geo_lookup()
    print("Setting up Geographic Lookups: Done")

    # Initialise the SPENSER population and related methods
    print("Setting up the SPENSER population and related methods ...", end="\r")
    spenser = Spenser(ladnm_lookup, ladcd_lookup)
    print("Setting up the SPENSER population and related methods: Done")

    # Initialise the EPC dataset and related methods
    print("Setting up the EPC data and related methods ...", end="\r")
    epc = Epc(oacd_lookup, ladnm_lookup, ladcd_lookup)
    print("Setting up the EPC data and related methods: Done")

    # Initialise the Enriching population class
    print("Setting up the Propensity Score Matching and related methods ...", end="\r")
    psm = EnrichingPopulation()
    print("Setting up the Propensity Score Matching and related methods: Done")

    # Create history variables
    list_SHAPE = []
    list_SHAPE_names = []
    list_EPC = []
    list_EPC_names = []
    error_lad = []

    print("Starting main loop")
    for lad_code in tqdm(lad_codes):
        try:
            # SPENSER and EPC per Local Authority
            epc_lad_df = epc.df.loc[epc.df.LADCD == lad_code].reset_index(drop=True)
            spenser_lad_df = spenser.df.loc[spenser.df.LADCD == lad_code].reset_index(
                drop=True
            )

            # SPENSER and EPC data preparation main steps.
            epc_lad_df = epc.step(epc_lad_df)
            spenser_lad_df = spenser.step(spenser_lad_df)

            # Combine SPENSER and EPC to get an Enriched Population
            rich_df = psm.step(spenser_lad_df, epc_lad_df)

            # Store Enriched Population
            list_SHAPE_names.append("_".join([lad_code, "_SHAPE.csv"]))
            list_SHAPE.append(rich_df)

            # Store processed EPC
            list_EPC_names.append("_".join([lad_code, "_EPC.csv"]))
            list_EPC.append(epc_lad_df)

        except:
            error_lad.append(lad_code)

    print('Saving Outputs in "data/output/" ...', end="\r")
    # Save Enriched Population (SHAPE)
    psm.save_csv_files(list_SHAPE_names, list_SHAPE, "SHAPE_England.zip")
    # Save Processed EPC
    psm.save_csv_files(list_EPC_names, list_EPC, "EPC_England.zip")
    # Save Distribution Images
    psm.save_validation_fig(list_SHAPE, list_EPC)
    # Save list of missing Local Authorities
    with open("data/output/error_log.txt", "w") as outfile:
        outfile.write("\n".join(error_lad))
    print('Saving Outputs in "data/output/": Done')

    print("Total run time {} seconds".format(int(time() - t0)))
