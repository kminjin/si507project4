import requests, json, csv
from bs4 import BeautifulSoup
from advanced_expiry_caching import Cache

# "crawling" -- generally -- going to all links from a link ... like a spiderweb
# its specific def'n varies, but this is approximately the case in all situations
# and is like what you may want to do in many cases when scraping

######

# A "simple" example (without much fancy functionality or data processing)

# Constants
START_URL = "https://www.nps.gov/index.htm"
FILENAME = "national_sites.json"

# So I can use 1 (one) instance of the Cache tool -- just one for my whole program, even though I'll get data from multiple places
PROGRAM_CACHE = Cache(FILENAME)

# assuming constants exist as such
# use a tool to build functionality here
def access_page_data(url):
    data = PROGRAM_CACHE.get(url)
    if not data:
        data = requests.get(url).text
        PROGRAM_CACHE.set(url, data) # default here with the Cache.set tool is that it will expire in 7 days, which is probs fine, but something to explore
    return data

#######

main_page = access_page_data(START_URL)

# explore... find that there's a <ul> with class 'topics' and I want the links at each list item...

# I've cached this so I can do work on it a bunch
main_soup = BeautifulSoup(main_page, features="html.parser")
list_of_topics = main_soup.find('ul',{'class':'dropdown-menu SearchBar-keywordSearch'})
# print(list_of_topics) # cool


# for each list item in the unordered list, I want to capture -- and CACHE so I only get it 1 time this week --
# the data at each URL in the list...
all_links = list_of_topics.find_all('a')
# print(all_links) # cool
# now need each one's href attr

# # Debugging/thinking code:
#
# for link in all_links:
#     print(link['href'])
#
#     # Just text! I'm not going back to the internet at all anymore since I cached the main page the first time

# This is stuff ^ I'd eventually clean up, but probably not at first as I work through this problem.

all_pages = [] # gotta get all the data in BeautifulSoup objects to work with...
for l in all_links:
    page_data = access_page_data('http://www.nps.gov' + l['href'])
    soup_of_page = BeautifulSoup(page_data, features="html.parser")
    all_pages.append(soup_of_page)
# print(all_pages)

# Now I can do some investigation on just one of those BeautifulSoup instances, and thus decide what I want to do with each one...
# Each time I run the program, I'm not going to the internet at all sometimes unless some page is new or it's -- in this case -- been more than 7 days since storing data.
# After the first time, it'll run much faster! (On a certain scale, anyway)

# Just for example --
# print(topics_pages[0].prettify())
all_info=[]
for each in all_pages:
    each_info = each.find_all('li', {'class':'clearfix'})
    for each in each_info:
        each_list = []
        if each.find('h3') == None:
            continue
        if each.find('h3'):
            name = each.find('h3')
            each_list.append(name.text)
        if len(each.find('h2')) == 0:
            each_list.append('National Site')
        else:
            type = each.find('h2')
            each_list.append(type.text)
        if len(each.find('p')) == 0:
            each_list.append('NONE')
        else:
            description = each.find('p')
            each_list.append(description.text)
        if len(each.find('h4')) == 0:
            each_list.append('NONE')
        else:
            location = each.find('h4')
            each_list.append(location.text)
        all_info.append(each_list)

# new_list = [all_list[i:i+4] for i in range(0, len(all_list), 4)]



# with open('national_sites.csv','w') as parks_file:
#     parkwriter = csv.writer(parks_file)
#     parkwriter.writerow(['Park Name','Park Type','Desc','Park Location'])
#     for each in all_list:
#         parkwriter.writerow(each[0], each[1],each[2],each[3],', ')


outfile = open('national_sites.csv','w',encoding='utf-8')
outfile.write('NAME,TYPE,DESCRIPTION,LOCATION')
outfile.write('\n')
for each in all_info:
    line = '{},{},{},{}'.format(each[0],each[1],each[2].replace('\n',' ').replace(',',' '),each[3].replace(',',' '))
    outfile.write(line)
    outfile.write('\n')
outfile.close()

# outfile=open("national_sites.csv","w")
# header1="NAME,TYPE,DESCRIPTION,LOCATION\n"
# outfile.write(header1)
# for each in all_list:
#     line="{},{},\"{}\",\"{}\"\n".format(each[0], each[1],each[2],each[3])
#     outfile.write(line)
# outfile.close()

# with open('national_sites.csv','w') as nationalsites_file:
#     writer = csv.writer(nationalsites_file)
#     writer.writerow(['Name','Type','Description','Location', 'Main State'])
