from setuptools import setup, find_packages

setup(
    name='Mennekes Amtron API',
    description='API to control Mennekes AMTRON wallbox chargers',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'minimalmodbus',
        'uvicorn'
    ],
    entry_points={
        'console_scripts': [
            'mennekes-amtron-api=mennekes_amtron_api.main:main'
        ]
    },
)
