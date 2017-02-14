from setuptools import setup, find_packages

setup(
    name="pycross",
    version="0.1",
    package_dir={'': 'src'},
    packages=find_packages(),
    author='Gergely, Gulyas',
    provides=['pycross'],
    zip_safe=False,
    install_requires=[
                      'numpy',
                      'pyopengl'
                      ],
    description='This is the description'
)
