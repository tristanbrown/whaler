from setuptools import setup, find_packages

setup(name='whaler',
    version='0.0.1',
    author = "Tristan R. Brown",
    author_email = "brown.tristan.r@gmail.com",
    description = ("Analytical package for computational chemistry software, "
                        "ORCA."),
    url = 'https://github.com/tristanbrown/whaler',
    license = "MIT",
    packages = find_packages(),
    install_requires = [''],
    entry_points = {
        'console_scripts': [
            'whaler = my_project.__main__:main'
        ]
    },
    )