from setuptools import setup, find_packages
import re
import pathlib as pl


def get_version():
    filename = "__init__.py"
    with open(filename) as f:
        match = re.search(
            r"""^__version__ = ['"]([^'"]*)['"]""", f.read(), re.M
        )
    if not match:
        raise RuntimeError("{} doesn't contain __version__".format(filename))
    version = match.groups()[0]
    return version


def get_install_requires():
    path = pl.Path(__file__).parent
    path = path.joinpath("requirements.txt")
    with open(path) as f:
        content = f.read()
        content_list = content.splitlines()
        return content_list


def main():
    setup(
        name="data_validation",
        packages=["data_validation"],
        author="Joshua Ziegler",
        version=get_version(),
        description="library for parsing and validating structured data",
        install_requires=get_install_requires(),
        # url="https://github.com/Joshua-96/MVG_tracker.git",
        # package_data={"data_validation": ["sample/*.json"]},
        python_requires=">=3.6"
    )


if __name__ == "__main__":
    main()