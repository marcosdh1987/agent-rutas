import os
from setuptools import setup, find_packages

def load_requirements(filename='requirements.in'):
    """Load requirements from a file, ignoring blank lines and comments."""
    here = os.path.abspath(os.path.dirname(__file__))
    req_path = os.path.join(here, filename)
    with open(req_path, 'r') as f:
        lines = f.read().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]

setup(
    name='agent_rutas',
    version='0.1.0',
    description='Agente especializado en informar sobre el estado de las rutas de la provincia de Neuquén',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=load_requirements(),
    python_requires='>=3.8',
    include_package_data=True,
)