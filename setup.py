from setuptools import setup, find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="deltame",
    version="0.1.0",
    license="MIT",
    description="Physiological Modeling Framework",

    author="Satoshi Koyama@Delta Mex Inc.",
    url="https://www.delta-mex.com/",

    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,

    install_requires=_requires_from_file("requirements.txt"),
    tests_require=["pytest"],
)
