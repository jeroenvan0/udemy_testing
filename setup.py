from setuptools import setup, find_packages

with open ("requirement.txt") as f:
    requirements = f.read().splitlines()

setup(
    name = "ML-OPS-PROJECT1",
    version="1.1",
    author="Jeroen van Oostendorp",
    packages = find_packages(),
    install_requires = requirements
)

