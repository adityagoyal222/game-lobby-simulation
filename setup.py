from setuptools import setup, find_packages

setup(
    name="gamematchmaking",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "kafka-python==2.0.2",
        "confluent-kafka==2.3.0",
        "peewee==3.17.0",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "pydantic==2.5.3",
    ],
)
