from setuptools import setup

setup(
    name='phonepe',
    version='1.0.0',
    description='A Python library for interacting with PhonePe Payment Gateway API.',
    author='Bijay Nayak',
    author_email='bijay6779@gmail.com',
    url='https://github.com/devbijay/phonepe-pg',
    packages=['phonepe'],
    install_requires=[
        'requests', 'pydantic',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
