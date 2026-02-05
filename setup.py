from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="drf-scoped-permissions",
    version="0.1.0",
    author="Frankapps",
    author_email="hello@frankapps.com",
    description="Resource-scoped API key and group permissions for Django REST Framework. Built for startups moving fast.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frankapps-io/drf-scoped-permissions",
    project_urls={
        "Bug Tracker": "https://github.com/frankapps-io/drf-scoped-permissions/issues",
        "Documentation": "https://github.com/frankapps-io/drf-scoped-permissions",
        "Source Code": "https://github.com/frankapps-io/drf-scoped-permissions",
    },
    packages=find_packages(exclude=["tests*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=[
        "Django>=4.2",
        "djangorestframework>=3.14",
        "djangorestframework-api-key>=3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-django>=4.5",
            "pytest-cov>=4.0",
            "ruff>=0.1.0",
            "mypy>=1.0",
            "django-stubs>=4.2",
            "djangorestframework-stubs>=3.14",
        ],
        "jwt": [
            "djangorestframework-simplejwt>=5.0",
        ],
        "docs": [
            "sphinx>=6.0",
            "sphinx-rtd-theme>=1.2",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="django rest framework api key permissions scopes authorization",
)
