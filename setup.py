from setuptools import setup, find_packages # pyright: ignore[reportMissingModuleSource]

setup(
    name="vbmcp",
    version="0.1",
    packages=find_packages(exclude=["tests"]),
    test_suite="tests",
)
