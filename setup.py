from setuptools import setup, find_packages

setup(
    name='gamematchmaking',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'google-cloud-pubsub==2.19.0',
        'sqlalchemy==2.0.25',
        'pg8000==1.31.2',
        'cloud-sql-python-connector==1.13.0',
        'python-dotenv==1.0.0',
        'pydantic==2.5.3',
    ],
    entry_points={
        'console_scripts': [
            'run-streamer=src.simulator.data_streamer:main',
            'run-consumer=src.matchmaking.consumer:main',
            'run-datagen=src.scripts.data_gen:main',
            'run-initdb=src.scripts.init_db:main',
        ],
    },
)