# encoding=utf8
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

MAIN_URL = "epocacosmeticos.com.br"
CATEGORIAS = ['Perfumes', 'Cabelos', 'Maquiagem', 'Dermocosméticos', 'Tratamentos', 'Corpo e Banho', 'Unhas']
productNames = []
productTitles = []
productUrls = []

def get_category_url(url,category):
    if 'http' not in url:
        url = 'http://'+url
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    categoryUrl = soup.find('a',text=category,href=True)
    
    return str(categoryUrl['href'])
    
def get_product_urls(url,classType,productUrls):
    if 'http' not in url:
        url = 'http://'+url

    driver = webdriver.Chrome()
    driver.get(url)
    innerHTML = driver.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(innerHTML)
    driver.close()

    #productUrls  = []
    #r = requests.get(url)
    #soup = BeautifulSoup(r.text)
    
    for productUrl in soup.findAll('a',class_=classType,href=True):
        if (productUrl not in productUrls) and ("epoca" in str(productUrl['href'])):
            productUrls.append(str(productUrl['href']))
    
    if soup.find('li',class_='next pgEmpty'):
        return False
    else:
        return True

    #return productUrls
    
def search_info(url,productNames,productTitles):
    if 'http' not in url:
        url = 'http://'+url
 
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    titleTag = soup.find('title')    
    productNameTag = soup.find('div',class_=re.compile("productName"))

    if (productNameTag):
        productNames.append(productNameTag.string)
        productTitles.append(titleTag.string)
        return True
    return False

def has_one_att_type(tag):
    if (len(tag.attrs)==1):
    	return tag.has_attr('type')
    return False

def number_of_pages(url):
    if 'http' not in url:
        url = 'http://'+url
 
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    productTag = soup.find(has_one_att_type)
    
    indexStart = productTag.string.find("=")
    indexEnd = productTag.string.find(";",indexStart)
    numberOfPages = productTag.string[indexStart+2:indexEnd]
    
    return int(numberOfPages)

############### MAIN PROGRAM ####################################

#for category in CATEGORIAS:
i = 2
categoryUrl = get_category_url(MAIN_URL, "Unhas")

while(get_product_urls(categoryUrl,"shelf-default__link",productUrls)):
    #print len(productUrls)
    if (i > 2):
        categoryUrl = categoryUrl[0:len(categoryUrl)-1-len(str(i-1))] + '#' + str(i)
    else:
        categoryUrl = categoryUrl + '#' + str(i)
    i = i + 1

i = 0
with open("result.csv",'wb') as resultFile:
    wr = csv.writer(resultFile)
    wr.writerow(['URLs:','Product Names:','Product Titles:'])
    previousLength = 0
    counter = 0
    for productUrl in productUrls:
        if (search_info(productUrl,productNames,productTitles)):
            print len(productNames), len(productTitles)
            wr.writerow([productUrl,productNames[i-counter],productTitles[i-counter]])
        else:
            counter = counter + 1
        previousLength = len(productNames)
        i = i + 1
    
# Close file
resultFile.close()


#numberOfPages = number_of_pages(categoryUrl)


#categoryUrl = "https://www.epocacosmeticos.com.br/perfumes#2"
#driver.get(categoryUrl)
#innerHTML = driver.execute_script("return document.body.innerHTML")
#soup = BeautifulSoup(innerHTML)
#tag = soup.find('li',class_='next')
#print tag
#for productUrl in soup.findAll('a',class_="shelf-default__link",href=True):
#    productUrls.append(str(productUrl['href']))
#print productUrls
    

# Close file
#resultFile.close()

#<li class="next">próximo</li>
#<li class="next pgEmpty">próximo</li>
