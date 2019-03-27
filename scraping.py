from time import sleep
import requests
from bs4 import BeautifulSoup
from rx_class import Rx
import mysql.connector
import re

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
data collection of top 300 drugs in United States from website and organizing scraped data
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







#######################################################################################  insertion bellow


"""
insertion into the drug table
"""
sql = "INSERT INTO drugs (name, total_rx) VALUES (%s, %s)"

#format Rx data for sql insertion
data = [(value.drug_name, value.total_rx) for value in top_300_drugs]

#insert
mycursor.executemany(sql, data)

#commit
connection.commit()

#confirmation of insertion
print(mycursor.rowcount, "was inserted.")





"""
insertion into the brand_name table
"""


#gather brand names associated with each drug
brand_urls = "https://clincalc.com/DrugStats/Drugs/"


for drug in top_300_drugs:
        #generate each drug's unique url
        url_search = ''.join(c for c in drug.drug_name if c.isalpha())
        drug_url = brand_urls + url_search
        
        res = requests.get(drug_url)
        soup = BeautifulSoup(res.text, "html.parser")
        
        #grab the table with the brand names, organize the names into a list of strings
        columns = soup.find(class_="columns large-6")
        #check for NoneType if no brand names
        if columns:
                #find and grab the brand names
                child = columns.findChild()
                ul = child.find_next_sibling().findChildren()
                data = [value.text for value in ul]
        
                #insert all the associated brand names into the database where the current rank of the current drug = drug_id
                sql= "INSERT INTO brand_names (name, drug_id) VALUES (%s, %s)"
                insertion = [(brand, int(drug.rank)) for brand in data]
                mycursor.executemany(sql, insertion)
                connection.commit()
                
                #confirmation of number of brand names inserted
                print(mycursor.rowcount, " was inserted.")
        
        #rest the scraper
        sleep(2)
        




"""
scraping of drug.com and insertion into database for side effects
"""
#used for storing found side effects,
serious_side_effects = {}
common_side_effects = {}

side_effects_table = []

base_url = "https://www.drugs.com/search.php?searchterm="
#format the names for the search url link
basic_drug_names = [name.drug_name.split(';')[0].replace(' ', '+') for name in top_300_drugs]

#use the website serach bar, search the full name, grab only the "Editor's Pick" links, go to side effects page from there
for item in basic_drug_names:
        res = requests.get(base_url + item)
        soup = BeautifulSoup(res.text, "html.parser")
        #search for the Editor's Pick
        found =soup.find(title='Editor\'s Pick')
        
        
        if found:
                #follow the hyperlink to the side effects page
                parent =soup.find(class_="snippet search-result search-result-with-secondary")
                parent = parent.find('ul', class_="search-result-secondary column-list-2")
                link = "https://www.drugs.com" + parent.find('a', href=True).get('href')
                
                sleep(1)
                
                #scrape the current drugs side effect page
                sideEffect_res = requests.get(link)
                side_soup = BeautifulSoup(sideEffect_res.text, "html.parser")
                
                #gather the side effects and organize text into a list of strings
                more_common = side_soup.find_all('h3', text='More Common') #finds both serious and nonserious side effects if they exist
                if len(more_common) > 1: # there are both serious and nonserious side effects
                        serious_more_common_table = more_common[0].find_next_sibling().text.strip().splitlines()
                        nonserious_more_common_table = more_common[1].find_next_sibling().text.strip().splitlines()
                        #append both to the side effects list
                        side_effects_table.extend(serious_more_common_table)
                        side_effects_table.extend(nonserious_more_common_table)
                #there is only one category of side effects for this frequency
                elif len(more_common) == 1:
                        side_effects_table.extend(more_common[0].find_next_sibling().text.strip().splitlines())
                        
                less_common = side_soup.find_all('h3', text='Less Common')
                if len(less_common) > 1:
                        serious_less_common_table = less_common[0].find_next_sibling().text.strip().splitlines()
                        nonserious_less_common_table = less_common[1].find_next_sibling().text.strip().splitlines()
                        side_effects_table.extend(serious_less_common_table)
                        side_effects_table.extend(nonserious_less_common_table)
                elif len(less_common) == 1:
                        side_effects_table.extend(less_common[0].find_next_sibling().text.strip().splitlines())                
                                
                rare = side_soup.find_all('h3', text='Rare')
                if len(rare) > 1:
                        serious_rare_table = rare[0].find_next_sibling().text.strip().splitlines()
                        nonserious_rare_table = rare[1].find_next_sibling().text.strip().splitlines()
                        side_effects_table.extend(serious_rare_table)
                        side_effects_table.extend(nonserious_rare_table)
                elif len(rare) == 1:
                        side_effects_table.extend(rare[0].find_next_sibling().text.strip().splitlines())            
                        
        #insert all the side effects of current drug
        sql = "INSERT INTO side_effects (effect, drug_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE effect = effect"
        data = [(side_effect, basic_drug_names.index(item)+1) for side_effect in side_effects_table]
        
        mycursor.executemany(sql, data)      
        connection.commit()
        print(item + " side effects were inserted. " + str(basic_drug_names.index(item)+1) + " of 300 committed.")
        
        sleep(2)
        
        
        
        
        
"""
scraping and insertion of associated_diseases
"""

base_url = "https://www.drugs.com/search.php?searchterm="
#format the names for the url link
basic_drug_names = [name.drug_name.split(';')[0].replace(' ', '+') for name in top_300_drugs]

#initialize id's for drug and disease to match the MySQL Pimary Keys
drugId = 1
diseaseId = 1
disease_table = {}

#use the website serach bar, search the full name, grab only the "Editor's Pick" links, go to side effectrs from there
for item in basic_drug_names:
        
        
        res = requests.get(base_url + item)
        soup = BeautifulSoup(res.text, "html.parser")
        #search for the Editor's Pick
        found =soup.find(title='Editor\'s Pick')
        
        
        if found:
                #follow the hyperlink to the overview page
                parent =soup.find(class_="snippet search-result search-result-with-secondary")
                link = parent.find('a', href=True).get('href')
                overview_res = requests.get(link)
                second_side_soup = BeautifulSoup(overview_res.text, "html.parser")
               
                #search for specific associated diseases with cg in url
                overview = second_side_soup.find('a', href= re.compile("cg"))
                
                #if there is none, it may be more general e.g. "infection" with mcd in url, redo overview variable with new parameter
                if not overview:
                        overview = second_side_soup.find('a', href= re.compile("mcd"))
               
                
                
                #scrapper could not find a hyperlink at all
                if not overview:
                        print("No disease found for drug id " + str(basic_drug_names.index(item)+1))
                        
                #the current drug has an associated disease
                else:
                        #get the disease text
                        disease = overview.text.lower() #lower for Python/MySQL casesensitivity
                        
                        #a preexisting disease in the dictionary
                        if disease in disease_table:
                                temp = disease_table[disease] #assign the diseaseId of the prexisting disease to a temporary variable for sql insertion
                        
                        #a unique disease, append to the dictionary of diseases with its unique id        
                        else:        
                                disease_table[disease] = diseaseId
                                temp = diseaseId

                                #insert unique disease into database
                                sql= "INSERT INTO associated_diseases (name) VALUES (%s)"
                                mycursor.execute(sql, (disease,))
                                connection.commit()
                                
                                diseaseId += 1 #increment to match the next primary key in the database
                                
              
        #insert into the treats table the current drug's id and the disease associated with it
        print("inserting into sql: " + str(temp) + "," + str(diseaseId))        
        sql= "INSERT INTO treats (disease_id, drug_id) VALUES (%s, %s)"
        mycursor.execute(sql, (temp, drugId))
        connection.commit()
              
        #finished scripts, next drug in list
        print(str(basic_drug_names.index(item)+1) + " of 300 done")  
        drugId += 1
        sleep(2)
        