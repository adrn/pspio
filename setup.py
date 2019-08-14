from setuptools import setup

setup(name='pspio',
      version='0.1',
      description='A Python reader for EXP PSP files',
      author='adrn',
      author_email='adrianmpw@gmail.com',
      url='https://github.com/adrn/pspio',
      packages=['pspio'],
      install_requires=['numpy', 'astropy', 'pyyaml']
)