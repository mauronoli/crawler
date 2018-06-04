# encoding=utf8
################################ LIBRARIES ####################################
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from bs4 import BeautifulSoup
from requests import get
import requests
import re
import csv
import selenium
from selenium import webdriver


################################ GLOBAL VARIABLES ####################################
MAIN_URL = "epocacosmeticos.com.br"
CATEGORIES = ['Perfumes', 'Cabelos', 'Maquiagem', 'Dermocosméticos', 'Tratamentos', 'Corpo e Banho', 'Unhas']
productNames = []
productTitles = []
productUrls = []


################################ FUNCTIONS ####################################
def get_category_url(url,category):  #Returns the URL of the respective category page
    if 'http' not in url:
        url = 'http://'+url   #adds http to the URL if it's not there
    
    r = requests.get(url)   #get request for the main URL
    soup = BeautifulSoup(r.text)   #stores the html related to the URL
    categoryUrl = soup.find('a',text=category,href=True)   #searches for links with the respective category name
    
    return str(categoryUrl['href'])
    
def get_product_urls(url,classType,productUrls): #stores the product URLs in a list
    if 'http' not in url:
        url = 'http://'+url

    driver = webdriver.Chrome()
    driver.get(url)   #opens a Chrome browser with a certain URL
    innerHTML = driver.execute_script("return document.body.innerHTML")   #execute JavaScript and stores the resulting html in the variable innerHTML
    soup = BeautifulSoup(innerHTML)   #Now the html can be parsed with BeautifulSoup
    driver.close()   #closes the browser

    for productUrl in soup.findAll('a',class_=classType,href=True):   #finds all links with the class attribute equal to classType
        if (productUrl not in productUrls) and ("epoca" in str(productUrl['href'])):
            productUrls.append(str(productUrl['href']))   #appends to the list if it's not already there (to eliminate duplicat entries)
                                                          #and if 'epoca' is part of the URL (to eliminate URLs from adds)
    
    if soup.find('li',class_='next pgEmpty'):
        return False   #last page of this category
    else:
        return True   #not last page of this category
    
def search_info(url,productNames,productTitles):
    if 'http' not in url:
        url = 'http://'+url
 
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    titleTag = soup.find('title')   #searches for title tag
    productNameTag = soup.find('div',class_=re.compile("productName"))   #searches for div tags whose class attribute contains the string "productName"

    if (productNameTag):
        productNames.append(productNameTag.string)
        productTitles.append(titleTag.string)
        return True   #returns True if product URL was found
    return False   #returns False if product URL was found


################################ FUNCTIONS ####################################
for category in CATEGORIES:   #navigate through all the different categories of products
    page = 2
    categoryUrl = get_category_url(MAIN_URL, category)

    while(get_product_urls(categoryUrl,"shelf-default__link",productUrls)):   #repeats until the last page is reached   
        if (page > 2):
            categoryUrl = categoryUrl[0:len(categoryUrl)-1-len(str(page-1))] + '#' + str(page)   #rearranges the URL to navigate through the pages
        else:
            categoryUrl = categoryUrl + '#' + str(page)   #transition from first to second page
        page = page + 1   #increment page number

i = 0
with open("result.csv",'wb') as resultFile:   #opens a csv file to write on
    wr = csv.writer(resultFile)
    wr.writerow(['URLs:','Product Names:','Product Titles:'])   #writes the first line of the file: the header
    previousLength = 0
    counter = 0
    for productUrl in productUrls:
        if (search_info(productUrl,productNames,productTitles)):   #found the URL
            wr.writerow([productUrl,productNames[i-counter],productTitles[i-counter]])   #writes information on file
        else:   #URL not found
            counter = counter + 1   #offset to adjust the index of the list after a URL not found
        i = i + 1   #index of the list to be written to the file
   
resultFile.close()   #closes file
