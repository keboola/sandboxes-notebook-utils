from setuptools import setup

setup(
    name='keboola-sandboxes-notebook-utils',
    version='2.2.0',
    url='https://github.com/keboola/sandboxes-notebook-utils',
    packages=['keboola_notebook_utils'],
    package_dir={'keboola_notebook_utils': ''},
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'autosave-worker=keboola_notebook_utils.autosave_worker:main',
        ],
    },
)
