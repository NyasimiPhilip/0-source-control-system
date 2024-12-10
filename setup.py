from setuptools import setup, find_packages

setup(
    name='pygit',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pygit=pygit.cli:main',
        ],
    },
    python_requires='>=3.6',
)