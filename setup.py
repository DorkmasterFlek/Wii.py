import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="Wii.py",
      version='0.1',
      description="Wii library written in and for Python",
      url='https://github.com/DorkmasterFlek/Wii.py',
      author="Xuzz, SquidMan, megazig, Matt_P, Omega, The Lemon Man, marcan, Daeken",
      author_email="",
      maintainer="Dorkmaster Flek",
      maintainer_email="dorkmasterflek@gmail.com",
      license="GNU GPL v3",
      python_requires=">=2.7, >=3.3",
      long_description=long_description,
      packages=["Wii"],
      install_requires=['pycrypto', 'Pillow'],
      extras_require={
          'GUI': ["wxPython"],
      },
      )
