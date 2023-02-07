""" Setup for pip-install. """

from setuptools import setup


setup(
    name='aws_sigv4',
    version='1.0.0',
    description='AWS SigV4 for httpx',
    author='Spandan Sharma',
    author_email='ustulation@gmail.com',
    python_requires='>=3.10',
    url='https://github.com/ustulation/aws-sigv4-python',
    py_modules=['aws_sigv4'],
    install_requires=['boto3', 'botocore', 'httpx'],
    include_package_data=True,
    license='GNU General Public License v3.0',
)
