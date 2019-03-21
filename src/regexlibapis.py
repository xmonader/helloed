#!usr/bin/python

#       regexlib.py
#       
#       Copyright 2009 ahmed youssef <xmonader@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import http.client
from .myhappymapper import get_root_string, find_all, find_one

HOST="regexlib.com"
URL="http://regexlib.com/webservices.asmx"

#check: http://www.lyonsreg.com/products/python.asp
def soap_post(action, xml):
    h=http.client.HTTPConnection(HOST, 80)
    headers={
        'Host':HOST,
        'Content-Type':'text/xml; charset=utf-8',
        'Content-Length':len(xml),
        'SOAPAction':'"%s"' % action,
        }
    h.request("POST", URL, xml, headers)
    result=h.getresponse().read()

    return result

def create_listregexp(keyword, regex_substring, min_rating, howmanyrows):
    xml="""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <listRegExp xmlns="http://regexlib.com/webservices.asmx">
      <keyword>%s</keyword>
      <regexp_substring>%s</regexp_substring>
      <min_rating>%d</min_rating>
      <howmanyrows>%d</howmanyrows>
    </listRegExp>
  </soap12:Body>
</soap12:Envelope>"""%(keyword, regex_substring, min_rating, howmanyrows)
    return soap_post("http://regexlib.com/webservices.asmx/listRegExp", xml)

def create_getregexpdetails(id_):
    xml="""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <getRegExpDetails xmlns="http://regexlib.com/webservices.asmx">
      <regexpId>%d</regexpId>
    </getRegExpDetails>
  </soap12:Body>
</soap12:Envelope>"""%id_
    return soap_post("http://regexlib.com/webservices.asmx/getRegExpDetails"
, xml)

def create_listallasxml(maxrows):
    xml="""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ListAllAsXml xmlns="http://regexlib.com/webservices.asmx">
      <maxrows>%d</maxrows>
    </ListAllAsXml>
  </soap:Body>
</soap:Envelope>"""%maxrows
    return soap_post("http://regexlib.com/webservices.asmx/ListAllAsXml"
, xml)

def get_details_of_regexp(id_):
    xml=create_getregexpdetails(id_)
    print(xml)
    print("*"*20)
    root=get_root_string(xml)
    print(root.prettify())
    regexpdetails=find_one("getRegExpDetailsResult", root)
    return regexpdetails

def get_expressions_of(keyword, regex_substring, min_rating, howmanyrows):
    xml=create_listregexp(keyword, regex_substring, min_rating, howmanyrows)
    root=get_root_string(xml)
    lst=list(find_all("Expressions", root))
    return lst if len(lst)==howmanyrows else lst[:howmanyrows]

if __name__=="__main__":
    expslist=get_expressions_of("Email", "", 5, 5)
    for exps in expslist:
        print("*"*20)
        print(exps.Pattern)

