Required Datasets
=================

Before run the model you need to download some datasets:

- Domestic Energy Performance Certificates (EPCs)
- SPENSER England Household Population
- Geographic Lookup in the UK

All input datasets should be stored in the input data folder (``data/input/``).

EPCs Data
--------------------

Energy Performance Certificates (EPCs) are a rating scheme to summarise the
energy efficiency of buildings. An EPC also includes several information
related with the accommodation.

`You can register and download the UK EPC data here
<https://epc.opendatacommunities.org/#register>`_.

EPC variables
^^^^^^^^^^^^^^^^^^^^

The EPC data provides information about a few dozen variables.

`You can find the complete EPC Glossary here 
<https://epc.opendatacommunities.org/docs/guidance#glossary>`_.

In this package we select the following variables:

- ``POSTCODE``: The postcode of the property.
- ``PROPERTY_TYPE``: Describes the type of property such as House, Flat, Maisonette etc.
- ``BUILT_FORM``: The building type of the Property e.g. Detached, Semi-Detached, Terrace etc.
- ``CONSTRUCTION_AGE_BAND``: Age band when building part constructed.
- ``TENURE``: Describes the tenure type of the property.
- ``TOTAL_FLOOR_AREA``: Total Useful Floor Area (m²).
- ``MAINS_GAS_FLAG``: Whether mains gas is available.
- ``BUILDING_REFERENCE_NUMBER``: Unique identifier for the property.
- ``LODGEMENT_DATETIME``: Date and time lodged on the Energy Performance of Buildings Register.

This variables are listed in a configuration file (``./config/config.yaml``).

EPC variables lookup
^^^^^^^^^^^^^^^^^^^^

Most of the original EPC information is unencoded. During the package execution
most information are properly encoded and organised. You can find all the
encoding tables in the lookup file (``./config/lookups.yaml``).

*Note: the EPC certificates are filled in by hand and it is possible to find
several typos or different descriptions for the same thing.
This makes the encoding process very difficult.*

The encode tables include all terms found in certificates issued up to and
including *31 March 2022*.

SPENSER Data
--------------------

The SPENSER (Synthetic Population Estimation and Scenario Projection Model) uses
Iterative Proportional Fitting (IPF) to create two synthetic populations: one of
individuals (at Middle Layer Super Output Area (MSOA) level) and other of
households (at Output Area (OA) level). Both use the 2011 Census Data. The
population of individuals/households are evolved in time using a dynamic
microsimulation model, and finally, individuals are linked to households. Each
SPENSER Household has information related to accommodation type, tenure,
household type/size, number of rooms/bedrooms, central heating availability,
NS-SEC and Ethnic group of Household Reference Person.

You can find a SPENSER population
`here <https://osf.io/623qz>_`.

Geographic Lookup
--------------------

To combine EPC and SPENSER data we first need to guarantee that the datasets
have compatible area granularity.

Initially the datasets have the following granularities:

- EPC: organised by postcode and Local Authority
- SPENSER: organised by output area and Local Authority

*Note: Although the two datasets have local authority information, they are not
compatible.*

Therefore, to ensure local compatibility, we use a lookup table to recategorize
both EPC and SPENSER area related information.
You can find a Geographic Lookup table
`here <https://geoportal.statistics.gov.uk/datasets/postcode-to-output-area-to-lower-layer-super-output-area-to-middle-layer-super-output-area-to-local-authority-district-february-2022-lookup-in-the-uk/about>`_.
