import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="fyysikkospeksi-taulubot",
    version=0.1,
    description="Telegram bot for adding a Fyysikkospeksi frame to a profile picture.",
    long_description=read('README.md'),
    author="Fyysikkospeksi",
    author_email="tuottajat@fyysikkospeksi.fi",
    url="https://github.com/fyysikkokilta/fyysikkospeksi-taulubot",
    packages=['taulubot'],
    python_requires=">=3.6.9,<3.10",
    install_requires=[
        "Pillow~=8.3",
        "numpy~=1.21",
        "python-telegram-bot~=13.7",
        "requests~=2.26",
    ],
    extras_require={
        "test": [
            "pylint~=2.9",
            "pytest-asyncio~=0.15",
            "pytest-cov~=2.12",
            "pytest-sugar~=0.9",
            "pytest-xdist~=2.3",
            "pytest~=6.1",
            "telethon~=1.23",
        ],
    },
)
