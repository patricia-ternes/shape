# SHAPE

The **Synthetic Household/Accommodation Population for Energy (SHAPE)** is an
enriched synthetic population of households, obtained by combining the SPENSER
household population with accommodation-related information available from the
Domestic Energy Performance Certificates (EPC) data, namely:

- Accommodation floor area (band)
- Accommodation age (band)
- Gas (flag: Y/N)

To enrich the SPENSER population with the EPC data, the Propensity Score
Matching (PSM) technique with a kernel density algorithm was used.

In this repository you can find the package that we we create/use to generate
the SHAPE population.

## Population Download

If you want use the synthetic population itself, you can download the complete
dataset via the CDRC repository,
[here](https://data.cdrc.ac.uk/dataset/synthetic-householdaccommodation-population-energy-shape).

## Environment setup

To start working with this repository you need to clone it onto your local
machine:

```bash
$ git clone https://github.com/patricia-ternes/shape.git
$ cd shape
```

### Requirements

This package currently supports running on Linux,  <!-- and macOS. -->
and was built using the following dependences:

- causalinference==0.1.3
- matplotlib=3.5.1
- numpy=1.21.2
- pandas=1.4.1
- python=3.9.7
- pyyaml=6.0
- scikit-learn=1.0.2
- seaborn=0.11.2
- setuptools=58.0.4
- tqdm==4.63.0

The easiest way to configure the correct requirements is by using a
[conda](https://docs.anaconda.com/anaconda/install/) environment.
You can create an environment for this project using the provided
environment file:

```bash
$ conda env create -f environment.yml
$ conda activate shape
```

## Installation & Usage

Next we install the SHAPE package into the environment using `setup.py`:

```bash
$ python setup.py install
```

To run the model type:

```bash
$ python shape-population
```

The above command will run the package as defined in the
[main file](shape/__main__.py). If you want to create a personalised script, you
can import the modules as follows:

```python
from shape import Epc, Spenser, geo_lookup, EnrichingPopulation
```

## Required Datasets

Before run the model you need to download some datasets:

- Domestic Energy Performance Certificates (EPCs)
- SPENSER England Household Population
- Geographic Lookup in the UK

All input datasets should be stored in the [`input data`](data/input/) folder.

### EPCs Data

Energy Performance Certificates (EPCs) are a rating scheme to summarise the
energy efficiency of buildings. An EPC also includes several information
related with the accommodation.

You can register and download the UK EPC data
[here](https://epc.opendatacommunities.org/#register).

#### EPC variables

The EPC data provides information about a few dozen variables.
You can find the complete EPC Glossary
[here](https://epc.opendatacommunities.org/docs/guidance#glossary).

In this package we select the following variables:

- `POSTCODE`: The postcode of the property.
- `PROPERTY_TYPE`: Describes the type of property such as House, Flat, Maisonette etc.
- `BUILT_FORM`: The building type of the Property e.g. Detached, Semi-Detached, Terrace etc.
- `CONSTRUCTION_AGE_BAND`: Age band when building part constructed.
- `TENURE`: Describes the tenure type of the property.
- `TOTAL_FLOOR_AREA`: Total Useful Floor Area (m²).
- `MAINS_GAS_FLAG`: Whether mains gas is available.
- `BUILDING_REFERENCE_NUMBER`: Unique identifier for the property.
- `LODGEMENT_DATETIME`: Date and time lodged on the Energy Performance of Buildings Register.

This variables are listed in a [configuration file](./config/config.yaml).

#### EPC variables lookup

Most of the original EPC information is unencoded. During the package execution
most information are properly encoded and organised. You can find all the
encoding tables in the [lookup file](./config/lookups.yaml).

*Note: the EPC certificates are filled in by hand and it is possible to find
several typos or different descriptions for the same thing.
This makes the encoding process very difficult.*

The encode tables include all terms found in certificates issued up to and
including *31 March 2022*.

### SPENSER Data

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
[here](https://osf.io/623qz).

### Geographic Lookup

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
[here](https://geoportal.statistics.gov.uk/datasets/postcode-to-output-area-to-lower-layer-super-output-area-to-middle-layer-super-output-area-to-local-authority-district-february-2022-lookup-in-the-uk/about).

## Outputs

The package provide four different outputs that are stored in
[`output data`](data/output/) folder:

1. Enriched Population (SHAPE)
2. Log of Missing Local Authorities
3. Processed EPC (useful for validation)
4. Distribution Images (useful for validation)

<!-- ## Develop packages

- pytest=6.2.5
- black=19.10b0
- sphinx=4.4.0
- sphinx_rtd_theme=0.4.3


## Documentation with sphinx

1. Create the docs folder: `$ sphinx-quickstart docs`
2. Use the apidoc: `$ sphinx-apidoc -o docs activity_model/`
3. Configure some files:
   - conf.py:
     - uncomment: `import os`, `import sys`, and `sys.path.insert(0, os.path.abspath("../.."))`.
     - add extentions: `sphinx.ext.autodoc`,`sphinx.ext.napoleon` , and `sphinx.ext.viewcode`.
     - change theme: `sphinx_rtd_theme`
   - index.rst:
     - `.. include:: ../activity_model.rst`
4. `$ make clean html`
5. `$ make html` -->
