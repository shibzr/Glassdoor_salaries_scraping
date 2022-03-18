from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'A basic package to scrape and analyze salary data from Glassdoor using Selenium'
LONG_DESCRIPTION = 'A little package that allows to scrape salary data off Glassdoor for analyzing' \
                   'market salary for any profession in any city in the world then make ' \
                   'statistics analysis and visulaizations on the data'

# Setting up
setup(
    name="GlassdoorScrapping",
    version=VERSION,
    author="Shehab Raslan",
    author_email="<shehab.raslan.fr@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['Selenium','chromedriver-binary', 'Pandas', 'Numpy', 'Plotly'],
    keywords=['python', 'selenium', 'Glassdoor', 'salary', 'data science'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Data Scientists",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)