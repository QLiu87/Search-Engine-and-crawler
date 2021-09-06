from helper import *
from urllib.request import urlopen
import time
import requests
import urllib.robotparser
from bs4 import BeautifulSoup
import json
import os
from queue import Queue
import sys
import threading
import signal

class LockingCounter():
    def __init__(self):
        self.lock = threading.Lock()
        self.count = 0
    def increment(self):
        with self.lock:
            self.count += 1

list_json = list()
level_lookup_table = dict()
MAX_THREADS = 2
#exit conditions: 1. no more links to crawl 2. reached links limit 3. reached level limits and no more links to crawl 4. enough data(50 mbs)
class crawler:
    queue = set()
    already_done = set()
    base_url = ""
    directory_name = "output"
    #robots.txt limitations
    request_delay = 1 #defalt of 1 second
    rb = urllib.robotparser.RobotFileParser()
    #level
    curr_url = ""
    level_limit = 5

    def __init__(self, level_limit, seed, dir):
        self.directory_name = dir + "/"
        create_project_dir(self.directory_name)
        create_data_files(self.directory_name)
        self.queue = file_to_set(seed)
        #print(self.queue)
        self.already_done = file_to_set(self.directory_name + "/already_done.txt")
        self.base_url = next(iter(self.queue))
        #level 
        level_lookup_table[self.base_url] = 1
        self.curr_url = self.base_url
        self.level_limit = level_limit
        #init_robot
        self.init_robots()
        self.crawl(self.base_url)
        

    def crawl(self, base_url):
        if base_url not in self.already_done:
            try:
                if level_lookup_table[base_url] > self.level_limit:
                    self.queue.remove(base_url)
                    self.already_done.add(base_url)
                    return
            except Exception as e:
                self.queue.remove(base_url)
                self.already_done.add(base_url)
            try:
                #default url
                print("Crawling --------")
                url = base_url
                self.curr_url = base_url
                delay = 0
                if delay < self.request_delay:
                    time.sleep(1)
                text = requests.get(url).text
                finder = Link_helper(base_url)
                finder.feed(text)
                self.get_data(text)
                #print(len(finder.page_links()))
                self.queue_append(finder.page_links())
                if base_url in self.queue:
                    self.queue.remove(base_url)
                self.already_done.add(base_url)
                #increment the count for number of pages crawled
                
                set_to_file(self.queue, self.directory_name + "/queue.txt")
                set_to_file(self.already_done, self.directory_name + "/already_done.txt")
            except Exception as e:
                print(str(e))
                if base_url in self.queue:
                    self.queue.remove(base_url)
            #update queue and already_done
            
            
            
        #print(finder.page_links())
    
    def queue_append(self, links):
        #print("Appending")
        for url in links:
            #print(url)
            if url in self.queue or url in self.already_done:
                #print("In continue")
                continue
            if self.rb.can_fetch("*", url):
                #print("Adding to queue")
                # filling level look up table 
                try:
                    curr_level = level_lookup_table[self.curr_url] + 1
                    level_lookup_table[url] = curr_level
                except Exception as e:
                    print(str(e))
                    level_lookup_table[url] = 1
                self.queue.add(url)
            
    def init_robots(self):
        print("Checking Robots.txt")
        self.rb.set_url(self.base_url + "/robots.txt")
        self.rb.read()
        if self.rb.crawl_delay("*" != None):
            #print(self.rb.crawl_delay("*"))
            self.request_delay = self.rb.crawl_delay("*")
             
    def get_data(self, text):
        soup = BeautifulSoup(text, "lxml")
        url_json = dict()
        url_json["title"] = soup.title.string
        #url_json["link_title"] = dict()
        #url_json["img_info"] = dict()
        url_json["page_url"] = self.curr_url
        url_json["body"] = ""
        #stores all a tag contents
        counter = 0
        #for node in soup.findAll('a'):
        #    url_json["link_title"]["link"+ str(counter)] = "".join(node.findAll(text = True))
        #    counter += 1
        #stores all p tag contents
        temp_body = ""
        #print(soup.find_all('p'))
        for node in soup.find_all('p'):
            if node.string != None:
                temp_body += node.string
        # stores all img text contents and their src url
        for node in soup.find_all('h2'):
            if node.string != None:
                temp_body += node.string
        for node in soup.find_all('h3'):
            if node.string != None:
                temp_body += node.string
        url_json["body"] = temp_body
        #counter = 0
        #for node in soup.find_all('img'):
            #print(node.get("alt"))
        #    temp_img_info = {"text" : str(node.get('alt')), "img_link" :str(node.get('src'))}
        #    url_json["img_info"]["img"+ str(counter)] = temp_img_info
        #    counter += 1
        url_json["last_modified"] = get_last_modified(self.curr_url)
        append_to_file(self.directory_name + "/temp_data.json", json.dumps(url_json))
        #list_json.append(url_json)
        return

def work():
    on = True
    while on:
        url = q.get()
        if counter.count >= pages_to_visit:
            output = file_to_list(c.directory_name + "/temp_data.json")
            write_file(c.directory_name + "/crawl_results.json", json.dumps(output))
            delete_file_contents(c.directory_name + "/temp_data.json")
            delete_file(c.directory_name + "/temp_data.json")
            #print("here")
            os.kill(os.getpid(), signal.SIGINT)
            sys.exit()
        c.crawl(url)
        counter.increment()
        print(f"Current count is {counter.count}")
        q.task_done()
        if exit_event.is_set():
            on = False
    os.kill(os.getpid(), signal.SIGINT)
    sys.exit()

def create_jobs():
    if exit_event.is_set():
            os.kill(os.getpid(), signal.SIGINT)
    for link in file_to_set(c.directory_name + '/queue.txt'):
        q.put(link)
    q.join()
    crawl()

def crawl():
    queued_links = file_to_set(c.directory_name + '/queue.txt')
    if len(queued_links) > 0:
        create_jobs()

def signal_handler(signum, frame):
    exit_event.set()
#-----------------code starts here
#default values

q = Queue()
global pages_to_visit
max_level = 3
seed_file = ""
output_directory = ""
exit_event = threading.Event()

if len(sys.argv) - 1 < 5:
    print("./crawler.sh < Fileseed.txt > < pages : 10000 > < hops away : 6 > <output−dir > <number of threads USE WITH CAUTION")
else:
    seed_file = sys.argv[1]
    pages_to_visit = int(sys.argv[2])
    max_level = sys.argv[3]
    output_directory = sys.argv[4]
    MAX_THREADS = int(sys.argv[5])
print(sys.argv)
file_to_set(seed_file)
counter = LockingCounter()


signal.signal(signal.SIGINT, signal_handler)
c = crawler(max_level, seed_file, output_directory)
for _ in range(MAX_THREADS):
        
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

crawl()


# while os.path.getsize(c.directory_name + "/queue.txt") > 0 and test == 2:
#     upcoming_links = file_to_set(c.directory_name + "/queue.txt")
#     for link in upcoming_links:
#         upcoming_links = file_to_set(c.directory_name + "/queue.txt")
#         if page_counter > pages_to_visit or os.path.getsize(c.directory_name + "/output.json") > 43000000:#sys.getsizeof(list_json) > 50000000:
#            # write_file(c.directory_name + "/output.json", json.dumps(list_json))
#             output = file_to_list(c.directory_name + "/output.json")
#             write_file(c.directory_name + "/test.json", json.dumps(output))
#             sys.exit()
#         print(link)
#         print(os.path.getsize(c.directory_name + "/output.json"))
#         print(page_counter)
#         c.crawl(link)

#         page_counter += 1




# Check if there are items in the queue, if so crawl them





