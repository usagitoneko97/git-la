import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-la",
    version="0.0.1",
    author="Ho Guo Xian",
    author_email="hogouxian@gmail.com",
    description="simple git picker from large directory structure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'scripts': ['git-la=git_la:main'],
    },
    python_requires='>=3.6',
)
