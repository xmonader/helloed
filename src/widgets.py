#       widgets.py
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

import sys, os
from os.path import exists, dirname
import StringIO
import inspect

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree 



#gtk
import pygtk
pygtk.require('2.0')
import gtk
from pyconsole import Console
from terminal import GeditTerminal
try:
    from myhappymapper import get_root_document
    have_happymapper=True
except ImportError:
    have_happymapper=False
    


        

class FileBrowserTV(gtk.TreeView):
    
    def __init__(self, path=os.getcwd()):
        super(FileBrowserTV, self).__init__()
        self._path=path
        self.search_pred=lambda x: x
        self._init_tv()
        self._update_view()
        self.set_enable_search(True)


    def set_path(self, path):
        self._path=path
        self._update_view()
        
    path=property(fget=lambda self: self._path, fset=set_path)
    
    def _init_tv(self):
        filescolumn=gtk.TreeViewColumn()
        filescolumn.set_title("Files")
        
        iconrenderer=gtk.CellRendererPixbuf()
        cellrenderer=gtk.CellRendererText()
        
        filescolumn.pack_start(iconrenderer, True)
        filescolumn.add_attribute(iconrenderer, 'stock_id', 0)
        filescolumn.pack_start(cellrenderer, True)
        filescolumn.add_attribute(cellrenderer, "text", 1)
        
        self.append_column(filescolumn)
    
    update_view=lambda self: self._update_view()
    def _update_view(self):
        self.model=None
        lstore=gtk.ListStore(str, str)
        flist=os.listdir(self.path)
        #flist.sort()
        dirs=[x for x in flist if os.path.isdir(self.path+os.path.sep+x)]
        files=[x for x in flist if os.path.isfile(self.path+os.path.sep+x)] 
        dirs.sort()
        files.sort()
        #print "FLIST:", flist
        #for f in flist:
        for f in dirs:
            fpath=self.path+os.path.sep+f
            #print "Dirs..."
            if os.path.isdir(fpath):
                #print "\tadding: ", f
                if self.search_pred(f):
                    lstore.append([gtk.STOCK_DIRECTORY, f])
                #flist.remove(f)
        
        #for f in flist:
        for f in files:
            #print "Files..."
            fpath=self.path+os.path.sep+f
            if os.path.isfile(fpath):
                #print "\tadding: ", f

                if self.search_pred(f):
                    lstore.append([gtk.STOCK_FILE, f])
                #flist.remove(f)
        self.set_model(lstore)
        
    def set_search_pred(self, pred=lambda x: x):
        self.search_pred=pred
        
    def go_up(self):
        self.set_path(os.path.dirname(self.path)) #set it to the parent.
    
    def go_home(self):
        if "win" in sys.platform:
            self.set_path("c:/")
        else:
            self.set_path("/home")
            
class PythonSourcePlugin(object):
    def __init__(self, modulepath=None):
        self.set_module_path(modulepath)
        
    def set_module_path(self, path):
        if path is not None and exists(path):
            self.name, suffix, mode, mtype=inspect.getmoduleinfo(path)
            sys.path.append(dirname(path))
            self.m=__import__(self.name)

    def get_classes(self):
        return inspect.getmembers(self.m, inspect.isclass) #[ (classname, class ) ]
    
    def get_methods_of(self, classname):
        return inspect.getmembers(classname, inspect.ismethod)
            
    def get_functions(self):
        return inspect.getmembers(self.m, inspect.isfunction)
        
    
class SourceCodeTreeView(gtk.TreeView):
    
    def __init__(self, clicked_callback=None):
        
        super(SourceCodeTreeView, self).__init__()
        self._init_tv()
        self.on_item_clicked=clicked_callback
        
    def _init_tv(self):
        sourcecolumn=gtk.TreeViewColumn()
        sourcecolumn.set_title("Source")
        
        cellrenderer=gtk.CellRendererText()
        sourcecolumn.pack_start(cellrenderer, True)
        sourcecolumn.add_attribute(cellrenderer, "text", 0)
        
        self.append_column(sourcecolumn)
        
    def set_language(self, lang):
        self.lang=lang
        self.update_view()
        
    def update_view(self):
        
        tstore=gtk.TreeStore(str)
        miter=tstore.append(None, ["Source"])
        
        for (classname, class_) in self.lang.get_classes():
            i=tstore.append(miter, [classname])
            for (methodname, _) in self.lang.get_methods_of(class_):
                tstore.append(i, [methodname])
        for (funcname, func_) in self.lang.get_functions():
            tstore.append(miter, [funcname])

        self.set_model(tstore)
   
   
class XMLTreeView(gtk.TreeView):

        
    def __init__(self, xml=None, clicked_callback=None):
        super(XMLTreeView, self).__init__()
        self._init_tv()
        self.set_xml(xml)
        self.on_item_clicked=clicked_callback
    
    def _init_tv(self):
        tagscolumn=gtk.TreeViewColumn()
        tagscolumn.set_title("Tags")
        
        cellrenderer=gtk.CellRendererText()
        tagscolumn.pack_start(cellrenderer, True)
        tagscolumn.add_attribute(cellrenderer, "text", 0)
        
        self.append_column(tagscolumn)
        
    def _get_string_stream(self, text):
        return StringIO.StringIO(text)
        
    def set_xml(self, xml):
        if xml is not None:
            self.xml=xml
            
            self.tree=etree.parse(self._get_string_stream(xml))
            self.root=self.tree.getroot()
            self.update_view()
            
    def update_view(self):
        
        tstore=gtk.TreeStore(str)
        miter=tstore.append(None, [self.root.tag])
        
        def update_iter_with_tag(tstore, iter, tag):
            for t in tag.getchildren():
                i=tstore.append(iter, [t.tag])
                #FIXME: better way maybe?
                if hasattr(t.text, "strip"):
                    if t.text.strip():
                        tstore.append(i, [t.text])  
                else:
                    if t.text:
                        tstore.append(i, [t.text])  


                for attrname, attrvalue in t.attrib.items():
                    tstore.append(i, [attrname+  "="+attrvalue if attrvalue.strip() else ""])
                if len(t.getchildren())>0:
                    update_iter_with_tag(tstore, i, t)
                    
        update_iter_with_tag(tstore, miter, self.root)
        self.set_model(tstore)
            
if have_happymapper:
    class XMLTreeViewHM(gtk.TreeView):

            
        def __init__(self, xml=None, clicked_callback=None):
            super(XMLTreeView, self).__init__()
            self._init_tv()
            self.set_xml(xml)
            self.on_item_clicked=clicked_callback
        
        def _init_tv(self):
            tagscolumn=gtk.TreeViewColumn()
            tagscolumn.set_title("Tags")
            
            cellrenderer=gtk.CellRendererText()
            tagscolumn.pack_start(cellrenderer, True)
            tagscolumn.add_attribute(cellrenderer, "text", 0)
            
            self.append_column(tagscolumn)
            
        def set_xml(self, xml):
            if xml is not None:
                self.xml=xml
                self.root=get_root_document(xml)
                self.update_view()
                
        def update_view(self):
            
            tstore=gtk.TreeStore(str)
            miter=tstore.append(None, [self.root.itsname])
            
            def update_iter_with_tag(tstore, iter, tag):
                for t in tag.iter_innertags():
                    i=tstore.append(iter, [t.itsname])
                    if "no_content" not in t.clean_content.lower():
                        tstore.append(i, [t.clean_content])
                    for attr in t.attrs:
                        tstore.append(i, [attr.itsname+  "="+attr.value if attr.value.strip() else ""])
                    if len(t.innertags())>0:
                        update_iter_with_tag(tstore, i, t)
                        
            update_iter_with_tag(tstore, miter, self.root)
            self.set_model(tstore)
                
            
        
         
        
class SidePaneBrowser(gtk.VBox):
    
    def __init__(self, path=os.getcwd()):
        super(SidePaneBrowser, self).__init__(False, 0)
        self._init_comp(path)
        self.openfilecallback=None #function with filepath argument.
        
    def set_openfilecallback(self, callback):
        if callable(callback):
            self.openfilecallback=callback

    def _init_comp(self, path):
        
        self.tbar=gtk.Toolbar()
        self.tbar.set_style(gtk.TOOLBAR_ICONS)

        self.pathentry=gtk.Entry()
        self.pathentry.connect("key-press-event", self._on_keypressed)
        self.pack_start(self.pathentry, False, False, 5)
        
        self.refreshbtn=gtk.ToolButton("gtk-refresh")
        self.refreshbtn.connect("clicked", self._on_btnrefresh_clicked)
        
        self.gobtn=gtk.ToolButton("gtk-ok")
        self.gobtn.connect("clicked", self._on_btngo_clicked)
        
        self.upbtn=gtk.ToolButton("gtk-go-up")
        self.upbtn.connect("clicked", self._on_upbtnclicked)
        
        self.homebtn=gtk.ToolButton("gtk-home")
        self.homebtn.connect("clicked", self._on_homebtnclicked)
        
        self.tbar.insert(self.refreshbtn, 0)
        self.tbar.insert(self.upbtn, 1)
        self.tbar.insert(self.gobtn, 2)
        self.tbar.insert(self.homebtn, 3)
        
        scrolled=gtk.ScrolledWindow()
        self.fbtv=FileBrowserTV(path)
        self.pathentry.set_text(self.fbtv.path)
        self.fbtv.connect("row-activated", self._ontvitemclicked)
        scrolled.add(self.fbtv)
        
        self.pack_start(self.tbar, False, False, 0)
        self.pack_start(scrolled, True, True, 0)
        
        self.matchfilenameexpander=gtk.Expander("Match Filename:")
        self.pack_start(self.matchfilenameexpander, False, False, 2)
        
        self.matchfilenameentry=gtk.Entry()
        self.matchfilenameentry.connect("key-press-event", self._onmatchfilenameentry_keypressed)
        self.matchfilenameexpander.add(self.matchfilenameentry)
       
        #FIXME:
        self.matchfilename=""

    #FIXME:
    def _onmatchfilenameentry_keypressed(self, w, event):
        if gtk.gdk.keyval_name(event.keyval)=="Return": #Enter
            self.matchfilename=w.get_text()
            self.fbtv.set_search_pred(lambda x: self.matchfilename in x)
            self.fbtv.update_view()
        
    def _ontvitemclicked(self, widget, *args):
        selection=self.fbtv.get_selection()
        model, selection_iter=selection.get_selected()
        
        if selection_iter:
            item=model.get_value(selection_iter, 1) #iter, column
            try:
                if item=="..":
                    self.fbtv.go_up()
                    self._set_entry(self.fbtv.path)
                else:
                    if self.fbtv.path=="/":
                        itempath=os.path.sep+item
                    else:
                        itempath=self.fbtv.path + os.path.sep+item
                    if os.path.isdir(itempath):
                        self.fbtv.path=itempath
                        self._set_entry(self.fbtv.path)
                    else:
                        if callable(self.openfilecallback):
                            self.openfilecallback(itempath)
            except Exception, ex:
                print ex
    

    #TREE VIEW CONNECTIONS
    def _on_upbtnclicked(self, widget, *args):
        self.fbtv.go_up()
        self.pathentry.set_text(self.fbtv.path)
        
    def _on_keypressed(self, widget, event):
        if gtk.gdk.keyval_name(event.keyval)=="Return": #Enter
            self._go_to_entry()
        
    def _set_entry(self, to):
        self.pathentry.set_text(to)
        self._go_to_entry()
        
    def _go_to_entry(self):
        epath=self.pathentry.get_text()
        if epath and os.path.exists(epath):
            self.fbtv.path=epath
            
    def _on_btnrefresh_clicked(self, widget, *args):
        self._go_to_entry()
            
    def _on_btngo_clicked(self, widget, *args):
        self._go_to_entry()

    def _on_homebtnclicked(self, widget, *args):
        self.fbtv.go_home()
        self._set_entry(self.fbtv.path)

    
class LeftSidePane(gtk.Notebook):
    def __init__(self, *args):
        gtk.Notebook.__init__(self, *args)
        self.add_filebrowser()
        self.add_xmlviewer()
        self.add_sourceviewer()
        
    def add_filebrowser(self):
        self.filebrowser=SidePaneBrowser()
        self.append_page(self.filebrowser, gtk.Label("FileBrowser"))
        
    def add_xmlviewer(self):
        scrolled=gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.xmlviewer=XMLTreeView()
        scrolled.add(self.xmlviewer)
        self.append_page(scrolled, gtk.Label("XMLViewer"))
        
    def add_sourceviewer(self):
        scrolled=gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sourceviewer=SourceCodeTreeView()
        scrolled.add(self.sourceviewer)
        self.append_page(scrolled, gtk.Label("SourceViewer"))



class Paste(object):
    def __init__(self, author="", title="", code="", lang=""):
        self.author=author
        self.title=title
        self.lang=lang
        self.code=code

class HPaste(object):
    PASTE_URL="http://hpaste.org/fastcgi/hpaste.fcgi/save"
    
    @staticmethod
    def create_data_dict(title, name, content, syntax):
        return dict(
            content=content,
            author=name,
            title=title,
            save='save',      
            language=syntax,
            channel='none',
        )
        
    @staticmethod
    def create_data_from_paste(paste):
        return dict(
            content=paste.code,
            author=paste.author,
            title=paste.title,
            save='save',      
            language=paste.lang,
            channel='none',
        )
    
    @classmethod
    def get_syntax_items(cls):
        return [
            ("apacheconf","ApacheConf"),
            ("BBCode", "bbcode"),
            ("Bash", "bash"),
            ("C", "c"),
            ("C#", "csharp"),
            ("C++", "cpp"),
            ("CSS", "css"),
            ("Clojure", "clojure"),
            ("Common Lisp", "common-lisp"),
            ("D", "d"),
            ("HTML", "html"),
            ("Haskell", "haskell"),
            ("INI", "ini"),
            ("Io", "io"),
            ("Java", "java"),
            ("JavaScript", "js"),
            ("Lighttpd configuration file", "lighty"),
            ("Lua", "lua"),
            ("Makefile", "make"),
            ("Objective-C", "objective-c"),
            ("PHP", "php"),
            ("Perl", "perl"),
            ("Python", "python"),
            ("Python 3", "python3"),
            ("Python 3.0 Traceback", "py3tb"),
            ("Python Traceback", "pytb"),
            ("Python console session", "pycon"),
            ("Raw token data","raw"),
            ("Ruby", "rb"),
            ("SQL", "sql"),
            ("Scala", "scala"),
            ("Text only", "text"),
            ("VimL", "vim"),
            ("XML", "xml"),
            ("YAML", "yaml"),
            ("reStructuredText", "rst"),
            ("sqlite3con", "sqlite3"),
        ]


#FROM pida.utils.web
from urllib import urlencode
from urllib2 import urlopen, Request
def fetch_url(url, data={}, auth=None):
    """
    fetch a URL.

    It takes these arguments:

        ``url``: the url to fetch
        ``data`` (optional): Additional POST data
        ``auth`` (optional): A tuple in the format (username, password) that's
                             used for http authentication

    """
    req = Request(url)

    if auth:
        base64string = base64.encodestring('%s:%s' % auth)[:-1]
        req.add_header("Authorization", "Basic %s" % base64string)

    if data:
        urlargs = (req, urlencode(data))
    else:
        urlargs = (req,)

    def _fetcher():
        try:
            f = urlopen(*urlargs)
            content = f.read()
            url = f.url
        except Exception, e:
            content = str(e)
            url = None
        return url, content
    return _fetcher()
        
class Paster(object):
        
    def __init__(self):
        self.pastedlinks=[]
        
    def supported_services(self):
        return ("HPaste")
        
    def paste(self, paste):
        d=HPaste.create_data_from_paste(paste)
        link=fetch_url(HPaste.PASTE_URL, d)[0]
        self.pastedlinks.append(link)
        return link
        #print "pasted..: ", link
        
                
class PasterWidget(gtk.VBox):
    
    def __init__(self, homogeneous=True, spacing=0):
        super(PasterWidget, self).__init__(homogeneous, spacing)
        self._init_comps()
        self.paster=Paster()
        
    def _init_comps(self):
        hb1=gtk.HBox(True, 2)
        hb1.pack_start(gtk.Label("Author: "),True, True, 2)
        self.authorentry=gtk.Entry()
        hb1.pack_start(self.authorentry,True, True, 2)

        hb2=gtk.HBox(True, 2)
        hb2.pack_start(gtk.Label("Title: "),True, True, 2)
        self.titleentry=gtk.Entry()
        hb2.pack_start(self.titleentry,True, True, 2)
        
        hb3=gtk.HBox(True, 2)
        hb3.pack_start(gtk.Label("Code: "),True, True, 2)
        self.txtview=gtk.TextView()
        scrolled=gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.txtview)
        hb3.pack_start(scrolled,True, True, 2)

        
        hb4=gtk.HBox(True, 2)
        hb4.pack_start(gtk.Label("Language: "),True, True, 2)
        self.langentry=gtk.Entry()
        hb4.pack_start(self.langentry,True, True, 2)

        hb5=gtk.HBox(True, 2)
        hb5.pack_start(gtk.Label("Link: "),True, True, 2)
        self.linkentry=gtk.Entry()
        hb5.pack_start(self.linkentry,True, True, 2)

        hb6=gtk.HBox(True, 2)
        self.btn_paste=gtk.Button("Paste!")
        self.btn_paste.connect("clicked", self._on_paste)
        hb6.pack_start(self.btn_paste,True, True, 2)
       
        self.pack_start(hb1, True, True, 2)
        self.pack_start(hb2, True, True, 2)
        self.pack_start(hb3, True, True, 2)
        self.pack_start(hb4, True, True, 2)
        self.pack_start(hb5, True, True, 2)
        self.pack_start(hb6, True, True, 2)
        
        #self.tbl=gtk.Table(6, 2)
        #self.tbl.set_row_spacings(10)
        #self.tbl.set_col_spacings(4)
        #self.tbl.attach(gtk.Label("Author: "),0, 1, 0, 1)
        #self.authorentry=gtk.Entry()
        #self.tbl.attach(self.authorentry, 1, 2, 0, 1)
        
        #self.tbl.attach(gtk.Label("Title: "), 0, 1, 1, 2)
        #self.titleentry=gtk.Entry()
        #self.tbl.attach(self.titleentry, 1, 2, 1, 2)
        
        #self.tbl.attach(gtk.Label("Code: "),0, 1, 2, 3)
        #self.txtview=gtk.TextView()
        #scrolled=gtk.ScrolledWindow()
        #scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #scrolled.add(self.txtview)
        #self.tbl.attach(scrolled, 1, 2, 2, 3)
        
        #self.tbl.attach(gtk.Label("Language: "), 0, 1, 3, 4)
        #self.langentry=gtk.Entry()
        #self.tbl.attach(self.langentry, 1, 2, 3, 4)
        
        #self.tbl.attach(gtk.Label("Link: "), 0, 1, 4, 5)
        #self.linkentry=gtk.Entry()
        #self.tbl.attach(self.linkentry, 1, 2, 4, 5)
        
        #self.btn_paste=gtk.Button("Paste!")
        #self.btn_paste.connect("clicked", self._on_paste)
        #self.tbl.attach(self.btn_paste, 1, 2, 5, 6)
        
        #self.pack_start(self.tbl, False, False, 0)
        
    def _on_paste(self, widget):
        author=self.authorentry.get_text()
        title=self.titleentry.get_text()
        buf=self.txtview.get_buffer()
        code=buf.get_text(buf.get_start_iter(), buf.get_end_iter())
        lang=self.langentry.get_text()
        
        paste=Paste(author=author, title=title, code=code, lang=lang)
        link=self.paster.paste(paste)
        if link:
            self.linkentry.set_text(link)
        
        
class TabWidget(gtk.Notebook):
    
    def __init__(self, *args):
        gtk.Notebook.__init__(self, *args)
        #self.add_simple_label()
        self.add_terminal()
        self.add_python_console()
        self.add_scribble()
        self.add_paster()
        
    def add_terminal(self):
        self.gterminal=GeditTerminal()
        self.append_page(self.gterminal, gtk.Label("Terminal"))
        #self.append_page(PidaTerminal(), gtk.Label("Terminal"))
        
    def add_python_console(self):
        self.append_page(Console(), gtk.Label("PyConsole"))
        
    def add_scribble(self):
        self.scribble_scrolled_window=gtk.ScrolledWindow()
        self.scribble_scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scribble_tv=gtk.TextView()
        self.scribble_scrolled_window.add(self.scribble_tv)
        self.append_page(self.scribble_scrolled_window, gtk.Label("Scribble"))
        
    
    def add_paster(self):
        #FIXME
        scrolled=gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.paster=PasterWidget()
        scrolled.add(self.paster)
        self.append_page(scrolled, gtk.Label("Paster"))
        
    #def add_simple_label(self):
        #self.append_page(gtk.Label("Hi"), gtk.Label("simple label"))
        
        
class BottomPane(gtk.VBox):
    
    def __init__(self, *args):
        gtk.VBox.__init__(self, *args)
        self._init_comps()
        
    def _init_comps(self):
        self.tabwidget=TabWidget()
        self.add(self.tabwidget)
        

class WC(object):
    
    def __init__(self, text=None):
        self.text=text
        
    nlines=lambda self: len(self.text.splitlines()) or 0
    nwords=lambda self: len(self.text.split(" ")) or 0
    nchars=lambda self: len(self.text)  or 0
    ncharsnospaces=lambda self:len(self.text)-self.text.count(" ") or 0
     

#GEDIT: bracketcompletion plugin.
from gtk import gdk

common_brackets = {
    '(' : ')',
    '[' : ']',
    '{' : '}',
    '"' : '"',
    "'" : "'",
}

close_brackets = {
    ')' : '(',
    ']' : '[',
    '}' : '{',
}

language_brackets = {
    'changelog': { '<' : '>' },
    'html': { '<' : '>' },
    'ruby': { '|' : '|', 'do': 'end' },
    'sh': { '`' : '`' },
    'xml': { '<' : '>' },
    'php': { '<' : '>' },
}


class BracketCompletionViewHelper(object):
    def __init__(self, view):
        self._view = view
        self._doc = view.get_buffer()
        self._last_iter = None
        self._stack = []
        self._relocate_marks = True
        self.update_language()
        
        #Add the markers to the buffer
        insert = self._doc.get_iter_at_mark(self._doc.get_insert())
        self._mark_begin = self._doc.create_mark(None, insert, True)
        self._mark_end = self._doc.create_mark(None, insert, False)

        self._handlers = [
            None,
            None,
            view.connect('notify::editable', self.on_notify_editable),
            self._doc.connect('notify::language', self.on_notify_language),
            None,
        ]
        self.update_active()

    def deactivate(self):
        if self._handlers[0]:
            self._view.disconnect(self._handlers[0])
            self._view.disconnect(self._handlers[1])
            self._doc.disconnect(self._handlers[4])
        self._view.disconnect(self._handlers[2])
        self._doc.disconnect(self._handlers[3])
        self._doc.delete_mark(self._mark_begin)
        self._doc.delete_mark(self._mark_end)

    def update_active(self):
        # Don't activate the feature if the buffer isn't editable or if
        # there are no brackets for the language
        active = self._view.get_editable() and \
                 self._brackets is not None

        if active and self._handlers[0] is None:
            self._handlers[0] = self._view.connect('event-after',
                                                   self.on_event_after)
            self._handlers[1] = self._view.connect('key-press-event',
                                                   self.on_key_press_event)
            self._handlers[4] = self._doc.connect('delete-range',
                                                  self.on_delete_range)
        elif not active and self._handlers[0] is not None:
            self._view.disconnect(self._handlers[0])
            self._handlers[0] = None
            self._view.disconnect(self._handlers[1])
            self._handlers[1] = None
            self._doc.disconnect(self._handlers[4])
            self._handlers[4] = None

    def update_language(self):
        lang = self._doc.get_language()
        if lang is None:
            self._brackets = None
            return

        lang_id = lang.get_id()
        if lang_id in language_brackets:
            self._brackets = language_brackets[lang_id]
            # we populate the language-specific brackets with common ones lazily
            self._brackets.update(common_brackets)
        else:
            self._brackets = common_brackets

        # get the corresponding keyvals
        self._bracket_keyvals = set()
        for b in self._brackets:
            kv = gtk.gdk.unicode_to_keyval(ord(b[-1]))
            if (kv):
                self._bracket_keyvals.add(kv)
        for b in close_brackets:
            kv = gtk.gdk.unicode_to_keyval(ord(b[-1]))
            if (kv):
                self._bracket_keyvals.add(kv)

    def get_current_token(self):
        end = self._doc.get_iter_at_mark(self._doc.get_insert())
        start = end.copy()
        word = None

        if end.ends_word() or (end.inside_word() and not end.starts_word()):
            start.backward_word_start()
            word = self._doc.get_text(start, end)

        if not word and start.backward_char():
            word = start.get_char()
            if word.isspace():
                word = None

        if word:
            return word, start, end
        else:
            return None, None, None

    def get_next_token(self):
        start = self._doc.get_iter_at_mark(self._doc.get_insert())
        end = start.copy()
        word = None

        if start.ends_word() or (start.inside_word() and not start.starts_word()):
            end.forward_word_end()
            word = self._doc.get_text(start, end)

        if not word and end.forward_char():
            word = start.get_char()
            if word.isspace():
                word = None

        if word:
            return word, start, end
        else:
            return None, None, None

    def compute_indentation (self, cur):
        """
        Compute indentation at the given iterator line
        view : gtk.TextView
        cur : gtk.TextIter
        """
        start = self._doc.get_iter_at_line(cur.get_line())
        end = start.copy();

        c = end.get_char()
        while c.isspace() and c not in ('\n', '\r') and end.compare(cur) < 0:
            if not end.forward_char():
                break
            c = end.get_char()

        if start.equal(end):
            return ''
        return start.get_slice(end)

    def on_notify_language(self, view, pspec):
        self.update_language()
        self.update_active()

    def on_notify_editable(self, view, pspec):
        self.update_active()

    def on_key_press_event(self, view, event):
        if event.state & (gdk.CONTROL_MASK | gdk.MOD1_MASK):
            return False

        if event.keyval in (gtk.keysyms.Left, gtk.keysyms.Right):
            self._stack = []

        if event.keyval == gtk.keysyms.BackSpace:
            self._stack = []
            
            if self._last_iter == None:
                return False
            
            iter = self._doc.get_iter_at_mark(self._doc.get_insert())
            iter.backward_char()
            self._doc.begin_user_action()
            self._doc.delete(iter, self._last_iter)
            self._doc.end_user_action()
            self._last_iter = None
            return True

        if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter) and \
           view.get_auto_indent() and self._last_iter != None:
            # This code has barely been adapted from gtksourceview.c
            # Note: it might break IM!

            mark = self._doc.get_insert()
            iter = self._doc.get_iter_at_mark(mark)

            indent = self.compute_indentation(iter)
            indent = "\n" + indent
            
            # Insert new line and auto-indent.
            self._doc.begin_user_action()
            self._doc.insert(iter, indent)
            self._doc.insert(iter, indent)
            self._doc.end_user_action()

            # Leave the cursor where we want it to be
            iter.backward_chars(len(indent))
            self._doc.place_cursor(iter)
            self._view.scroll_mark_onscreen(mark)

            self._last_iter = None
            return True

        self._last_iter = None
        return False

    def on_event_after(self, view, event):
        if event.type != gdk.KEY_PRESS or \
           event.state & (gdk.CONTROL_MASK | gdk.MOD1_MASK) or \
           event.keyval not in self._bracket_keyvals:
            return
        
        # Check if the insert mark is in the range of mark_begin to mark_end
        # if not we free the stack
        insert = self._doc.get_insert()
        iter_begin = self._doc.get_iter_at_mark(self._mark_begin)
        iter_end = self._doc.get_iter_at_mark(self._mark_end)
        insert_iter = self._doc.get_iter_at_mark(insert)
        if not iter_begin.equal(iter_end):
            if not insert_iter.in_range(iter_begin, iter_end):
                self._stack = []
                self._relocate_marks = True
        
        # Check if the word is not in our brackets
        word, start, end = self.get_current_token()
        
        if word not in self._brackets and word not in close_brackets:
            return

        # If we didn't insert brackets yet we insert them in the insert mark iter
        if self._relocate_marks == True:
            insert_iter = self._doc.get_iter_at_mark(insert)
            self._doc.move_mark(self._mark_begin, insert_iter)
            self._doc.move_mark(self._mark_end, insert_iter)
            self._relocate_marks = False
        
        # Depending on having close bracket or a open bracket we get the opposed
        # bracket
        bracket = None
        bracket2 = None
        
        if word not in close_brackets:
            self._stack.append(word)
            bracket = self._brackets[word]
        else:
            bracket2 = close_brackets[word]
        
        word2, start2, end2 = self.get_next_token()
        
        # Check to skip the closing bracket
        # Example: word = ) and word2 = )
        if word == word2:
            if bracket2 != None and self._stack != [] and \
               self._stack[len(self._stack) - 1] == bracket2:
                self._stack.pop()
                self._doc.handler_block(self._handlers[4])
                self._doc.delete(start, end)
                self._doc.handler_unblock(self._handlers[4])
                end.forward_char()
                self._doc.place_cursor(end)
            return
        
        # Insert the closing bracket
        if bracket != None:
            self._doc.begin_user_action()
            self._doc.insert(end, bracket)
            self._doc.end_user_action()
            
            # Leave the cursor when we want it to be
            self._last_iter = end.copy()
            end.backward_chars(len(bracket))
            self._doc.place_cursor(end)

    def on_delete_range(self, doc, start, end):
        self._stack = []


     
def testmoduleviewer():
    p=PythonSourcePlugin()
    p.set_module_path("/home/ahmed/tstqlistwidget.py")
    
    print p.get_classes()[0][1]
    #print type(p.get_classes())
    
    print p.get_methods_of(p.get_classes()[0][1])
    print p.get_functions()

if __name__=="__main__":
    testmoduleviewer()
