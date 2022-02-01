import os

from setuptools import find_packages, setup

from version import get_version


README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

setup(
    name="django-pagetools",
    version=get_version(),
    packages=find_packages(exclude=("demo", "demo.*")),
    include_package_data=True,
    license="MIT License",
    description="A set of Django apps to to provide some cms-like features",
    python_requires=">=3.6",
    install_requires=[
        "Django >=3.0,<4.0",
        "django-crispy-forms==1.14.0",
        "django-grappelli==3.0.*",
        "beautifulsoup4==4.10.*",
        "django-debug-toolbar==3.2.*",
        "django-filebrowser==4.0.*",
        "django-mptt==0.13.*",
        "django-sekizai==3.0.*",
        "django-model-utils==4.2.*",
        "django-simple-captcha==0.5.*",
        "djangoajax==3.*",
        "Pillow==9.*",
    ],
    long_description=README,
    author="Tim Heithecker",
    author_email="tim.heithecker@gmail.com",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",  # example license
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    test_suite="runtests.runtests",
)
