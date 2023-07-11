import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shape-population",
    version="0.1.0",
    author="Patricia Ternes",
    author_email="p.ternesdallagnollo@leeds.ac.uk",
    description="The SHAPE Population package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.9",
)
