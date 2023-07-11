# SHAPE Documentation

This documentation is built with `sphinx`.

## Setup Steps

1. Install Package and theme:
   - sphinx=4.4.0
   - sphinx_rtd_theme=0.4.3
2. Start the basic structure inside the `docs` folder using: `$ sphinx-quickstart docs`
3. Use the apidoc: `$ sphinx-apidoc -o docs .`
4. Configure some files:
   - conf.py:
     - add the `src` folder as path:

       ```python
         import os
         import sys
         sys.path.insert(0, os.path.abspath('../src'))
       ```

     - add extentions: `'sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc'`.
     - change theme: `sphinx_rtd_theme`
   - Create and populate files.

## Build locally

1. `$ make clean html`: clean old build
2. `$ make html`: build new site

You can find the built website in `docs/_build/html/index.html`
