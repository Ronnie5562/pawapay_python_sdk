from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pawapay-python-sdk",
    version="1.0.0",
    author="Abimbola Ronald",
    author_email="abimbolaronald@gmail.com",
    description="Python SDK for PawaPay mobile money payment platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ronnie5562/pawapay_python_sdk",
    packages=find_packages(include=['pawapay', 'pawapay.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    keywords="pawapay, mobile money, payments, africa, fintech, api",
)
