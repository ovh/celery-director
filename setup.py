from pathlib import Path

from setuptools import find_packages, setup

with open(
    Path(__file__).parent.resolve() / "director" / "VERSION", encoding="utf-8"
) as ver:
    version = ver.readline().rstrip()

with open("requirements.txt", encoding="utf-8") as req:
    requirements = [r.rstrip() for r in req.readlines()]

long_description = ""
try:
    with open("README.md", encoding="utf-8") as readme:
        long_description = readme.read()
except FileNotFoundError:
    pass

dev_requirements = [
    "tox==3.5.3",
    "black==20.8b1",
]

doc_requirements = ["mkdocs==1.0.4", "mkdocs-material==4.6.3"]


setup(
    name="celery-director",
    version=version,
    description="Celery Director",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    author="OVHcloud",
    author_email="opensource@ovhcloud.com",
    url="https://github.com/ovh/celery-director",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "ci": ["pytest", "pytest-cov"],
        "doc": doc_requirements,
    },
    include_package_data=True,
    entry_points={"console_scripts": ["director=director.cli:cli"],},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: System :: Monitoring",
    ],
    python_requires="~=3.6",
)
