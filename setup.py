from setuptools import setup, find_packages

setup(
    name="theseus_alpha",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "hyperliquid-python-sdk",
        "openai",
        "python-dotenv",
    ]
)