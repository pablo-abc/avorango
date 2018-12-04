from setuptools import setup, find_packages

setup(
    name='avorango',
    version='0.1.0',
    author='Pablo Berganza',
    author_email='pberganza10@gmail.com',
    description='An ORM for ArangoDB',
    packages=find_packages(),
    install_requires=[
        'python-arango',
        'stringcase',
    ],
)
