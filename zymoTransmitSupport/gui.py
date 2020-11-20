import os
try:
    import tkinter
    active = True
except Exception as err:
    print("Unable to load Tkinter.  Error as follows:\n%s" %err)
    active = False


defaultDirectory = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]

if active:


    def selectFileForOpening(prompt:str, defaultDirectory:str=defaultDirectory, fileTypes=(("All Files", "*.*"))):
        if not active:
            raise RuntimeError("Attempted to use GUI while not active")
        import tkinter.filedialog
        file = tkinter.filedialog.askopenfilename(initialdir=defaultDirectory, title=prompt, filetypes=fileTypes)
        return file


    def selectDirectoryForOpening(prompt:str, defaultDirectory:str=defaultDirectory):
        if not active:
            raise RuntimeError("Attempted to use GUI while not active")
        import tkinter.filedialog
        file = tkinter.filedialog.askdirectory(initialdir=defaultDirectory, title=prompt, mustexist='True')
        return file


    def textEditFile(filePath:str):
        class _Window(tkinter.Frame):
            def __init__(self, master, filePath: str, title: str = "Text Editor"):
                if not os.path.isfile(filePath):
                    raise FileNotFoundError("Unable to find file %s" % filePath)
                self.filePath = filePath
                tkinter.Frame.__init__(self, master)
                self.master = master
                self.master.title(title)
                self.pack(fill=tkinter.BOTH, expand=1)
                menu = tkinter.Menu(topWindow)
                topWindow.config(menu=menu)
                self.fileMenu = tkinter.Menu(menu)
                menu.add_cascade(label="Save", menu=self.fileMenu)
                self.text = tkinter.Text(topWindow, height=200, width=200)
                self.fileMenu.add_command(label="Save", command=self.saveFile)
                self.text.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=True)
                self.scrollbar = tkinter.Scrollbar(topWindow, orient="vertical")
                self.scrollbar.config(command=self.text.yview)
                self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y, expand=True)
                self.text.config(yscrollcommand=self.scrollbar.set)
                file = open(self.filePath, 'r')
                for line in file:
                    self.text.insert(tkinter.END, line)
                file.close()

            def saveFile(self):
                text = self.text.get(1.0, tkinter.END)
                file = open(self.filePath, 'w')
                file.write(text)
                file.close()

        topWindow = tkinter.Tk()
        topWindow.geometry("400x400")
        editor = _Window(topWindow, filePath, "Editing %s. Save and quit when done." %filePath)
        topWindow.mainloop()


    def promptForCertPassword():
        import tkinter.simpledialog
        password = tkinter.simpledialog.askstring("PFX Certificate Password", "Enter certificate password if needed.", show = "*")
        return password

