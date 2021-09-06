# Web Crawler with Search Engine
 A basic crawler that crawls about 50 MB of data from a given URL

 There is a main class Crawler, which takes in one url, find all a tag href links and store them to a queue.txt file. The txt data from this URL are written into temp_data.json.
 In the main function, the queue.txt file are checked for size, if it is not empty, then one URL is taken from the file, and feed into the crawler class.
 This process keeps repeating until the Crawler has crawled enough pages or exhausted all links from the queue.txt file. Then data from temp_data.json are tranformed into json format and dumped into crawl_results.json file.

Needed Modules for Crawler:
1. pip install bs4
2. pip install requests
3. pip install lxml

Comments:
If Ctrl + C might not exit the program, use Ctrl + Z instead.(In my testing, Ctrl + C works in windows, but sometimes not in linux)

Instruction:
To run the Crawler under cmd(windows):
1. `$ .\crawler.bat [seed_file] [pages_to_crawl] [level] [Output_file_directory_name] [number of threads you want to use] 
 
To run Indexer:
have elasticsearch installed locally.

Since the program run under the assumption that elasticsearch is installed locally, please start the service by:
1. go under elasticsearch's root folder
2. [elasticsearch_directory]\bin\elasticsearch-service.bat start.
3. After service started, under project's root folder
4. cd .\app\
5. npm install
6. cd ..
7. ./indexer [output_directory]

To see Part 3 web application:
After running ./indexer [output_directory], go to url : http://localhost:3001/




