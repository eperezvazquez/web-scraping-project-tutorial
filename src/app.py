# your app code here
import pandas as pd
import numpy as np
import sqlite3
import requests
from bs4 import BeautifulSoup
import tqdm
import matplotlib.pyplot as plt

url = "https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue"

pag = requests.get(url)
pag_texto = pag.text
text_beaut = BeautifulSoup(pag_texto, "html.parser")
type(text_beaut)
tablas = text_beaut.findAll("table")
print(len(tablas))
id_tabla_quarter = None

for i in range(len(tablas)):
    if "Tesla Quarterly Revenue" in str(tablas[i]):
        id_tabla_quarter = i
        print("Tabla encontrada:", id_tabla_quarter)
        break

tabla_quarter = tablas[1]
tabla_quarter_body = tabla_quarter.tbody
lista_tr = tabla_quarter_body.find_all("tr")

revenue_ls = []

for tr in tqdm.tqdm(lista_tr):
    all_tr = tr.find_all("td")
    date = all_tr[0].text
    revenue = all_tr[1].text 
    #print("*"*10)
    #print(len(date), date)
    #print(date[0].text, date[1].text)
    revenue_ls.append([date,revenue])

print(revenue_ls)

revenue_df = pd.DataFrame(revenue_ls, columns=["Date", "Revenue"])

revenue_df.head()

def preproc_revenue(texto):
    texto = texto.replace("$","")
    texto = texto.replace(",","")
    if texto == "":
        return np.nan
    return float(texto)

preproc_revenue(revenue_df["Revenue"][1])
revenue_df["Revenue"]=revenue_df["Revenue"].apply(preproc_revenue)
revenue_df = revenue_df.dropna(subset="Revenue")
revenue_df.to_csv("revenue_df.csv", index=None)

##Generando el SQL
connection = sqlite3.Connection("Tesla.db")
c = connection.cursor()
#Step 8: Let's create a table in our database to store our revenue values:
# Create table
c.execute('''CREATE TABLE revenue4
(Date, Revenue)''')

records = revenue_df.to_records(index=False)
list_of_tuples = list(records)
# Insert the values
c.executemany('INSERT INTO revenue4 VALUES (?,?)', list_of_tuples)
# Save (commit) the changes
connection.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
connection.close()
#Step 9: Now retrieve the data from the database
#Our database name is “Tesla.db”. We saved the connection to the connection object.

connection = sqlite3.Connection("Tesla.db")
c = connection.cursor()

#Next time we run this file, it just connects to the database, and if the database is not there, it will create one.
#https://docs.python.org/3/library/sqlite3.html
for row in c.execute('SELECT * FROM revenue4 ORDER BY date'):
        print(row)
#Step 10: Finally create a plot to visualize the data
#What kind of visualizations show we do?
#revenue_df.head()
fig = plt.figure(figsize=(10,6))
ax1 = fig.add_axes([0,0,1,1])
ax1.set_title('Revenue per year')
ax1.plot(revenue_df['Date'],
        revenue_df['Revenue'],
        color='blue'
)
plt.show()
