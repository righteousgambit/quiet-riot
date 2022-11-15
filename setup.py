import setuptools

REQUIRES = [
                "setuptools>=42",
                 "wheel",
                 "boto3==1.17.84",
                 "requests==2.28.1"
]
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quiet_riot",
    version="1.0.3",
    author="Wess ladd",
    author_email="wesladd@traingrc.com",
    description="AWS Assessment tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={'quiet_riot': ["results/*.txt","wordlists/*.txt","*.txt","enumeration/*"]},
    install_requires=REQUIRES,
    url="https://github.com/pypa/sampleproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    entry_points={"console_scripts": "quiet_riot=quiet_riot.main:main"},
    # zip_safe=True,
    packages=setuptools.find_packages(),

    python_requires=">=3.7"
)
