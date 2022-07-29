import setuptools


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='backtest',
    version='0.2.1',
    author='mniyk',
    author_email='my.name.is.yohei.kono@gmail.com',
    description='backtest python library',
    long_description=long_description,
    url='https://github.com/mniyk/backtest.git',
    packages=setuptools.find_packages(),
    install_requires=['pandas'])
