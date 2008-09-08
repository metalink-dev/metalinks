import Tkinter
import tkFileDialog
import tkMessageBox
import os
import gettext
import locale
import time
import webbrowser

import checker

NAME="Metalink Checker"
ABOUT=""
#WEBSITE="http://www.metalinker.org"
WEBSITE="http://www.nabber.org/projects/checker"

def translate():
    '''
    Setup translation path
    '''
    global PATH
    if __name__=="__main__":
        try:
            base = os.path.basename(__file__)[:-3]
            PATH = os.path.dirname(__file__)
            localedir = os.path.join(PATH, "locale")
        except NameError:
            base = os.path.basename(sys.executable)[:-4]
            PATH = os.path.dirname(sys.executable)
            localedir = os.path.join(PATH, "locale")
    else:
        temp = __name__.split(".")
        base = temp[-1]
        PATH = "/".join(["%s" % k for k in temp[:-1]])
        localedir = os.path.join(PATH, "locale")

    #print base, localedir
    t = gettext.translation(base, localedir, [locale.getdefaultlocale()[0]], None, 'en')
    return t.ugettext

_ = translate()

class Table(Tkinter.Frame):
    def __init__(self, *args):
        Tkinter.Frame.__init__(self, *args)
        self.subelements = []

    def data(self, datalist):
        self.clear()
        
        row = 1
        for datarow in datalist:
            column = 1
            for datacolumn in datarow:
                label = Tkinter.Label(self, text=datacolumn)
                label.grid(column=column, row=row)
                self.subelements.append(label)
                column += 1
            row += 1

    def clear(self):
        for element in self.subelements:
            del(element)
        self.subelements = []
        
class Application:
    def __init__(self, master):
        self.master = master
        self.checker = checker.Checker()
        self.createWidgets()

        self.quit = self.exit
        self.destroy = self.exit

    def createWidgets(self):
        # create menu
        menu = Tkinter.Menu(self.master)
        self.master.config(menu=menu)

        Filemenu = Tkinter.Menu(menu)
        menu.add_cascade(label=_("File"), menu=Filemenu, underline=0)
        Filemenu.add_command(label=_("Open") + "...", underline=0, command=self.open)
        Filemenu.add_separator()
        Filemenu.add_command(label=_("Exit"), underline=1, command=self.exit)

        Helpmenu = Tkinter.Menu(menu)
        menu.add_cascade(label=_("Help"), menu=Helpmenu, underline=0)
        Helpmenu.add_command(label=_("About") + "...", underline=0, command=self.about)
        Helpmenu.add_command(label=_("Website") + "...", underline=0, command=self.website)

        # main frame
        self.main_frame = Tkinter.Frame(self.master)
        self.main_frame.pack(expand=1, fill=Tkinter.BOTH)

        longtext = 100

        row_index = 1
        Tkinter.Label(self.main_frame, text=_("File") + ":").grid(row=row_index, sticky="NW")
        self.filename_txt = Tkinter.Entry(self.main_frame, width=longtext)
        self.filename_txt.grid(row=row_index, column=1)
        Tkinter.Button(self.main_frame, text=_("Browse") + "...", command=self.open).grid(row=row_index, column=2)
        self.check_button = Tkinter.Button(self.main_frame, text=_("Check"), command=self.do_check)
        self.check_button.grid(row=row_index, column=3)
        
        self.cancel_button = Tkinter.Button(self.main_frame, text=_("Cancel"), command=self.do_cancel)
        self.cancel_button.grid(row=row_index, column=4)
        self.cancel_button.configure(state="disabled")
 
        #tooltip = _("File to open and check.")
        #ToolTip(self.filename_txt, text=tooltip)
        row_index += 1

        self.tableframe = Table(self.main_frame)
        self.tableframe.grid(column=1, row=row_index, sticky="NW")
        

    def do_check(self):
        self.check_button.configure(state="disabled")
        self.cancel_button.configure(state="active")
        # should start new thread here
        self.checker.check_metalink(self.filename_txt.get())
        # wait and do updates here
        #if self.checker.isAlive():
        self.update()

        self.do_cancel()

    def do_cancel(self):
        # should start new thread here
        self.checker.clear_results()
        # wait for thread here
        self.cancel_button.configure(state="disabled")
        self.check_button.configure(state="active")

    def update(self):
        count = 0
        active = 1
        while active:
            active = self.checker.activeCount()
            if active != count:
                # do update stuff here

                result = self.format_table(self.checker.get_results())
                self.tableframe.data(result)

                count = active
            time.sleep(1)

    def format_table(self, datadict):
        datalist = [[_("Filename"), _("URL"), _("Response Code"), _("Size Check")]]
        for filename in datadict.keys():
            datalist.append([filename])
            urls = datadict[filename].keys()
            for url in urls:
                add = ["", url]
                for item in datadict[filename][url]:
                    add.append(item)
                datalist.append(add)
        return datalist

    def open(self):
        init = ""
        if self.filename_txt.get() != "":
            init = os.path.dirname(self.filename_txt.get())
        result = tkFileDialog.askopenfilename(initialdir = init, title=_("Please select a Metalink file to open") + "...", filetypes=[('Metalink File','*.metalink')])
        if result != "":
            # do file path set here
            self.filename_txt.delete(0, Tkinter.END)
            self.filename_txt.insert(0, result)
            
    def about(self):
        tkMessageBox.showinfo(_("About") + " " + NAME, ABOUT)

    def website(self):
        webbrowser.open_new_tab(WEBSITE)

    def exit(self):
        self.master.quit()
        
def run():
    root = Tkinter.Tk()
    root.title(NAME)
    root.geometry("850x500")
    #try:
    app = Application(master=root)
    #app.periodic_task()
    #except:
    #    return
    

    root.protocol("WM_DELETE_WINDOW", app.exit)
    root.mainloop()

if __name__=="__main__":
    run()
