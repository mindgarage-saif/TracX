from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="TracX",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    entry_points="""
        [console_scripts]
        TracX=TracX.studio:main
        TracX-Calibrate=TracX.calibrate:main
    """,
)
