import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="funcmaster",
    version="0.0.1",
    author="Farhan Husain",
    author_email="cooljackal@gmail.com",
    description="A straightforward workflow tool that is easy to use.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cooljackal/funcmaster",
    packages=["funcmaster"],
    entry_points={
        'console_scripts': ['funcmaster=funcmaster.cli:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)