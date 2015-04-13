from udp_client import *
import sys
import socket

if sys.version_info < (3, 0):
    from Tkinter import *
    from tkMessageBox import *
    from tkColorChooser import askcolor
    from ConfigParser import SafeConfigParser
    import ttk as ttk
else:
    from tkinter import *
    from tkinter.messagebox import *
    from tkinter.colorchooser import askcolor
    from configparser import SafeConfigParser
    import tkinter.ttk as ttk


class App:
    NAME = 'PythonQStationController'
    TITLE = 'Q Station Controller'
    BACKGROUND = '#efefef'
    CONFIG_FILE = 'config.ini'
    PORT = 11600

    def __init__(self):
        self.root = Tk(className=self.TITLE)
        self.root.title(self.TITLE)
        self.root.resizable(0, 0)
        self.root.configure(background=self.BACKGROUND)
        icon = PhotoImage(file='icons/icon.gif')
        self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
        
        self.mainframe = Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.configure(background=self.BACKGROUND)

        self.udp_client = NONE
        self.ip = StringVar()
        self.name = StringVar()
        self.color = ()
        self.status = IntVar()
        self.response = StringVar()
        self.item = StringVar()
        self.item_id = IntVar()

        self.config = SafeConfigParser()
        self.config.read(self.CONFIG_FILE)

        try:
            self.ip.set(socket.gethostbyname('belllnet'))
        except:
            if any(self.NAME in sec for sec in self.config.sections()):
                self.ip.set(self.config.get(self.NAME, 'last_ip'))
            else:
                self.config.add_section(self.NAME)

        self.bulb_treeview = ttk.Treeview(self.mainframe)
        self.bulb_treeview.heading("#0", text="Bulbs")
        self.bulb_treeview.grid(column=0, row=0, rowspan=2, sticky=(N, W, E, S))
        self.bulb_treeview.bind('<<TreeviewSelect>>', self.callback_bulb_treeview)

        Label(self.mainframe, text='Q Station IP').grid(column=1, row=0, sticky=W)

        self.ip_entry = Entry(self.mainframe, textvariable=self.ip)
        self.ip_entry.grid(column=2, row=0, sticky=(W, E))

        img_connect = PhotoImage(file='icons/arrow_refresh.gif')
        Button(self.mainframe, command=self.callback_get_bulbs, image=img_connect).grid(column=3, row=0, sticky=(W, E))

        #Button(self.mainframe, command=self.callback_get_groups, image=img_connect).grid(column=3, row=10, sticky=(W, E))

        self.labelframe = LabelFrame(self.mainframe, text='Bulb Settings')
        self.labelframe.grid(column=1, columnspan=3, row=1, sticky=(N, W, E, S))

        Label(self.labelframe, text='Name').grid(column=1, row=1, sticky=W)

        self.name_entry = Entry(self.labelframe, textvariable=self.name)
        self.name_entry.grid(column=2, row=1, sticky=(W, E))

        Label(self.labelframe, text='Brightness').grid(column=1, row=3, sticky=W)
        
        self.bright_scale = Scale(self.labelframe, from_=0, to=255, orient=HORIZONTAL)
        self.bright_scale.set(0)
        self.bright_scale.grid(column=2, row=3, sticky=(N, W, E, S))

        Label(self.labelframe, text='Status').grid(column=1, row=2, sticky=W)

        Checkbutton(self.labelframe, text=' Turn the bulb on or off', variable=self.status).grid(column=2,
                                                                                                 columnspan=2,
                                                                                                 row=2,
                                                                                                 sticky=(W, E))

        img_accept = PhotoImage(file='icons/accept.gif')
        Button(self.labelframe, text='Set Values', command=self.callback_set_values, image=img_accept,
               compound=LEFT).grid(column=1, columnspan=2, row=5, sticky=(W, E))

        Label(self.labelframe, text='Color').grid(column=1, row=4, sticky=W)

        img_color = PhotoImage(file='icons/color_wheel.gif')
        self.color_button = Button(self.labelframe, command=self.callback_set_color, image=img_color)
        self.color_button.grid(column=2, row=4, sticky=(W, E))

        for child in self.mainframe.winfo_children():
            try:
                child.grid_configure(padx=10, pady=5)
                child.configure(background=self.BACKGROUND)
            except:
                pass

        for child in self.labelframe.winfo_children():
            try:
                child.grid_configure(padx=10, pady=5)
                child.configure(background=self.BACKGROUND)
                child.configure(state='disable')
            except:
                pass

        if self.ip.get():
            self.callback_get_bulbs()

        self.ip_entry.focus()

        self.root.mainloop()

    def callback_set_color(self):
        if self.bulb_treeview.selection() != '' and self.item != 'bulbs':
            tempcolor = askcolor(color=(int(self.color[0][0]), int(self.color[0][1]), int(self.color[0][2])))
            if tempcolor[1] is not None:
                self.color = tempcolor 
                self.color_button.config(background=self.color[1])
        else:
            showinfo('Info', 'Please select the bulb you want to control.')

    def callback_set_values(self):
        if self.bulb_treeview.selection() != '' and self.item != 'bulbs':
            self.udp_client.set_light(self.bright_scale.get(),
                                      self.color[0][0],
                                      self.color[0][1],
                                      self.color[0][2],
                                      self.status.get(),
                                      self.response['led'][self.item_id]['sn'])
            self.udp_client.set_title(self.response['led'][self.item_id]['sn'],
                                      self.name.get())
            self.callback_get_bulbs()
        else:
            showinfo('Info', 'Please select the bulb you want to control.')

    def callback_get_bulbs(self):
        if self.ip.get() != '':
            self.udp_client = UdpClient(self.ip.get(), self.PORT)
            self.response = self.udp_client.get_lights()

            self.config.set(self.NAME, 'last_ip', self.ip.get())

            with open(self.CONFIG_FILE, 'w') as f:
                self.config.write(f)

            map(self.bulb_treeview.delete, self.bulb_treeview.get_children())
            self.bulb_treeview.insert('', 'end', 'bulbs', text='Q Station', open=True)

            for i in range(len(self.response['led'])):
                if int(self.response['led'][i]['online']) == 1:
                    status = 'Online'
                else:
                    status = 'Offline'

                self.bulb_treeview.insert('bulbs',
                                          'end',
                                          text=self.response['led'][i]['title'] + ' (' + status + ')',
                                          tag=i)

            for child in self.labelframe.winfo_children():
                child.configure(state='normal')
        else:
            showerror('Error', 'Please fill in the Q Station IP first.')

    #def callback_get_groups(self):
        # There seems to be an error in this seciton, line 204
        # if self.ip.get() != '':
        #     self.udp_client = UdpClient(self.ip.get(), self.PORT)
        #     self.groups = self.udp_client.get_groups()
        #     self.lights = self.udp_client.get_groups()

        #     self.config.set(self.NAME, 'last_ip', self.ip.get())

        #     with open(self.CONFIG_FILE, 'w') as f:
        #         self.config.write(f)

        #     print self.groups['data'][0]['group_title'], self.groups['data'][0]['group_id']
            
        #     # map(self.bulb_treeview.delete, self.bulb_treeview.get_children())


        #     for i in range(len(self.groups['data'])):
        #         self.bulb_treeview.insert('', 'end', 'groups', text=self.groups['data'][i]['group_title'], open=True)
        #         # has to be adjusted for each element of the group
        #         # if int(self.response['led'][i]['online']) == 1:
        #         #     status = 'Online'
        #         # else:
        #         #     status = 'Offline'
        #         for n in range(len(self.groups['data'])):
        #         # self.bulb_treeview.insert('groups',
        #         #                           'end',
        #         #                           text=self.groups['data'][i]['group_title'],
        #         #                           tag=i)

        #     # for child in self.labelframe.winfo_children():
        #     #     child.configure(state='normal')
        # else:
        #     showerror('Error', 'Please fill in the Q Station IP first.')

    def callback_bulb_treeview(self, event):
        self.item = self.bulb_treeview.selection()[0]

        if self.item != 'bulbs':
            self.item_id = int(self.bulb_treeview.item(self.bulb_treeview.focus())['tags'][0])

            self.name_entry.delete(0, END)
            self.name_entry.insert(0, self.response['led'][self.item_id]['title'])
            self.bright_scale.set(int(self.response['led'][self.item_id]['bright']))
            self.color_button.config(background=self.rgb_to_hex((int(self.response['led'][self.item_id]['r']),
                                                                 int(self.response['led'][self.item_id]['g']),
                                                                 int(self.response['led'][self.item_id]['b']))))
            self.color = ((self.response['led'][self.item_id]['r'],
                          self.response['led'][self.item_id]['g'],
                          self.response['led'][self.item_id]['b']),
                          '')
            self.status.set(int(self.response['led'][self.item_id]['iswitch']))

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

if __name__ == '__main__':
    app = App()
