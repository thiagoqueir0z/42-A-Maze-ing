from pathlib import Path
from setuptools import setup, find_packages


BASE_DIR = Path(__file__).parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="mazegen-mariaalm",
    version="1.0.0",
    packages=find_packages(exclude=("*.test", "*.test.*", "test", "test.*")),
    include_package_data=True,
    package_data={
        "mazegen.mlx": ["libmlx.so", "docs/*"],
    },
    install_requires=[],
    python_requires=">=3.10",
    author="mariaalm",
    description="A reusable maze generator module for the 42 curriculum",
    long_description=README,
    long_description_content_type="text/markdown",
)
