from setuptools import Extension, setup

setup(
    name="feal_in_c",
    version="1.0",
    description="FEAL encryption C extension module",
    ext_modules=[
        Extension(
            "feal_in_c",
            sources=["feal_module.c", "feal.c"],
            include_dirs=["."],
        )
    ],
)
