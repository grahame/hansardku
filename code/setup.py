from setuptools import setup, find_packages

dev_requires = ['flake8', 'nose']
install_requires = ['requests>=2.2']

setup(
    author = "Grahame Bowland",
    author_email = "grahame@angrygoats.net",
    description = "Haiku form the hansard.",
    license = "GPL3",
    url = "https://github.com/grahame/hansardku",
    name = "hansardku",
    version = "0.0.1",
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    extras_require = {
        'dev': dev_requires
    },
    install_requires = install_requires,
)
