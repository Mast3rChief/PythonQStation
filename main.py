from udp_client import *
import ttk
import sys
if sys.version_info <= (3, 0):
    from Tkinter import *
    from tkMessageBox import *
    from tkColorChooser import askcolor
else:
    from tkinter import *
    from tkinter.messagebox import *
    from tkinter.colorchooser import askcolor


class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("Python Q Station Control")
        
        self.mainframe = Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        
        self.ip = StringVar()
        self.name = StringVar()
        self.color = StringVar()
        self.response = StringVar()
        self.item_id = IntVar()
        
        self.bulb_treeview = ttk.Treeview(self.mainframe)
        self.bulb_treeview.grid(column=0, row=1, rowspan=5, sticky=(W, E))
        self.bulb_treeview.bind('<<TreeviewSelect>>', self.callback_bulb_treeview)
        
        self.ip_entry = Entry(self.mainframe, textvariable=self.ip)
        self.ip_entry.grid(column=2, row=1, sticky=(W, E))

        self.name_entry = Entry(self.mainframe, textvariable=self.name)
        self.name_entry.grid(column=2, row=2, sticky=(W, E))
        
        self.bright_scale = Scale(self.mainframe, from_=0, to=100, orient=HORIZONTAL)
        self.bright_scale.set(0)
        self.bright_scale.grid(column=2, row=3, sticky=(N, W, E, S))

        Button(self.mainframe, text='Set Values', command=self.callback_set_values).grid(column=2, row=6, sticky=(W, E))
        Button(self.mainframe, text='Get bulbs from Q Station', command=self.callback_get_bulbs).grid(column=0, row=6, sticky=(W, E))
        self.color_button = Button(self.mainframe, text='Change Color', command=self.callback_set_color)
        self.color_button.grid(column=2, row=4, sticky=(W, E))

        Label(self.mainframe, text='Q Station IP').grid(column=1, row=1, sticky=W)
        Label(self.mainframe, text='Name').grid(column=1, row=2, sticky=W)
        Label(self.mainframe, text='Brightness').grid(column=1, row=3, sticky=W)
        Label(self.mainframe, text='Color').grid(column=1, row=4, sticky=W)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=10, pady=5)

        self.ip_entry.focus()

        self.root.mainloop()

    def callback_set_color(self):
        self.color = askcolor(color=(int(self.response['led'][self.item_id]['r']), int(self.response['led'][self.item_id]['g']), int(self.response['led'][self.item_id]['b'])))

        self.color_button.config(background=self.color[1])

    def callback_set_values(self):
        if self.bulb_treeview.selection() != '' and self.bulb_treeview.selection()[0] != 'bulbs':
            udp_client = UdpClient(self.ip.get(), 11600)
            udp_client.set_light(self.bright_scale.get(), self.color[0][0], self.color[0][1], self.color[0][2], self.bulb_treeview.item(self.bulb_treeview.selection()[0], 'tag')[0])
        else:
            showinfo('Info', 'Please select the bulb you want to control.')
    
    def callback_get_bulbs(self):
        if self.ip.get() != '':
            udp_client = UdpClient(self.ip.get(), 11600)
            self.response = udp_client.get_lights()

            map(self.bulb_treeview.delete, self.bulb_treeview.get_children())
            self.bulb_treeview.insert('', 'end', 'bulbs', text='Q Station', open=True)

            for i in range(len(self.response['led'])):
                if int(self.response['led'][i]['online']) == 1:
                    status = 'On'
                else:
                    status = 'Off'

                self.bulb_treeview.insert('bulbs', 'end', text=self.response['led'][i]['title'] + ' (' + status + ')', tag=self.response['led'][i]['sn'])
        else:
            showerror('Error', 'Please fill in the Q Station IP first.')

    def callback_bulb_treeview(self, event):
        item = self.bulb_treeview.selection()[0]

        if item != 'bulbs':
            self.item_id = int(self.bulb_treeview.selection()[0][3]) - 1

            self.name_entry.delete(0, END)
            self.name_entry.insert(0, self.response['led'][self.item_id]['title'])
            self.bright_scale.set(self.response['led'][self.item_id]['bright'])
            self.color_button.config(background=self.rgb_to_hex((int(self.response['led'][self.item_id]['r']), int(self.response['led'][self.item_id]['g']), int(self.response['led'][self.item_id]['b']))))

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

if __name__ == '__main__':
    app = App()