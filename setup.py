"""Setup script"""
import setuptools
import os
import re

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")
TESTS_REQUIRE = ["coverage", "nose", "pytest"]
DESCRIPTION = ""
REQUIRED_PACKAGES = [
    "click",
    "click_option_group",
    "botocore",
    "boto3",
]
PROJECT_NAME = "quiet-riot"
PROJECT_UNDERSCORE = "quiet_riot"
AUTHOR_NAME = "Wes Ladd"
AUTHOR_EMAIL = "noreply@example.com"
PROJECT_URL = "https://github.com/righteousgambitresearch/quiet-riot"


def get_version():
    init = open(os.path.join(HERE, PROJECT_UNDERSCORE, "bin", "version.py")).read()
    return VERSION_RE.search(init).group(1)


def get_description():
    return open(
        os.path.join(os.path.abspath(HERE), "README.md"), encoding="utf-8"
    ).read()


setuptools.setup(
    name=PROJECT_NAME,
    include_package_data=True,
    version=get_version(),
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url=PROJECT_URL,
    packages=setuptools.find_packages(exclude=["test*"]),
    tests_require=TESTS_REQUIRE,
    install_requires=REQUIRED_PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": f"{PROJECT_NAME}={PROJECT_UNDERSCORE}.bin.cli:main"},
    zip_safe=True,
    keywords="aws security",
    python_requires=">=3.7",
)
