__author__ = 'minfon'
#-*- coding: utf-8 -*-

import urllib
import urllib2
from sgmllib import SGMLParser
import MySQLdb
import sys
import threading
import pycurl
import os

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import textwrap

webroot = "https://www.kickstarter.com/discover/categories/technology?ref=category"
linkroot = "http://www.kickstarter.com"
html_start ="<html> <head> <meta content=\"text/html; charset=ISO-8859-1\" http-equiv=\"content-type\"> </head> <body>"
html_end = "</body> </html>"
#  解析  列表
#  第 1 級
class kickstarter_root_HTMLParser(SGMLParser):
    def __init__(self , video_download ):
        SGMLParser.__init__(self)

        self.video_download = video_download
        self.div_1_tag_unclosed = 0
        self.catalog_capture = 0
        self.catalog_key = ''
        self.catalog_link = ''

    def start_div(self,attrs):
        for name,value in attrs:
            if( name=='class' and value == 'header item'):
                self.div_1_tag_unclosed = 1
            if( name=='class' and value == 'project-card relative'):
                self.div_1_tag_unclosed = 1
           # else:
           #     self.div_1_tag_unclosed = 0
           #     self.catalog_capture = 0

    def end_div(self):
        self.div_1_tag_unclosed = 0

    def start_a(self,attrs):
        for name,value in attrs:
            #if( self.div_1_tag_unclosed == 1 and name=='data-category'):
            #    self.catalog_key = value;
            #elif( self.div_1_tag_unclosed == 1 and  name=='href'):
             if( self.div_1_tag_unclosed == 1 and  name=='href'):
                self.catalog_link = linkroot + value +"/";
               # print self.catalog_key

                print self.catalog_link

                try:
                     httpopen = urllib2.urlopen( self.catalog_link )
                     content2 = httpopen.read()
                     s1 = content2.find('<div class="short_blurb py2 pl1 pr1">')
                     s2 = content2.find('<div class="NS-projects-faqs" id="project-faqs">')
                     dd = html_start + content2[s1 : s2] + html_end
                     #print dd
                     desp = kickstarter_projectcase_HTMLParser( content2, dd , self.video_download )
                     desp.feed(content2)
                except urllib2.HTTPError, e:
                      print " ******** Http Access Denied. ******* "
                      #print e.fp.read()

               # content2 = myurl().urlopen( self.catalog_link )
               # desp = quirky_home_HTMLParser( self.catalog_key )
               # desp.feed(content2)


    def end_a(self):
        self.catalog_key = ''
        self.catalog_link = ''

    def handle_data(self, data):
        if( self.div_1_tag_unclosed == 1):
            if( data == 'Shop By Category'):
                self.catalog_capture = 1


#  解析  列表
#  第 2 級
class kickstarter_projectcase_HTMLParser(SGMLParser):
    def __init__( self , linkaddr , detail_content , video_download):
        SGMLParser.__init__(self)

        self.linkaddr = linkaddr
        self.detail_content = detail_content
        self.video_download = video_download
        self.title = ''
        self.description = ''
        self.type = ''
        self.author = ''
        self.location = ''
        self.thumbnail = ''
        self.video = ''
        self.p_1_tag_unclosed = 0
        self.a_1_tag_unclosed = 0
        self.a_2_tag_unclosed = 0
        self.h2_1_tag_unclosed = 0
        self.span_1_tag_unclosed = 0
        self.li_1_tag_unclosed = 0
        self.li_2_tag_unclosed = 0
        self.div_1_tag_unclosed = 0
        self.meta_1_tag_unclosed = 0

    def start_h2(self,attrs):
        for name,value in attrs:
            if( name=='class' and value == 'mb1'):
                self.h2_1_tag_unclosed = 1

    def end_h2(self):
        self.h2_1_tag_unclosed = 0

    def start_span(self,attrs):
            for name,value in attrs:
                if( name=='class' and value == 'creator'):
                    self.span_1_tag_unclosed = 1

    def end_span(self):
        self.span_1_tag_unclosed = 0

    def start_li(self,attrs):
        for name,value in attrs:
            if( name=='class' and value == 'location mr2'):
                self.li_1_tag_unclosed = 1
            if( name=='data-project-parent-category' and value == 'Technology'):
                self.li_2_tag_unclosed = 1



    def end_li(self):
        self.li_1_tag_unclosed = 0
        self.li_2_tag_unclosed = 0

    def start_a(self,attrs):
            for name,value in attrs:
                if( name=='class' and value == 'green-dark'):
                    self.a_1_tag_unclosed = 1
                if( name=='data-modal-class' and value == 'modal_project_by'):
                    self.a_2_tag_unclosed = 1

    def end_a(self):
        self.a_1_tag_unclosed = 0
        self.a_2_tag_unclosed = 0


    def start_p(self,attrs):
        for name,value in attrs:
            if( name=='class' and value == 'h3'):
                self.p_1_tag_unclosed = 1

    def end_p(self):
        self.p_1_tag_unclosed = 0


    def start_meta(self,attrs):
        for name,value in attrs:
            if( name=='property' and value == 'og:description'):
                self.meta_1_tag_unclosed = 1
            if( self.meta_1_tag_unclosed == 1 and name=='content' ):
                    self.meta_1_tag_unclosed = 0
                    self.description = value
                    print self.description

    def end_meta(self):
        self.meta_1_tag_unclosed = 0


    def start_div(self,attrs):
        for name,value in attrs:
            if( name=='data-image'):
                self.thumbnail = value

                url_0 = value.split('?')[:-1]
                url_1 = url_0[0].split('https')[1:]
                url_2 = value.split('?')[1:]
                jpgfile = url_2[0] +".jpg"
                if url_1[0].strip()=='':
                    link_1 = url_0[0]
                    download_one_file( link_1 , jpgfile  )
                else:
                    link_1 = 'http'+url_1[0]
                    download_one_file( link_1 , jpgfile)

                #self.thumbnail = value
                self.thumbnail = jpgfile

            if( name=='data-video-url'):
                self.video = value
                print self.video
                if( self.video_download == 1 ):
                    download_one_file(self.video, '')
                cursor = db.cursor()
                para = (self.type, self.title, self.description, self.author, self.location,self.detail_content, self.thumbnail ,self.video )
                cursor.execute(query_1,para)    #write to MySQL database
                db.commit()

    def handle_data(self, data):
        if( self.h2_1_tag_unclosed == 1 and self.a_1_tag_unclosed == 1 ):
            data1 = data.rstrip()
            data2 = data1.lstrip()
            print data2   # Project Title
            if data2.strip() !='':
                self.title = self.title + data2

        if( self.span_1_tag_unclosed == 1 and self.a_2_tag_unclosed == 1 ):
            data1 = data.rstrip()
            data2 = data1.lstrip()
            print data2   # Project Creator
            self.author = data2

        if( self.li_1_tag_unclosed == 1 and data != '\n' ):
            data1 = data.rstrip()
            data2 = data1.lstrip()
            print data2  # Location
            self.location = data2

        if( self.li_2_tag_unclosed == 1 and data != '\n' ):
            data1 = data.rstrip()
            data2 = data1.lstrip()
            print data2  # Project Type
            self.type = data2



import StringIO
class myurl:
    def __init__(self):
        self.c1 = ''
        self.c1 = pycurl.Curl()
        self.c1.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c1.setopt(pycurl.MAXREDIRS, 10)
        #self.c1.setopt(pycurl.CONNECTTIMEOUT, 60)
        #self.c1.setopt(pycurl.TIMEOUT, 300)
        #self.c1.setopt(pycurl.USERAGENT, "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)")
        #self.c1.setopt(pycurl.PROXY, 'http://10.36.6.68:3128')
        #self.c1.setopt(pycurl.PROXYUSERPWD, '00011:mf2222')
        #self.c1.setopt(pycurl.PROXYAUTH, pycurl.HTTPAUTH_ANY)  # or HTTPAUTH_DIGES or HTTPAUTH_BASIC or HTTPAUTH_NTLM or HTTPAUTH_ANY

    def urlopen(self, url):
        self.c1.setopt(pycurl.URL, url )

        html  = StringIO.StringIO()
        self.c1.setopt(pycurl.WRITEFUNCTION, html.write)
        #self.c1.setopt(pycurl.WRITEFUNCTION, c1_data.write)

        self.c1.perform()
        return html.getvalue()


def  display_progress( i, end_val, bar_length=20):
            percent = float(i) / end_val
            hashes = '#' * int(round(percent * bar_length))
            spaces = ' ' * (bar_length - len(hashes))
            sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
            sys.stdout.flush()
#  For test === progress bar ===
#for i in range(100):
#    threading._sleep(0.2)
#    display_progress(i,100,20)

def  download_one_file( url , file_name_2 ):

        if file_name_2.strip() !='':
            file_name = file_name_2
        else:
            file_name = url.split('/')[-1]

        open_OK = 0
        try:
            u = urllib2.urlopen(url)
            open_OK = 1
        except urllib2.HTTPError, e:
            print " ******** Access Denied. ******* "
        except urllib2.URLError:
            print " ******** Http Timeout Error! ******* "

        if(  open_OK == 1):
            f = open(file_name, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Downloading: %s Bytes: %s" % (file_name, file_size)

            file_size_dl = 0
            block_sz = 16384
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                f.write(buffer)
                display_progress(file_size_dl,file_size,20)

            f.close()
            print '\n'

#urllib.urlretrieve ("http://xxx.jpg", "xxxx.jpg")



print u"開始解析 www.kickstarter.com"
#========= PROXY ===============
'''
#proxy = urllib2.ProxyHandler({'http': r'http://00011:Mf3333@10.36.6.66:3128'})
proxy = urllib2.ProxyHandler({'http': r'http://10.191.131.30:3128'})
auth = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
urllib2.install_opener(opener)
'''


'''
# create a password manager
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
# If we knew the realm, we could use it instead of None.
#top_level_url = "http://10.191.131.19:3128"
top_level_url = "http://10.36.6.68:3128"
password_mgr.add_password(None, top_level_url, "00011", "Mf3333" )

proxy_handler = urllib2.ProxyHandler({"http":top_level_url })
handler = urllib2.HTTPBasicAuthHandler(password_mgr)
#handler = urllib2.AbstractDigestAuthHandler(password_mgr)
# create "opener" (OpenerDirector instance)
opener = urllib2.build_opener(handler)

# use the opener to fetch a URL
#opener.open(a_url)

# Install the opener.
# Now all calls to urllib2.urlopen use our opener.
urllib2.install_opener(opener)
'''




'''
passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, 'http://10.191.131.19:3128/', 0, 0)
#passman.add_password(None, 'http://10.191.131.19:3128/', '00011', 'Mf3333')
# use HTTPDigestAuthHandler instead here
authhandler = urllib2.HTTPDigestAuthHandler(passman)
#authhandler = urllib2.ProxyDigestAuthHandler(passman)
#authhandler = urllib2.AbstractDigestAuthHandler(passman)

#opener = urllib2.install_opener(auth_NTLM)
opener = urllib2.build_opener(authhandler)
#opener = urllib2.install_opener(authhandler)
'''




db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="0000", db="kickstarter",charset='utf8')
query_1 = "insert ignore into projects( type,title,description,author,location,content,thumbnail,video ) values(%s,%s,%s,%s,%s,%s,%s,%s)"

video_download = 0
content1 = urllib2.urlopen( webroot )
#print content1.read()
#content1 = myurl().urlopen( webroot )
parse1 = kickstarter_root_HTMLParser( video_download )
parse1.feed(content1.read())
db.close()


'''
text2 = "The Dart by Precision Touch offers a fine tip stylus with one of the smallest tips available at only 2mm using electronic circuitry."
text = "由于考虑到应用程序体验不佳，为确保准确可靠的触摸以及屏幕上各项图标元素之间的距离，早期乔布斯是极力反对10英寸以下的平板电脑，特别指出7英寸规格。乔布斯当时在一次财报会议上说：“7英寸两边不讨好，对于智能手机来说太大，对于苹果iPad来说太小。”不过，2011年苹果内部高管多次向乔布斯提出研发7英寸iPad的想法后，其实乔布斯内心已认同了这个思路，毕竟那时Android小尺寸平板的市场表现上已有了一定的起色，只是乔布斯不希望苹果进入低端平板电脑市场"
h = 30
w = 500
font = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc",28) # for Mac OSX Chinese
#font = ImageFont.truetype("/System/Library/Fonts/Helvetica.dfont",28)  # for Mac OSX English
img=Image.new("RGBA", (800,400),(128,128,255))
draw = ImageDraw.Draw(img)
#lines = textwrap.wrap(text, width = 40)
lines = textwrap.wrap(unicode(text,'utf-8'), width = 28 )
y_text = h
for line in lines:
    width, height = font.getsize(line)
    draw.text(((w - width)/2 +150, y_text), line, font = font ,fill="#55ff88")
    #draw.text(((w - width)/2 + 200, y_text),unicode('你好','utf-8'),(255,255,128),font=font)
    y_text += height
draw = ImageDraw.Draw(img)
img.save("3.png")
'''
