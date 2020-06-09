!pip install tkinter
from tkinter import *
import matplotlib
matplotlib.use('TkAgg')
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pandas as pd
import numpy as np
import datetime
from textwrap import wrap


# read files
track_length_combined = pd.read_csv('https://jroefive.github.io/track_length_combined')
set_placement = pd.read_csv('https://jroefive.github.io/set_placement_plot')

# Combine inputs into a datetime variable and retrieve the ID number for that show
def get_show_date(year,month,day):
    show_date = datetime.date(year, month, day)
    sd = str(show_date)
    show_played = True
    # Make sure the date input is in the database
    if sd in track_length_combined['date'].values:
        show_date_id = track_length_combined[track_length_combined['date']==sd]['order_id'].values
        # Previous line creates a series of the same ID values, so need to reset to equal just the first value.
        show_date_id = show_date_id[0]
    # If the show doesn't exist, set show_played to false so other functions won't run
    else:
        show_played = False
        show_date_id = 1
    return show_date, show_date_id, show_played

# Pull a list of all songs in each set of show
def get_setlist(show_date_id):
    show_only = track_length_combined[(track_length_combined['order_id']==show_date_id)]
    show_only = show_only.sort_values(by='position')
    show_songs_s1 = show_only[show_only['set']=='1']['title'].values
    show_songs_s2 = show_only[show_only['set']=='2']['title'].values
    show_songs_s3 = show_only[show_only['set']=='3']['title'].values
    show_songs_e = show_only[(show_only['set']=='E') | (show_only['set']=='E2')]['title'].values
    return show_songs_s1, show_songs_s2, show_songs_s3, show_songs_e

# Create Graphs
def get_graph(set_songs, show_date, show_date_id, hue_choice, graph_type):
    
    # Update hue list and order and make sure to include selected show
    hue_list = ('Before', 'Previous 50 Shows', show_date, 'Next 50 Shows', 'After')
    hue_choice.append(show_date)
    hue_order = []
    for hue in hue_list:
        if hue in hue_choice:
            hue_order.append(hue)
    
    # Select the correct data dependent on graph type
    if graph_type == 'dur':
        tracks_from_set = track_length_combined[track_length_combined['title'].isin(set_songs)].copy()
    elif graph_type == 'place':
        tracks_from_set = set_placement[set_placement['title'].isin(set_songs)].copy()
    
    # Create timing column to color code graph by recent shows
    tracks_from_set.loc[tracks_from_set['order_id'] < show_date_id, 'timing'] = 'Before'
    tracks_from_set.loc[tracks_from_set['order_id'] > show_date_id, 'timing'] = 'After'
    tracks_from_set.loc[(tracks_from_set['order_id'] > show_date_id) & (tracks_from_set['order_id'] - (show_date_id + 50) <= 0), 'timing'] = 'Next 50 Shows'
    tracks_from_set.loc[(tracks_from_set['order_id'] < show_date_id) & (tracks_from_set['order_id'] - (show_date_id - 50) >= 0), 'timing'] = 'Previous 50 Shows'
    tracks_from_set.loc[tracks_from_set['order_id'] == show_date_id, 'timing'] = show_date
    
    # Drop all timing values that weren't selected
    tracks_from_set = tracks_from_set[tracks_from_set['timing'].isin(hue_choice)]
    
    # Color palette so the colors stay consistent for all timing choices
    palette = {"Before":"#E8E0DE", "Previous 50 Shows":"#2C6E91", show_date:"#000000", "Next 50 Shows":"#F15A50", "After":"#DEE8E4"}
    
    # Create figure, add subplot and set x values since both graphs have same x value
    graph = Figure(figsize = (12.5,5))
    graph.patch.set_facecolor('#2C6E91')
    ax = graph.add_subplot(111)
    
    
    # Plot duration graph and set y axis label to be duration
    if graph_type == 'dur':
        sns.swarmplot(x="title", y="duration", hue = 'timing', hue_order = hue_order, order = set_songs, data=tracks_from_set, 
            palette=palette, ax=ax)
        ax.set_ylabel('Song Duration in Minutes', fontname="Arial", fontsize=18)
        
    # Plot set placement graph, set y axis label to be set placement, and rename yticklabels to make it clearer what set placement mean
    elif graph_type == 'place':
        sns.swarmplot(x="title", y="percentintoset", hue = 'timing', hue_order = hue_order, order = set_songs, data=tracks_from_set, 
            palette=palette, ax=ax)
        ax.set_ylabel('Set Placement', fontname="Arial", fontsize=18)
        ytick_list = ax.get_yticks().tolist()
        for n,i in enumerate(ytick_list):
            if i == 1:
                ytick_list[n] = 'Start Set 1'
            elif i == 1.5:
                ytick_list[n] = 'Middle Set 1'
            elif i == 2:
                ytick_list[n] = 'Start Set 2'
            elif i == 2.5:
                ytick_list[n] = 'Middle Set 2'
            elif i == 3:
                ytick_list[n] = 'Start Set 3'
            elif i == 3.5:
                ytick_list[n] = 'Middle Set 3'
            elif i == 4:
                ytick_list[n] = 'Start Encore'
            elif i == 4.5:
                ytick_list[n] = 'Middle Encore'
            elif i == 5:
                ytick_list[n] = 'End of Show'
        ax.set_yticklabels(ytick_list, fontname="Arial", fontsize=12)
    
    # Rotate and wrap song title labels
    ax.set_xlabel('Song Title', fontname="Arial", fontsize=18)
    labels = set_songs
    labels = [ '\n'.join(wrap(l, 10)) for l in labels ]
    ax.set_xticklabels(labels,rotation=45, fontname="Arial", fontsize=12)
    
    # Placement of legend and create enough space at bottom for song titles.
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=5, fancybox=True, shadow=True)
    graph.subplots_adjust(bottom=0.3)
    ax.spines['bottom'].set_color('#F15A50')
    ax.spines['top'].set_color('#F15A50')
    ax.xaxis.label.set_color('#F15A50')
    ax.tick_params(axis='x', colors='#F15A50')
    ax.spines['left'].set_color('#F15A50')
    ax.spines['right'].set_color('#F15A50')
    ax.yaxis.label.set_color('#F15A50')
    ax.tick_params(axis='y', colors='#F15A50')
    
    return graph

# Template for TK pages
class Template(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(side="top", fill="both", expand = True)
        
        self.frames = {}


        for F in (InputPage, SetlistPage):
            frame=F(container, self)
            self.frames[F]=frame
            frame.grid(row=0, column=0, sticky="nsew")

            self.show_frame(InputPage)
    
    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]

# Main page of app
class InputPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller=controller
        # Set some global variables
        self.month = ''
        self.day = ''
        self.year = ''
        self.show_date = ''
        self.show_date_id = 0
        global set_for_graph
        self.set_for_graph = IntVar()
        self.set_for_graph.set(1)
        self.hues = ('Before', 'Previous 50 Shows', 'Next 50 Shows', 'After')
        self.hue_choice = []
        self.config(bg="#2C6E91")
        # Reset the date, chosen set, and timing choices every time a graph or setlist is requested
        
        def reset_date():
            self.graph_frame.destroy()  
            self.pane6.destroy()
            self.pane7.destroy()
            self.pane8.destroy()
            self.pane9.destroy()
            self.pane_error.destroy()
            self.month = int(month.get())
            self.day = int(day.get())
            self.year = int(year.get())
            self.set_for_graph_int = self.set_for_graph.get()
            self.show_date, self.show_date_id, self.show_played = get_show_date(self.year,self.month,self.day)
            if not self.show_played:
                self.pane_error = Frame(self, bg="#2C6E91")
                self.pane_error.pack(side = TOP, fill = BOTH, expand = True, padx = 10, pady = 10)
                Label(self.pane_error, text="Phish did not play a show on " + str(self.show_date) + '. Or that show is not available in this database.', bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
            self.hue_choice = []
            for ix, hue in enumerate(self.hues):
                if hue_vars[ix].get():
                    self.hue_choice.append(hue)
        
        # Update setlist panes when setlist is requested
        def print_setlist(): 
            if self.show_played:
                self.pane6 = Frame(self, bg="#2C6E91") 
                self.pane6.pack(fill = BOTH, expand = True)
                self.pane7 = Frame(self, bg="#2C6E91") 
                self.pane7.pack(fill = BOTH, expand = True)
                self.pane8 = Frame(self, bg="#2C6E91") 
                self.pane8.pack(fill = BOTH, expand = True)
                self.pane9 = Frame(self, bg="#2C6E91") 
                self.pane9.pack(fill = BOTH, expand = True)
            
                Label(self.pane6, text='Set 1:', bg="#2C6E91", fg = '#F15A50', font = ('Arial', 18)).pack( side = LEFT, padx = 5, pady = 5)
                self.set1 = Label(self.pane6, text='', bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'))
                self.set1.pack( side = LEFT, expand = True)
        
                Label(self.pane7, text='Set 2:', bg="#2C6E91", fg = '#F15A50', font = ('Arial', 18)).pack( side = LEFT, padx = 5, pady = 5)
                self.set2 = Label(self.pane7, text='', bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'))
                self.set2.pack( side = LEFT, expand = True)
        
                Label(self.pane8, text='Set 3:', bg="#2C6E91", fg = '#F15A50', font = ('Arial', 18)).pack( side = LEFT, padx = 5, pady = 5)
                self.set3 = Label(self.pane8, text='', bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'))
                self.set3.pack( side = LEFT, expand = True)
        
                Label(self.pane9, text='Encore:', bg="#2C6E91", fg = '#F15A50', font = ('Arial', 18)).pack( side = LEFT, padx = 5, pady = 5)
                self.enc = Label(self.pane9, text='', bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'))
                self.enc.pack( side = LEFT, expand = True)
            
                self.s1, self.s2, self.s3, self.e = get_setlist(self.show_date_id)
                self.set1.config(text=self.s1)
                self.graph_frame.destroy()      
                self.graph_frame = Frame(self)
                self.graph_frame.pack(fill = BOTH, expand = True)
                if len(self.s2) > 0:
                    self.set2.config(text=self.s2)
                if len(self.s3) > 0:
                    self.set3.config(text=self.s3)
                if len(self.e) > 0:
                    self.enc.config(text=self.e)
        
        # Show graph command on button push
        def show_graph(graph_type):
            if self.show_played:
                # Get setlist
                self.s1, self.s2, self.s3, self.e = get_setlist(self.show_date_id)
                # Destory any previous graphs before graphing again    
                self.graph_frame = Frame(self)
                self.graph_frame.pack(fill = BOTH, expand = True)
                # If statement to input correct set, call get_graph, then draw graph
                if self.set_for_graph_int == 1 and len(self.s1)>0:
                    self.g1 = get_graph(self.s1, self.show_date, self.show_date_id, self.hue_choice, graph_type)
                    canvas = FigureCanvasTkAgg(self.g1, self.graph_frame)
                    canvas.draw()
                    set1plot = canvas.get_tk_widget()
                    set1plot.pack(side = LEFT)
                if self.set_for_graph_int == 2 and len(self.s2)>0:
                    self.g2 = get_graph(self.s2, self.show_date, self.show_date_id, self.hue_choice, graph_type)
                    canvas = FigureCanvasTkAgg(self.g2, master = self.graph_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(side = LEFT)
                if self.set_for_graph_int == 3 and len(self.s3)>0:
                    self.g3 = get_graph(self.s3, self.show_date, self.show_date_id, self.hue_choice, graph_type)
                    canvas = FigureCanvasTkAgg(self.g3, master = self.graph_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack()
                if self.set_for_graph_int == 4 and len(self.e)>0:
                    self.ge = get_graph(self.e, self.show_date, self.show_date_id, self.hue_choice, graph_type)
                    canvas = FigureCanvasTkAgg(self.ge, master = self.graph_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack()
                else:
                    self.pane_error = Frame(self, bg="#2C6E91")
                    self.pane_error.pack(side = TOP, fill = BOTH, expand = True, padx = 10, pady = 10)
                    Label(self.pane_error, text="Phish didn't play a Set " + str(self.set_for_graph_int) + " on " + str(self.show_date) + '.', bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
        
        # Labels and inputs for show date
        pane1 = Frame(self) 
        pane1.pack(side = TOP, fill = BOTH, expand = True, padx = 10, pady = 10)
        pane1.config(bg="#2C6E91")
        Label(pane1, text="Input Show Date:", bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, expand = True, fill = BOTH)
        Label(pane1, text="Month", bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, expand = True, fill = BOTH, padx = 5, pady = 5)
        month = Entry(pane1, bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'), justify ='center')
        month.insert(0,'12')
        month.pack( side = LEFT, fill = BOTH)
        Label(pane1, text="Day", bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, expand = True, fill = BOTH, padx = 5, pady = 5)
        day = Entry(pane1, bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'), justify ='center')
        day.insert(0,'31')
        day.pack( side = LEFT, fill = BOTH)
        Label(pane1, text="Year", bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, expand = True, fill = BOTH, padx = 5, pady = 5)
        year = Entry(pane1, bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'), justify ='center')
        year.insert(0,'1999')
        year.pack( side = LEFT, fill = BOTH)
        
        
        # Labels and inputs for which set to graph
        pane2 = Frame(self, bg="#2C6E91") 
        pane2.pack(side = TOP, fill = BOTH, expand = True, padx = 10, pady = 10)
        Label(pane2, text="Choose a Set for Graph:", bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH)
        Radiobutton(pane2, text='Set 1', variable=self.set_for_graph, value=1, bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
        Radiobutton(pane2, text='Set 2', variable=self.set_for_graph, value=2, bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
        Radiobutton(pane2, text='Set 3', variable=self.set_for_graph, value=3, bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
        Radiobutton(pane2, text='Encore', variable=self.set_for_graph, value=4, bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)


        # Checkbuttons for which shows to include
        pane3 = Frame(self, bg="#2C6E91") 
        pane3.pack(side = TOP, fill = BOTH, expand = True, padx = 10, pady = 10)
        Label(pane3, text="Filter Shows For Graph:", bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack(side = LEFT)
        hue_buttons = list(range(len(self.hues)))
        hue_vars = list(range(len(self.hues)))
        for ix, text in enumerate(self.hues):
            hue_vars[ix] = IntVar()
            hue_vars[ix].set(1)
            hue_buttons[ix] = Checkbutton(pane3, text=text, variable = hue_vars[ix],bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold'))
            hue_buttons[ix].pack(side = LEFT, expand = 1)
        
        pane5 = Frame(self, bg="#2C6E91") 
        pane5.pack(side = TOP, fill = BOTH, expand = True, padx = 10, pady = 10) 
        
        # Buttons to generate graphs
        Button(pane5, text="Check Setlist", command=lambda:[reset_date(),print_setlist()], bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
        Button(pane5, text="Show Song Duration Graph", command=lambda:[reset_date(),show_graph('dur')], bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
        Button(pane5, text="Show Set Placement Graph", command=lambda:[reset_date(),show_graph('place')], bg="#2C6E91", fg = '#F15A50', font = ('ARial 18 bold')).pack( side = LEFT, fill = BOTH, expand = 1)
        
        # Frames for setlist display
        self.pane6 = Frame(self, bg="#2C6E91") 
        self.pane6.pack(fill = BOTH, expand = True)
        self.pane7 = Frame(self, bg="#2C6E91") 
        self.pane7.pack(fill = BOTH, expand = True)
        self.pane8 = Frame(self, bg="#2C6E91") 
        self.pane8.pack(fill = BOTH, expand = True)
        self.pane9 = Frame(self, bg="#2C6E91") 
        self.pane9.pack(fill = BOTH, expand = True)
        self.graph_frame = Frame(self,bg = "#2C6E91")
        self.graph_frame.pack(fill = BOTH, expand = True)
        self.pane_error = Frame(self,bg = "#2C6E91")
        self.pane_error.pack(fill = BOTH, expand = True)
        
class SetlistPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller=controller


master = Template()
master.title("Phish Show Digest App")


master.mainloop()




