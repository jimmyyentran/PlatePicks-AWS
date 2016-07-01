#  import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
from nameParser import NameParser
import grequests
from dynamodb import DB
#  import unirest
#  from requests_futures.sessions import FuturesSession


class Crawler(object):
    # data is passed in as url as key and respective info: {url, location info}
    def __init__(self, data):
        self.urls = data;
        self.parse = NameParser("unwantedWords.txt")
        self.information = []
        self.url_to_id_lookup = {}
        #  self.session = FuturesSession()
        #  tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    #Take in a list of url
    #  @profile
    def query(self,limit):
        self.limit = limit
        async_list = []

        for key in self.urls:
            url = "http://www.yelp.com/biz_photos/"+key+"?tab=food&start=0"
            self.url_to_id_lookup[url] = key #add url as key
            action_item = grequests.get(url, hooks = {'response' :
                    self.extract_food_names
            })
            async_list.append(action_item)
        grequests.map(async_list, exception_handler=self.exception_handler)
        return self.information

    # allow grequests to output errors
    def exception_handler(self, request, exception):
        print "Failed %s" % (request)
        print(exception)

    def query_dynamodb(self, response, **kwargs):
        url = response.url
        foods = self.db.get_item()
        for food in foods:
            print(food)

    #  @profile
    def extract_food_names(self, response, **kwargs):
        #  print(vars(response))
        url = response.url
        firstUrl = url
        html = response.content
        #  url = args['url']
        #  html = args['response']
        #  soup = BeautifulSoup(html, 'html.parser')
        # parse for the number of pages
        #  for sz in soup.find("div", "page-of-pages arrange_unit arrange_unit--fill"):
            #  sz = int(sz[sz.find("of") + 2:])

        visited = [url]  # keeps track of visited urls
        pics = []
        pics_id = []
        com = []
        flag = True # if reached limit

        sz = 1 #just query on the first page
        for i in range(sz):
            if not flag: break # if reached limit then break this loop
            url.find("&start")
            url = url[:url.find("&start")] + "&start=" + str(30 * i)
            i += 1

            # parse the url for html code
            #  source_code = requests.get(url)  # variable = requests.get(url)
            #  html = source_code.text  # get source code of page
            soup = BeautifulSoup(html, 'lxml')
            #find all the links thats are img urls
            for link in soup.findAll('img', attrs={'height' : '226'}):
                #  print(link)
                if len(pics_id) ==(self.limit):
                    flag = False
                    break
                #  link['src'] = urllib.parse.urljoin(url, link['src'])
                link['src'] = urljoin(url, link['src'])
                if '#' not in link['src']:
                    if link['src'] not in visited:
                        visited.append(link['src'])
                        if "bphoto" in link['src']:
                            fake = link['alt']
                            fake = fake[fake.find("States.") + 7:]

                            # removes majority of the bad comments
                            if " United States" not in fake:
                                prettified = self.parse.parse_name(fake.rstrip().lstrip()) # strip
                                if prettified is not None:
                                    com.append(prettified)
                                    fake = link['src']
                                    fake = fake[fake.find("bphoto/") + 7:fake.rfind("/258s.jpg")]
                                    #  print(fake)
                                    #  fake = fake[fake.find("bphoto/") +
                                            #  7:fake.rfind("/o.jpg")]
                                    #  print(fake)
                                    pics.append(link['src'].replace("/258s", "/o"))
                                    pics_id.append(fake)

        # prints the comments, pic_id and the url of the picture
        for pic, coms, pic_id in zip(pics, com, pics_id):
            to_be_returned = dict(url=pic, food_id=pic_id, name=coms)

            # use dictionary lookup
            to_be_returned['location']=self.urls[self.url_to_id_lookup[firstUrl]]
            self.information.append(to_be_returned)
