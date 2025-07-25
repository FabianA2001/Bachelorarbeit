from setuptools import find_packages
from skbuild_conan import setup

setup(  # https://scikit-build.readthedocs.io/en/latest/usage.html#setup-options
    name="degree-constrained-triangulation",
    version="0.1.14",
    packages=find_packages("src"),  # Include all packages in `./src`.
    package_dir={"": "src"},  # The root for our python package is in `./src`.
    python_requires=">=3.7",  # lowest python version supported.
    install_requires=[
        "matplotlib",
        "networkx",
        "ortools",
        "shapely",
        "scipy",
        "seaborn",
        "python-sat",
        "algbench",
        "pytest",
        "scalene",
        "streamlit",
        "gurobipy",
        "slurminade",
    ],  # Python Dependencies
    conan_requirements=["cgal/[>=6.0.1]"],  # C++ Dependencies
    cmake_minimum_required_version="3.23",
)
