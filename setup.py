from setuptools import setup, find_packages

setup(
    name="walgreens-print",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "pillow>=9.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "walgreens-print=walgreens_print.__main__:main",
        ],
    },
    description="CLI tool to print photos at Walgreens",
    author="Walgreens Print Team",
) 