from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in revoh/__init__.py
from revoh import __version__ as version

setup(
	name="revoh",
	version=version,
	description="Revoh Company Customizations",
	author="Jagadeesan",
	author_email="jagadeesan.a1104@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
