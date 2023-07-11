Setup
=====

This project currently supports running on Linux.

To start working with this repository you need to clone it onto your local
machine: ::

    $ git clone https://github.com/patricia-ternes/shape.git
    $ cd shape


The easiest way to configure the correct requirements is by using a
`conda <https://docs.anaconda.com/anaconda/install/>`_ environment.
You can create an environment for this project using the provided
environment file: ::

    $ conda env create -f environment.yml
    $ conda activate shape

Next we install the SHAPE package into the environment using `setup.py`: ::

    $ python setup.py install

Running the model
-----------------

To run the model type: ::

    $ python shape-population


The above command will run the package as defined in the
main file (``shape/__main__.py``). If you want to create a personalised script, you
can import the modules as follows: ::

    from shape import Epc, Spenser, geo_lookup, EnrichingPopulation

