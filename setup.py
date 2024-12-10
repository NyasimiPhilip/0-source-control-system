from setuptools import setup, find_packages

setup(
    name='pygit',
    version='1.0.0',
    description='A lightweight implementation of Git in Python',
    author='Nyasimi Philip',
    author_email='nyasimiphilip@gmail.com',
    url='https://github.com/yourusername/pygit',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pygit=pygit.cli:main',
        ],
    },
    install_requires=[
        # List any dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)