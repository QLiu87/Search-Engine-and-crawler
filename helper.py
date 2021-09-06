import json
import os
from html.parser import HTMLParser
from urllib import parse
from urllib.parse import urlparse
import requests
import sys

#Reference for some of the helper functions. They are written and modified based on this tutorial https://www.youtube.com/watch?v=nRW90GASSXE&list=PL6gx4Cwl9DGA8Vys-f48mAH9OKSUyav0q
class Link_helper(HTMLParser):

    def __init__(self, base_url):#, page_url, curr_level):
        super().__init__()
        self.base_url = base_url
        #self.page_url = page_url
        # using set to record children, since it does not allow duplication
        self.links = set()
    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)
        
    def page_links(self):
        return self.links

    def error(self, message):
        pass

    def curr_link(self):
        return self.base_url + self.page_url


# Each website is a separate project (folder)
def create_project_dir(directory):
    if not os.path.exists(directory):
        print('Creating directory ' + directory)
        os.makedirs(directory)


# Create queue and crawled files (if not created)
def create_data_files(project_name):
    queue = os.path.join(project_name , 'queue.txt')
    already_done = os.path.join(project_name,"already_done.txt")
    output = os.path.join(project_name,"temp.json")
    if not os.path.isfile(queue):
        write_file(queue, '')
    if not os.path.isfile(already_done):
        write_file(already_done, '')
    if not os.path.isfile(already_done):
        write_file(output, '')



# Create a new file
def write_file(path, data):
    with open(path, 'w') as f:
        f.write(data)


# Add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')


# Delete the contents of a file
def delete_file_contents(path):
    open(path, 'w').close()

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)

# Read a file and convert each line to set items
def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt') as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results

def file_to_list(file_name):
    results = list()
    with open(file_name, 'rt') as f:
        for line in f:
            #print(line)
            try:
                results.append(json.loads(line))
            except Exception as e:
                continue
        #    results.append(line)
    return results

# Iterate through a set, each item will be a line in a file
def set_to_file(links, file_name):
    with open(file_name,"w") as f:
        for l in links:
            f.write(l+"\n")

def get_last_modified(url):
	result = urlparse(url)
	if True if [result.scheme, result.netloc, result.path] else False:
		header = requests.head(url).headers
		if 'Last-Modified' in header:
			return header['Last-Modified']
		return ""
	else:
		return ""

#
#{ "title" : "a", "url" : "www.ucr.edu", "paragraph" : "pp", "link_name" : "aaa", "related_date" :[]}