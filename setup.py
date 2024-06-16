import setuptools


setuptools.setup(
    name='metabot',
    version='0.3.19',
    author='Daniel Reed',
    author_email='nmlorg@gmail.com',
    description='Modularized, multi-account bot.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nmlorg/metabot',
    packages=setuptools.find_packages(include=('metabot', 'metabot.*')),
    python_requires='>=3.8',
    install_requires=[
        'googlemaps',
        'ntelebot >= 0.3.4',
        'pytz',
        'PyYAML >= 5.1',
        'requests',
    ])
