from setuptools import find_packages, setup

setup(
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
)
