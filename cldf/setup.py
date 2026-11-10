from setuptools import setup

setup(
    name="cldfbench_phonobank",
    py_modules=["cldfbench_phonobank"],
    packages=["phonobank_commands"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "cldfbench.dataset": [
            "phonobank=cldfbench_phonobank:Dataset",
        ],
        "cldfbench.commands": [
            "phonobank=phonobank_commands",
        ],
    },
    install_requires=[
        "cldfbench",
        "pycldf",
    ],
    extras_require={
        "test": [
            "pytest-cldf",
        ],
    },
)
