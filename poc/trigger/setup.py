from setuptools import setup, find_packages

setup(
    name='caminae',
    version = '0.1',
    description = 'Manage triggers with Django commands.',
    author = 'Makina Corpus',
    packages=find_packages(),
    install_requires = ['django == 1.4',
                        'South == 0.7.5'],
)
