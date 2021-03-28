from setuptools import find_packages, setup

setup(
    name='pyTranslate',
    packages=find_packages("./pyTranslate"),
    version='0.1.0',
    description='Custom Python translator API',
    author='KeksUngegessen',
    license='MIT',
    install_requires=['selenium', 'msedge-selenium-tools', 'webdriver_manager']
)
