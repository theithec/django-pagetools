import os
from setuptools import setup, find_packages

from version import get_version

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-pagetools',
    version=get_version(),
    packages=find_packages(exclude=("demo", "demo.*")),
    include_package_data=True,
    license='MIT License',
    description='A set of Django apps to to provide some cms-like features',
    # install_requires=[
    #     "Django==2.*",
    #     "beautifulsoup4==4.*",
    #     "django-crispy-forms==1.8.*",
    #     "django-debug-toolbar==3.*",
    #     "django-filebrowser==3.12.*",
    #     "django-grappelli<=2.14",
    #     "django-model-utils==4.0.*",
    #     "django-mptt==0.11.*",
    #     "django-sekizai==1.1.*",
    #     "django-simple-captcha==0.5.*",
    #     "djangoajax==3.*",
    #     "Pillow==8.*",
    # ],

    long_description=README,
    author='Tim Heithecker',
    author_email='tim.heithecker@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    test_suite="runtests.runtests",
)
