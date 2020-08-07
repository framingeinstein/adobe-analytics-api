import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="adobe-analytics-api_20",
    version="1.0.0",
    author="Jason Morgan",
    author_email="jason@framingeinstein.com",
    description="Adobe Analytics API 2.0 Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/framingeinstein/adobe-analytics-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)