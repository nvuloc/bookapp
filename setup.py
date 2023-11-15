from setuptools import setup, find_packages

setup(
    name="challenge-ocelot",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi == 0.104.1",
        "SQLAlchemy == 2.0.23",
        "uvicorn >= 0.24.0",
        "psycopg2-binary >= 2.9.9",
        "python-multipart >= 0.0.6",
        "bcrypt >= 4.0.1",
        "python-jose[cryptography] >= 3.3.0",
        "python-dotenv >= 1.0.0"
    ],
    extras_require={
        "development": [
            "httpx >= 0.25.1",
            "pytest >= 7.4.3"
        ]
    }
)
