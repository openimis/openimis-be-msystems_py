import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='openimis-be-msystems',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='GNU AGPL v3',
    description='The openIMIS Backend msystems reference module.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://openimis.org/',
    author='Kamil Malinowski',
    author_email='kmalinowski@soldevelo.com',
    install_requires=[
        'django',
        'django-db-signals',
        'djangorestframework',
        'openimis-be-core',
        'openimis-be-location',
        'openimis-be-policyholder',
        'lxml==4.9.3',
        'xmlsec==1.3.12',
        'python3-saml==1.16.0',
        'zeep==4.2.1'
        'spyne==2.14.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
)
