from setuptools import setup, find_packages

setup(
    name='tlv-weather-app',
    version='1.0.3',
    description='A simple Tel Aviv Rain Prediction App',
    author='Irena Guy',
    author_email='irenag@jfrog.com',
    packages=find_packages(),
    install_requires=[
        'flask',
        'requests',
        'gunicorn'
    ],
)

