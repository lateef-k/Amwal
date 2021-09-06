import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

NAME = "amwal"
DESCRIPTION = "The unofficial API for the Boursa"
URL = "https://github.com/abal2051/Amwal"
EMAIL = "abal2051@colorado.edu"
AUTHOR = "Abdullatif Khalid"
REQUIRES_PYTHON = '>=3.6.0'

REQURIED = ['python-dateutil','pandas','requests','beautifulsoup4']

setuptools.setup(
    name=NAME, 
    version="0.0.5",
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    install_requires=REQURIED,
    packages=['amwal'],
    classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: Implementation :: CPython',
            ],
    python_requires='>=3.6',
)


