from setuptools import setup
import json


with open('metadata.json', encoding='utf-8') as fp:
    metadata = json.load(fp)


setup(
    name='lexibank_spagnolmaltese',
    description=metadata['title'],
    license=metadata.get('license', ''),
    url=metadata.get('url', ''),
    py_modules=['lexibank_spagnolmaltese'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'spagnolmaltese=lexibank_spagnolmaltese:Dataset',
        ]
    },
    install_requires=[
        'pylexibank>=2.8',
        'idspy>=0.2',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
