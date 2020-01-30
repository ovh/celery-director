import os

from setuptools import find_packages, setup

requirements = []
with open("requirements.txt") as req:
    requirements = [r.rstrip() for r in req.readlines()]

dev_requirements = [
    "tox==3.5.3",
    "black==19.10b0",
]

setup(
    name="celery-director",
    version="0.0.1",
    description="Celery Director",
    long_description="Celery Director",
    author="OVHcloud",
    author_email="opensource@ovhcloud.com",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={"dev": dev_requirements, "ci": ["pytest", "pytest-cov"]},
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
