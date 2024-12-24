# setup.py

from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='graylog_telemidia',
    version='1.0.14',
    packages=find_packages(),
    install_requires=[
        'graypy',
    ],
    description='Este pacote fornece uma interface simples e eficiente para enviar mensagens de log para o Graylog, seguindo o padrão utilizado pela Telemidia.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    readme="README.md",
    author='Thales Casa Grande de Lima',
    author_email='cor@telemidia.net.br',
    url='https://github.com/telemidia-isp/graylog-telemidia-py',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)