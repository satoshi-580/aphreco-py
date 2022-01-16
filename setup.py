from setuptools import find_packages, setup


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="aphreco",
    version="0.1.0",
    license="MIT",
    description="Small-Scale Physiological Modeling Framework",
    author="Aphreco-Lab",
    url="https://aphreco.com/",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=_requires_from_file("requirements.txt"),
    tests_require=["pytest"],
)
