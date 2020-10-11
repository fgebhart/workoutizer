import os
import setuptools
from workoutizer import __version__

with open("Readme.md", "r") as fh:
    long_description = fh.read()


def requirements_from_txt(path_to_txt):
    path_to_reqs = os.path.join(os.path.dirname(__file__), 'setup', 'requirements')
    with open(os.path.join(path_to_reqs, path_to_txt), "r") as f:
        reqs = f.readlines()
    return [req for req in reqs if not req.startswith("#")]


setuptools.setup(
    name="workoutizer",
    author="Fabian Gebhart",
    version=__version__,
    setup_requires=['setuptools_scm'],
    install_requires=requirements_from_txt('requirements.txt'),
    include_package_data=True,
    description="Browser-based Sport Workout Organizer to analyze your Activities locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fgebhart/workoutizer",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
    ],
    python_requires='>=3.7',
    extras_require={
        'testing': requirements_from_txt('dev-requirements.txt'),
    },
    packages=setuptools.find_packages(exclude=['tests']) + ['setup', 'tracks', 'media'],
    entry_points={"console_scripts": ["wkz = workoutizer.__main__:cli"]}
)
