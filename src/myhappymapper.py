#!usr/bin/python

#       myhappymapper.py
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


#FIXED:
    # - find_all
    # - prettify
#TODO
    # - Better HTML handling.
    # - Migrate to XMLReader. <striked>


#xml handling
from xml.sax import make_parser, parseString
from xml.sax.handler import ContentHandler

#htmlhandling
try:
    from html.parser import HTMLParser as HP 
except ImportError:
    import html.parser as HP

import urllib2 as ulib2
import sys, traceback 

class Item(object):

    def __init__(self, name=None, content=None):

        self.itsname=name
        self.content=content #tag only.
        self.value=content #attr only.

    desc=lambda self: self.itsname + " => " + self.content
    #__repr__=__str__=lambda self: str(self.content)
    def __str__(self):
        return "{Tag:%s , content: %s}"%(self.itsname, self.content)
    __repr__=lambda self: self.content

class Attr(Item):
    pass


class AttrsDict(dict):
    
    def getNames(self):
        return list(self.keys())

class Tag(Item):


    def __init__(self, name=None, content="NO_CONTENT", attrs=None, parent=None):
        super(Tag, self).__init__(name, content)
        self._innertags=[] #Has many tags..
        self._attrs=[]
         #Has many attrs..
        if attrs:
            self.add_attrs(attrs)
        self.parent=parent
        self.nextSib=None
        self.prevSib=None
        self.current_tag=self
    

    innertags=lambda self: self._innertags
    first=lambda self: self._innertags[0]
 
    def __iter__(self):
        for t in self._innertags:
            yield t

    def has_tag(self, tagName):
        return any(tag.itsname==tagName for tag in self._innertags)

    def __getitem__(self, k):
        if isinstance(k, int):
            return self._innertags[k]
        elif isinstance(k, str):
                if hasattr(self, k):
                    return getattr(self, k)
        else:
            raise IndexError
    
    def iter_innertags(self):

        for t in self._innertags:
            yield t

    def get_tag(self, tagName):
        for tag in self._innertags:
            if tag.itsname==tagName:
                return tag

    def get_tags(self, tagName):
        return [tag for tag in self._innertags if tagName==tag.itsname]


    def add_tag(self, tag):
        """adds a Tag instance"""
        if len(self._innertags):
            self._innertags[-1].nextSib=tag
            tag.prevSib=self._innertags[-1]
        #self._innertags[-1].nextSib=tag
        self._innertags.append(tag)
        setattr(self,tag.itsname, tag)
        self.current_tag=tag

    def isvalidattr(self, attrname):
        if attrname in dir(self):
            return False
        return True

    def add_attr(self, attr):
        """adds an Attr instance."""

        self._attrs.append(attr)
        setattr(self, attr.itsname, attr.content)

        #Handle it later
        # if name is in dir then setattribute name to name0 ? 
        # and so on...
        #
    
    def set_attrs(self, attrs):

        for name in attrs.getNames():
            #print "SETTING %s TO %s" %(name, attrs.get(name))
        
            self.add_attr(Attr(name, attrs.get(name)))

    def iter_attrs(self):
        """iter_attrs() -> Yields attributes of Tag self."""
        for attr in self._attrs:
            yield attr.itsname, attr.value

    #verbosity only usage...
    def print_attrs(self):
        """Prints attributes of Tag self"""
        print("\t**Attrs: ")
        for name, value in self.iter_attrs():
            print("\t", name, " => ", value)

    def print_tags(self):
        """Prints inner tags of Tag self."""
        print("\t**Tags: ")
        for tag in self._innertags:
            #print "\t", tag.itsname, " => ", tag.content
            #print "\t", 
            tag.inspect_all()
    
    def as_xml(self):
        pass
                
    def inspect_all(self):
        """Prints attrs and tags (an alias for print_attrs and print_tags)"""
        print("****IN Tag: ", self.itsname)
        if self.parent:
            print("Parent: ", self.parent.itsname)
        else:
            print("Root tag.")
        self.print_attrs()
        self.print_tags()
        print("\tNEXT Sib of %s: %s"%(self.itsname, self.nextSib))
        print("\tPREV Sib of %s: %s"%(self.itsname, self.prevSib))
        print("******ENDED: ", self.itsname)
        
    def prettify(self, level=0): 
        txt=""
        txt +=" "*level + "<%s>"%self.itsname
        if self.innertags():
            for tag in self.innertags():
                txt +="\n"
                txt += tag.prettify(level+1)
            txt +="\n"+" "*level + "</%s>\n"%self.itsname
        else:
           txt +=self.content + "</%s>"%self.itsname
        
        return txt
                      
        
    def just_xml(self):
        txt=""
        txt +="<%s>"%self.itsname
        if self.innertags():
            for tag in self.innertags():
                txt += tag.just_xml()
        else:
            txt+=self.content
        txt +="</%s>"%self.itsname
        return txt
        
        
    inspect_me=inspect_all #Backward compatibility
    attrs=property(fget=lambda self: self._attrs, fset=set_attrs)
    clean_content=property(fget= lambda self: self.content.strip())
    
    

#MixIn(XML/HTML)

class HandlerMixIn(object):
    
    def my_init(self):
                
        self._roottag=Tag()
        self._stack=[]
        self._inroot=False

    def on_start_tag(self, el, xattrs): #xattrs[attr]
        #HANDLING HTML...
        attrs=AttrsDict()
        if not hasattr(xattrs, 'getNames'):
            attrs=AttrsDict()
            for attr in xattrs:
                attrs[ attr[0] ]=attr[1]
        else:
            attrs=xattrs
        t=Tag()
        t.itsname=el
        t.attrs=attrs
        
        if not self._inroot:
            self._inroot=True
            self._roottag=t
            self._stack.append(self._roottag)
        else:
            self._stack.append(t)
    
    def on_characters(self, content):
        if self._stack:
            self._stack[-1].content=content.strip() or "has more tags.."
            
    
    def on_end_tag(self, el):
        try:
            popped=self._stack.pop()
            if self._stack:
                popped.parent=self._stack[-1]
                self._stack[-1].add_tag(popped)
        except Exception as ex:
            #index out of range, Don't bother.
            traceback.print_exc(file=sys.stdout)


#HTML: NOT READY
class HTMLDocumentHandler(HandlerMixIn, HP):

    def __init__(self):
        self.reset()
        self.my_init()
        self.currel=None

    root_tag=property(fget=lambda self: self._roottag)
    
    def handle_starttag(self, el, attrs):
        self.on_start_tag(el, attrs)

    def handle_data(self, content):
        self.on_characters(content)

    def handle_endtag(self, el):
        self.on_end_tag(el)
            
class XMLDocumentHandler(HandlerMixIn, ContentHandler):

    def __init__(self):
        self.my_init()

    root_tag=property(fget=lambda self: self._roottag)
    
    def startElement(self, el, attrs):
        self.on_start_tag(el, attrs)
        
    def characters(self, content):
        self.on_characters(content)

    def endElement(self, el):
        self.on_end_tag(el)


        
#use list(find_all) instead.
def _find_all(tagName,root):
    s=[]
    if tagName==root.itsname:
        s +=[root]
    else:
        if root.has_tag(tagName):
            s +=root.get_tags(tagName)
            #print "S: ", s
        else:
            for tag in root.innertags():
                x=find_all(tagName, tag)
                if x:
                    s +=x
    return s

#def find_all_(tagName,root):
#    
#    if tagName==root.itsname:
#        yield root
#    else:
#        if root.has_tag(tagName):
#            for x in root.get_tags(tagName):
#                yield x
#        else:
#            for tag in root.innertags():
#                for x in find_all(tagName, tag): #.next()
#                    if x: yield x


def find_all(tagName, root):
    if tagName==root.itsname:
        yield root

    #if root.has_tag(tagName):
    #    for tag in root.get_tags(tagName):
    #        yield tag
                
    for tag in root.innertags():
        for x in find_all(tagName, tag): #.next()
            if x: yield x


def find_one(tagName,root):
    try:
        return next(find_all(tagName, root))
    except:
        return None

def prettify(self, root, level=0):
    return root.prettify(level)

def get_handler(xml=True):
    if xml:
        return XMLDocumentHandler()
    else:
        return HTMLDocumentHandler()
        
def get_root(f, xml=True):

    dh=get_handler(xml)
    if xml:
        p=make_parser()
        p.setContentHandler(dh)
        p.parse(open(f))
    else:
        fh=open(f)
        src=fh.read()
        fh.close()
        dh.feed(src)
    return dh.root_tag


def get_root_document(doc, xml=True):
    
    dh=get_handler(xml)
    if xml:
        #p=make_parser()
        parseString(doc, dh)
    else: #HTML
        dh.feed(doc)
    return dh.root_tag

get_root_string=get_root_document

def get_src(link):
    return ulib2.urlopen(link).read()


def simple_xml_test():
    txt="""<?xml version="1.0"?>
<computer>
    <library>
        <books>
            <book id="1" class="programming">
                <name>Introduction to Python</name>
                <author>Ahmed Youssef</author>
                <price>80</price>
            </book>
            <book id="2" class="programming">
                <name>Introduction to Java</name>
                <author>Wael Muhammed</author>
                <price>130</price>
            </book>
            <book id="3" class="programming">
                <name>Introduction to Ruby</name>
                <author>Ahmed Youssef</author>
                <price>70</price>
            </book>
            <book id="4" class="programming">
            <name>Introduction to Linux Programming</name>
            <author>Ahmed Mostafa</author>
            <price>90</price>
            </book>
        </books>
    </library>
</computer>
"""
    root=get_root_document(txt)
    root.inspect_all()
    print(root.prettify())
    bookslist=list(book.name.content for book in find_all("book", root))
    total=sum(list(int(price.clean_content) for price in find_all("price", root)))
    print("TOTAL: ", total)
    print(bookslist)

def simple_html_text():
    #
    txt="""
    <html>
        <body>
            <a href="/">parent directory</a>        01-feb-2009 03:26      -  
            <a href="csisomountpacks.tar.gz">csisomountpacks.tar.gz</a>  27-sep-2008 20:05    16k  
            <a href="practical_guide_to_use_ubuntu_linux.pdf">practical_guide_to_u..&gt;</a> 10-dec-2008 18:35   3.9m  
            <a href="drafts/">drafts/</a>                 04-mar-2009 06:17      -  
            <a href="extpython.pdf">extpython.pdf</a>           16-aug-2008 03:41   101k  
            <a href="fpctut.pdf">fpctut.pdf</a>              16-aug-2008 03:34   234k  
            <a href="gqamoos.pdf">gqamoos.pdf</a>             03-dec-2008 05:09   534k  
            <a href="gtksharptutorial/">gtksharptutorial/</a>       12-feb-2009 13:47      -
        </body>
            
    </html>
    """

    
    root=get_root_string(txt, False)
    #root.inspect_all()
    links=list([ a.href for a in find_all('a', root) ])
    print(links)
    
if __name__=="__main__":

    try:
        simple_xml_test()
        #simple_html_text()
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
