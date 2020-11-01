# COVID19 - Basic graphs about situation evolution
This very simple code is only supposed to give the possibility to create very basic interactive graphs.
Python code written quickly: absolutely no warranty on anything here, use it at your own risks.

## Prerequisites
- python3
- Install plotly, pandas and jupyter:
 > python3 -m pip install pandas jupyter plotly>=4.8

## Get COVID19 raw data: https://github.com/CSSEGISandData/COVID-19
Go to a folder where you would like to save COVID19 data and clone the repo containing it:
 > git clone git@github.com:CSSEGISandData/COVID-19.git

## Then, set in file default.env the path to your COVID-19 data repo. You can now run `inspect-covid19.py`
 > python3 inspect-covid19.py
- Graphs will open automatically
- 2 hmtl files will be generated: you can open them with any browser.

## To compare first & second tides run jupyter notebook inspect_france.ipynb

## Updates
When new data is available, just git pull the COVID-19 raw data repo and re-run inspect-covid.py to get new graphs and html.
