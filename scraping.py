from time import sleep
import requests
from bs4 import BeautifulSoup
from rx_class import Rx
import mysql.connector

"""
setting up connection to SQL database
"""
#establishing the connection
connection = mysql.connector.connect(
        host="localhost",
        user="kevin_j_benoit",
        database="medication"
)

#create the cursor
mycursor = connection.cursor()


"""
data collection from website and organizing scraped data
"""

top_drugs_url = "https://clincalc.com/DrugStats/Top300Drugs.aspx"

res = requests.get(top_drugs_url)
soup = BeautifulSoup(res.text, "html.parser")

#grab the table from the webpage
table = soup.find_all('table')[0] 

#parse each row in the table
rows = table.find_all('tr')

top_300_drugs = []

#process the row to get Rank, Drug Name, Total Prescriptions
for row in rows:
        columns = row.find_all('td')
        columns=[x.text.strip() for x in columns]
        if columns:
                #rank, drug_name, total_rx(remove commas, convert to integer)
                drug = Rx(columns[0], columns[1], int(columns[2].replace(',', '')))
                top_300_drugs.append(drug)

"""
insertion into the database
"""
sql = "INSERT INTO drug (name, total_rx) VALUES (%s, %s)"

#format Rx data for sql insertion
data = [(value.drug_name, value.total_rx) for value in top_300_drugs]

#insert
mycursor.executemany(sql, data)

#commit
connection.commit()

#confirmation of insertion
print(mycursor.rowcount, "was inserted.")