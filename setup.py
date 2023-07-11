from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.0'
DESCRIPTION = 'A Python library for interacting with PhonePe Payment Gateway API.'
LONG_DESCRIPTION = 'This Python package provides a simple interface to the PhonePe Payment Gateway. It can be used to ' \
                   'create PhonePe payment links, check the status of PhonePe transactions, and refund PhonePe ' \
                   'transactions. '


setup(
    name='phonepe',
    version=VERSION,
    description=DESCRIPTION,
    author='Bijay Nayak',
    author_email='bijay6779@gmail.com',
    url='https://github.com/devbijay/phonepe-pg',
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests', 'pydantic'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
    ,
)
