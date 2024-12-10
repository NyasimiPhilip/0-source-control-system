from setuptools import setup, find_packages

setup(
    name='pygit',
    version='1.0.0',
    description='A lightweight implementation of Git in Python',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pygit=pygit.cli:main',
        ],
    },
    install_requires=[
        'graphviz>=0.20.1',  # For visualization of commit graphs
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)