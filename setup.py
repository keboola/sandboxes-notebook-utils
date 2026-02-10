from distutils.core import setup

setup(
    name='keboola-sandboxes-notebook-utils',
    version='2.3.0.dev3',
    url='https://github.com/keboola/sandboxes-notebook-utils',
    packages=['keboola_notebook_utils'],
    package_dir={'keboola_notebook_utils': ''},
    python_requires='>=3.10',
    install_requires=['requests'],
)
