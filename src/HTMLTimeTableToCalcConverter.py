"""
----------------------------------------------------------------------------------------
OVERVIEW

REQUIREMENTS
- BeautifulSoup (bs4)
- Pandas

Date created: around 2023
This is a simple script I wrote to convert some HTML Time Table into the Libre Office Calc format
You must statically define the file path!

THIS SCRIPT IS VERY SIMPLE AND WAS WRITTEN FOR ONLY ONE SPECIFIC FORMAT. IT WILL 99% NOT WORK FOR YOUR USE CASE
----------------------------------------------------------------------------------------
"""


from bs4 import BeautifulSoup
from pandas import DataFrame


PATH = r"C:\Users\You\Desktop\New Text Document.html"


with open(PATH, mode='rt',
          encoding='utf-8') as file:
    calc_html: str = file.read()

soup: BeautifulSoup = BeautifulSoup(calc_html, 'html.parser')
table = soup.find('table')

data = []

for row in table.find_all('tr'):
    row_data = [cell.text for cell in row.find_all(['td', 'th'])]
    data.append(row_data)

data_frame: DataFrame = DataFrame(data[1:], columns=data[0])

data_frame.to_excel('output.xlsx', index=False)
