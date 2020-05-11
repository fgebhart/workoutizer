import setuptools
from workoutizer import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()


def requirements_from_txt(path_to_txt):
    with open(path_to_txt, "r") as f:
        reqs = f.readlines()
    return [req for req in reqs if not req.startswith("#")]


setuptools.setup(
    name="workoutizer",
    version=__version__,
    author="Fabian Gebhart",
    install_requires=requirements_from_txt('requirements.txt'),
    description="Browser-based Sport Workout Organizer to analyze your Activities locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/fgebhart/workoutizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    packages=setuptools.find_packages(exclude=['tests'])
)
