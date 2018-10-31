import setuptools


setuptools.setup(
    name='metabot',
    version='0.0.1.dev0',
    author='Daniel Reed',
    author_email='nmlorg@gmail.com',
    description='Modularized, multi-account bot.',
    url='https://github.com/nmlorg/metabot',
    packages=setuptools.find_packages(include=('metabot', 'metabot.*')),
    namespace_packages=setuptools.find_packages(include=('metabot', 'metabot.*')),
    install_requires=['ntelebot', 'pytz', 'requests'])
