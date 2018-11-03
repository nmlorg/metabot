import setuptools


setuptools.setup(
    name='metabot',
    version='0.0.3.0',
    author='Daniel Reed',
    author_email='nmlorg@gmail.com',
    description='Modularized, multi-account bot.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nmlorg/metabot',
    packages=setuptools.find_packages(include=('metabot', 'metabot.*')),
    namespace_packages=setuptools.find_packages(include=('metabot', 'metabot.*')),
    install_requires=['ntelebot >= 0.1.1, < 0.2', 'pytz', 'requests'])
