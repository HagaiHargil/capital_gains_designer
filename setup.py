import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="capital_gains", # Replace with your own username
    version="0.0.1",
    author="Hagai Har-Gil",
    author_email="hagaihargil@gmail.com",
    description="Converting tables",
    long_description=long_description,
    long_description_content_type="textmarkdown",
    packages=setuptools.find_packages(),
)