'''
Eli Lifland
GUI for checking requirements
'''
import tkinter as tk
from functools import partial 
from copy import deepcopy 
from collections import defaultdict
from geopy import geocoders
import sc_loading
import sc_plot
import sc_lib
import sstl

DEBUG = False
PARALLEL = True

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("SaSTL Monitor")
        self.HEIGHT=1000
        self.WIDTH=1850
        self.master.geometry('{}x{}+0+0'.format(self.WIDTH,self.HEIGHT))
        self.amenity_options = ['school','theatre','hospital','restaurant','library','university','parking','bank','cinema','fire_station','prison']
        self.available_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(127,127,127),(127,127,0),(127,0,127),(0,127,127),(255,127,127)]
        self.label_options = deepcopy(self.amenity_options)
        self.label_to_nodes = defaultdict(list)
        self.labels = []
        self.varToPath = dict()
        self.label_to_color = dict()
        self.sensor_locs_path = ''
        self.reqs = list()
        self.results = list()
        self.req_list_widgets = list()
        self.results_list_widgets = list()
        self.create_widgets()
        
    def create_widgets(self):
        self.create_area_input(0,0)
        self.create_data_input(0,180)
        self.create_req_input(0,280)
        self.create_results_section(0,600)

    def create_results_section(self,xoff,yoff):
        reqs = tk.Label(self.master,text='Results')
        reqs.place(x=xoff+10,y=yoff+10)
        self.results_list_x = xoff+50
        self.results_list_y = yoff+40
        canvas = tk.Canvas(self.master)
        x_start = self.results_list_x-20 
        y_start = self.results_list_y-10
        w = self.WIDTH-2*x_start
        h = self.HEIGHT-10-y_start
        canvas.create_rectangle(0,0,w,h,width=10)
        canvas.place(x=x_start,y=y_start,width=w,height=h)

    def create_req_input(self,xoff,yoff):
        reqs = tk.Label(self.master,text='Requirements')
        reqs.place(x=xoff+10,y=yoff+10)
        add_req_formula = tk.Button(self.master,bg='white',text='...',command=self.add_req_formula)
        add_req_formula.place(x=xoff+110,y=yoff+10,width=20,height=20)
        self.create_req_dropdown_input(xoff+50,yoff+30)
        self.req_list_x = xoff+50
        self.req_list_y = yoff+150
        canvas = tk.Canvas(self.master)
        x_start = self.req_list_x-20 
        y_start = self.req_list_y-20
        w = self.WIDTH-2*x_start
        h = 600-y_start
        canvas.create_rectangle(0,0,w,h,width=10)
        canvas.place(x=x_start,y=y_start,width=w,height=h)

    def create_req_dropdown_input(self,xoff,yoff):
        the = tk.Label(self.master,text='The')
        the.place(x=xoff,y=yoff+5)
        self.agg_input = tk.StringVar(self.master)
        self.agg_input.set('')
        self.selected_agg = ''
        self.agg_options = ['','<avg>','<min>','<max>']
        self.agg_menu = tk.OptionMenu(self.master,self.agg_input,*tuple(self.agg_options),command=self.update_selected_agg)
        self.agg_menu.place(x=xoff+35,y=yoff,width=75)
        self.var_input = tk.StringVar(self.master)
        self.var_input.set('')
        self.selected_var = ''
        self.var_options = ['']
        self.var_menu_loc = [xoff+125,yoff]
        self.var_menu = tk.OptionMenu(self.master,self.var_input,*tuple(self.var_options),command=self.update_selected_var)
        self.var_menu.place(x=self.var_menu_loc[0],y=self.var_menu_loc[1],width=200)
        within = tk.Label(self.master,text='within')
        within.place(x=xoff,y=yoff+40)
        self.req_range_entry = tk.Entry(self.master)
        self.req_range_entry.place(x=xoff+50,y=yoff+40,width=30)
        km_of = tk.Label(self.master,text='km of')
        km_of.place(x=xoff+90,y=yoff+40)
        self.spatial_input = tk.StringVar(self.master)
        self.spatial_input.set('<all/everywhere>')
        self.selected_spatial = '<all/everywhere>'
        self.spatial_options = ['<all/everywhere>','<some/somewhere>']
        self.spatial_menu = tk.OptionMenu(self.master,self.spatial_input,*tuple(self.spatial_options),command=self.update_selected_spatial)
        self.spatial_menu.place(x=xoff+140,y=yoff+35,width=150)
        self.lab_input = tk.StringVar(self.master)
        self.lab_input.set('')
        self.selected_lab = ''
        self.lab_options = ['']
        self.lab_menu_loc = [xoff+300,yoff+35]
        self.lab_menu = tk.OptionMenu(self.master,self.lab_input,*tuple(self.lab_options),command=self.update_selected_lab)
        self.lab_menu.place(x=self.lab_menu_loc[0],y=self.lab_menu_loc[1],width=200)
        should = tk.Label(self.master,text='should')
        should.place(x=xoff+510,y=yoff+40)
        self.tem_input = tk.StringVar(self.master)
        self.tem_input.set('<always>')
        self.selected_tem = '<always>'
        self.tem_options = ['<always>','<eventually>']
        self.tem_menu = tk.OptionMenu(self.master,self.tem_input,*tuple(self.tem_options),command=self.update_selected_tem)
        self.tem_menu.place(x=xoff+0,y=yoff+70,width=125)
        be = tk.Label(self.master,text='be')
        be.place(x=xoff+130,y=yoff+75)
        self.rel_input = tk.StringVar(self.master)
        self.rel_input.set('<above>')
        self.selected_rel = '<above>'
        self.rel_options = ['<above>','<below>']
        self.rel_menu = tk.OptionMenu(self.master,self.rel_input,*tuple(self.rel_options),command=self.update_selected_rel)
        self.rel_menu.place(x=xoff+155,y=yoff+70,width=90)
        self.req_val_entry = tk.Entry(self.master)
        self.req_val_entry.place(x=xoff+250,y=yoff+75,width=50)
        fro = tk.Label(self.master,text='from minute')
        fro.place(x=xoff+305,y=yoff+75)
        self.req_fro_entry = tk.Entry(self.master)
        self.req_fro_entry.place(x=xoff+390,y=yoff+75,width=38)
        to = tk.Label(self.master,text='to minute')
        to.place(x=xoff+435,y=yoff+75)
        self.req_to_entry = tk.Entry(self.master)
        self.req_to_entry.place(x=xoff+505,y=yoff+75,width=38)
        add_req = tk.Button(self.master, text='+', fg='white',bg='green',
                              command=self.add_req)
        add_req.place(x=xoff+600,y=yoff+75,height=20,width=20)

    def add_req(self):
        req = sc_lib.requirement()
        req.construct_req_str(self.selected_agg,self.selected_var,self.req_range_entry.get().strip(),self.selected_spatial,self.selected_lab,self.selected_tem,self.selected_rel,self.req_val_entry.get().strip(),self.req_fro_entry.get().strip(),self.req_to_entry.get().strip())
        self.reqs.append(req)
        self.refresh_req_list()

    def update_selected_rel(self,value):
        self.selected_rel = value

    def update_selected_tem(self,value):
        self.selected_tem = value
       
    def update_selected_spatial(self,value):
        self.selected_spatial = value
       
    def update_selected_agg(self,value):
        self.selected_agg = value

    def update_selected_var(self,value):
        self.selected_var = value

    def update_selected_lab(self,value):
        self.selected_lab = value

    def refresh_var_dropdown(self):
        self.var_menu.destroy()
        options = list(self.varToPath.keys())
        if not len(options):
            options = ['']
        options = ['<{}>'.format(o) for o in options]
        self.var_menu = tk.OptionMenu(self.master,self.var_input,*tuple(options),command=self.update_selected_var)
        self.var_menu.place(x=self.var_menu_loc[0],y=self.var_menu_loc[1],width=200)

    def refresh_lab_dropdown(self):
        self.lab_menu.destroy()
        options = ['<{}s>'.format(l) for l in self.labels]
        options+=''
        self.lab_menu = tk.OptionMenu(self.master,self.lab_input,*tuple(options),command=self.update_selected_lab)
        self.lab_menu.place(x=self.lab_menu_loc[0],y=self.lab_menu_loc[1],width=200)

    def create_data_input(self,xoff,yoff):
        data=tk.Label(self.master,text='Data')
        data.place(x=xoff+10,y=yoff+10)
        sensor_locs = tk.Label(self.master,text='Sensor Locations Path')
        sensor_locs.place(x=xoff+50,y=yoff+35)
        self.sensor_entry = tk.Entry(self.master)
        self.sensor_entry.place(x=xoff+205,y=yoff+35,width=150)
        set_sensor_locs = tk.Button(self.master, text='Set', fg='white',bg='black',
                              command=self.set_sensor_locs)
        set_sensor_locs.place(x=xoff+365,y=yoff+35,height=20)
        var = tk.Label(self.master,text='Variable')
        var.place(x=xoff+50,y=yoff+60)
        self.var_entry = tk.Entry(self.master)
        self.var_entry.place(x=xoff+115,y=yoff+60,width=75)
        path = tk.Label(self.master,text='Path')
        path.place(x=xoff+215,y=yoff+60)
        self.path_entry = tk.Entry(self.master)
        self.path_entry.place(x=xoff+265,y=yoff+60,width=150)
        add_var = tk.Button(self.master, text='+', fg='white',bg='green',
                              command=self.add_var)
        add_var.place(x=xoff+435,y=yoff+60,width=20,height=20)
        self.var_list_x = xoff+50
        self.var_list_y = yoff+90
        self.add_var_list()

    def create_area_input(self,xoff,yoff):
        areas = tk.Label(self.master,text='Areas')
        areas.place(x=xoff+10,y=yoff+10)
        add_label = tk.Button(self.master,bg='white',text='...',command=self.add_label_action)
        add_label.place(x=xoff+55,y=yoff+10,width=20,height=20)
        clear = tk.Button(self.master, text='Clear', fg='white',bg='gray',
                              command=self.clear_action)
        clear.place(x=xoff+350,y=yoff+10)
        start = tk.Button(self.master, text='Start the monitor', fg='white',bg='green',
                              command=self.start_action)
        start.place(x=xoff+425,y=yoff+10)
        city_name = tk.Label(self.master,text='City Name')
        city_name.place(x=xoff+85,y=yoff+45)
        self.city_entry = tk.Entry(self.master)
        self.city_entry.place(x=xoff+170,y=yoff+45,width=100)
        OR = tk.Label(self.master,text='OR')
        OR.place(x=xoff+60,y=yoff+65)
        coords = tk.Label(self.master,text='Coordinates')
        coords.place(x=xoff+85,y=yoff+85)
        self.coords_entry = tk.Entry(self.master)
        self.coords_entry.place(x=xoff+170,y=yoff+85,width=100)
        rangel = tk.Label(self.master,text='Range')
        rangel.place(x=xoff+280,y=yoff+65)
        self.range_entry = tk.Entry(self.master)
        self.range_entry.place(x=xoff+330,y=yoff+65,width=50)
        km = tk.Label(self.master,text='km')
        km.place(x=xoff+380,y=yoff+65)
        show_map = tk.Button(self.master, text='Show Map', fg='black',bg='white',
                              command=self.show_map)
        show_map.place(x=xoff+610,y=yoff+120)
        labels = tk.Label(self.master,text='Point Of Interests Label')
        labels.place(x=xoff+50,y=yoff+120)
        self.menu_x=xoff+210
        self.menu_y=yoff+115
        self.label_list_x=xoff+50
        self.label_list_y=yoff+155
        self.add_label_menu_and_list()
        add_existing_label = tk.Button(self.master,text='+',fg='white',bg='green',command=self.add_existing_label)
        add_existing_label.place(x=self.menu_x+110,y=self.menu_y+5,width=20,height=20)
        add_loc_txt = tk.Label(self.master,text='Add a location')
        add_loc_txt.place(x=self.menu_x+150,y=self.menu_y+5)
        add_loc = tk.Button(self.master,text='+',fg='white',bg='green',command=self.add_loc_action)
        add_loc.place(x=self.menu_x+250,y=self.menu_y+5,width=20,height=20)
        
    def add_label_menu_and_list(self):
        self.label_menu_input = tk.StringVar(self.master)
        if len(self.label_options):
            self.label_menu_input.set(self.label_options[0])
            self.selected_label = self.label_options[0]
            options = self.label_options
        else:
            self.label_menu_input.set('')
            self.selected_label = ''
            options = ['']
        self.label_menu = tk.OptionMenu(self.master,self.label_menu_input,*tuple(options),command=self.update_selected_label)
        self.label_menu.place(x=self.menu_x,y=self.menu_y,width=105)
        self.label_list_widgets = []
        cur_x = self.label_list_x
        cur_y = self.label_list_y
        for i in range(len(self.labels)):
            a = self.labels[i]
            action = partial(self.remove_label,a)
            remove = tk.Button(self.master,command=action ,bg='white',fg='red',text='x')
            text = tk.Label(self.master,text=a)
            canvas = tk.Canvas(self.master)
            if a in self.label_to_color:
                color = self.label_to_color[a]
            else:
                color = self.available_colors.pop(0)
                self.label_to_color[a] = color
            hexFormat = '#%02x%02x%02x' % color
            canvas.create_rectangle(0,0,20,20,fill=hexFormat)
            remove.place(x=cur_x,y=cur_y,height=20,width=20)
            text.place(x=cur_x+22,y=cur_y)
            canvas.place(x=cur_x+32+len(a)*6.5,y=cur_y,height=20,width=20)
            cur_x+=32+len(a)*6.5+45
            self.label_list_widgets.extend([remove,text,canvas])

    def update_selected_label(self,value):
        self.selected_label = value

    def refresh_label_menu_and_list(self):
        self.label_menu.destroy()
        for w in self.label_list_widgets:
            w.destroy()
        self.add_label_menu_and_list()
        self.refresh_lab_dropdown()

    def remove_label(self,label):
        self.labels.remove(label)
        self.label_options.append(label)
        self.available_colors.append(self.label_to_color[label])
        self.label_to_color.pop(label,None)
        self.refresh_label_menu_and_list()

    def show_map(self):
        graph = self.get_current_graph()
        if not graph:
            return
        sc_plot.plot(graph,self.label_to_color)
        '''
        self.city_entry.delete(0,'end')
        self.range_entry.delete(0,'end')
        self.coords_entry.delete(0,'end')
        '''

    def get_current_graph(self):
        amenities = [l for l in self.labels if l in self.amenity_options]
        graph = sc_lib.graph()
        city_entered = self.city_entry.get().strip()
        coords_entered = self.coords_entry.get().strip()
        if len(city_entered):
            graph.city = city_entered
        center_point = (0,0)
        if len(coords_entered):
            center_point = tuple([float(s) for s in coords_entered.split(',')])
        elif len(city_entered):
            gn = geocoders.GeoNames(username='elifland')
            loc = gn.geocode(city_entered)
            center_point = (loc.latitude,loc.longitude)
        else:
            print('must enter city name or coordinates')
            return None
        if len(self.sensor_locs_path):
            graph.add_sensor_locs(self.sensor_locs_path)
        rang = 1000
        entered_rang = self.range_entry.get().strip()
        if len(entered_rang):
            rang = float(entered_rang)*1000
        graph.add_OSMnx_pois(amenities,center_point,rang)
        if graph:
            for label in self.labels:
                for node in self.label_to_nodes[label]:
                    graph.add_node(node)
        return graph

    def start_action(self):
        graph = self.get_current_graph()
        if not graph:
            return
        checker = sstl.sstl_checker(graph,self.varToPath,debug=DEBUG,parallel=PARALLEL)
        self.results = list()
        for req in self.reqs:
            robustness = checker.check_spec(req.req_str)
            result_str = 'True' if robustness>0 else 'False'
            result_str += ', Robustness = {}'.format(robustness)
            self.results.append(result_str)
        self.refresh_results_list()

    def clear_action(self):
        self.amenity_options = ['school','theatre','hospital','restaurant','library','university','parking','bank','cinema','fire_station','prison']
        self.label_options = deepcopy(self.amenity_options)
        self.label_to_nodes = defaultdict(list)
        self.labels = []
        self.varToPath = dict()
        self.label_to_color = dict()
        self.sensor_locs_path = ''
        self.available_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(127,127,127),(127,127,0),(127,0,127),(0,127,127),(255,127,127)]
        self.reqs = list()
        self.results = list()
        self.refresh_var_list()
        self.refresh_req_list()
        self.refresh_label_menu_and_list()
        self.refresh_results_list()
        self.req_list_widgets = list()
        self.results_list_widgets = list()
        self.var_entry.delete(0,'end')
        self.path_entry.delete(0,'end')
        self.sensor_entry.delete(0,'end')
        self.city_entry.delete(0,'end')
        self.range_entry.delete(0,'end')
        self.coords_entry.delete(0,'end')
        self.req_to_entry.delete(0,'end')
        self.req_fro_entry.delete(0,'end')
        self.req_range_entry.delete(0,'end')
        self.req_fro_entry.delete(0,'end')
        self.req_val_entry.delete(0,'end')
        
    def set_sensor_locs(self):
        self.sensor_locs_path = self.sensor_entry.get().strip()

    def add_var_list(self):
        self.var_list_widgets = []
        cur_x = self.var_list_x
        cur_y = self.var_list_y
        for v in self.varToPath:
            action = partial(self.remove_var,v)
            remove = tk.Button(self.master,command=action,bg='white',fg='red',text='x')
            text = tk.Label(self.master,text=v)
            remove.place(x=cur_x,y=cur_y,height=20,width=20)
            text.place(x=cur_x+22,y=cur_y)
            cur_x+=22+len(v)*7.5+25
            self.var_list_widgets.extend([remove,text])

    def refresh_var_list(self):
        for w in self.var_list_widgets:
            w.destroy()
        self.add_var_list()
        self.refresh_var_dropdown()
        #print(self.varToPath)

    def remove_var(self,var):
        self.varToPath.pop(var,None)
        self.refresh_var_list()

    def add_var(self):
        var = self.var_entry.get().strip()
        path = self.path_entry.get().strip()
        self.varToPath[var] = path
        self.var_entry.delete(0,'end')
        self.path_entry.delete(0,'end')
        self.refresh_var_list()

    def add_req_list(self):
        self.req_list_widgets = []
        cur_x = self.req_list_x
        cur_y = self.req_list_y
        count=0
        for req in self.reqs:
            count+=1
            action = partial(self.remove_req,req)
            remove = tk.Button(self.master,command=action,bg='white',fg='red',text='x')
            req_text = 'R{}: {}'.format(count,req.pretty_str)
            text = tk.Label(self.master,text=req_text)
            remove.place(x=cur_x,y=cur_y,height=20,width=20)
            text.place(x=cur_x+22,y=cur_y)
            cur_y += 20
            self.req_list_widgets.extend([remove,text])

    def refresh_req_list(self):
        for w in self.req_list_widgets:
            w.destroy()
        self.add_req_list()

    def remove_req(self,req):
        self.reqs.remove(req)
        self.refresh_req_list()

    def add_results_list(self):
        self.results_list_widgets = []
        cur_x = self.results_list_x
        cur_y = self.results_list_y
        count=0
        for result in self.results:
            count+=1
            result_text = 'R{}: {}'.format(count,result)
            text = tk.Label(self.master,text=result_text)
            text.place(x=cur_x,y=cur_y)
            cur_y += 20
            self.results_list_widgets.extend([text])

    def refresh_results_list(self):
        for w in self.results_list_widgets:
            w.destroy()
        self.add_results_list()

    def add_existing_label(self):
        if not len(self.selected_label):
            return
        self.labels.append(self.selected_label)
        self.label_options.remove(self.selected_label)
        self.refresh_label_menu_and_list()

    def add_label_action(self):
        add_label_root = tk.Tk()
        add_app = AddLabelApp(add_label_root,self)
        add_app.mainloop()

    def add_loc_action(self):
        add_loc_root = tk.Tk()
        add_app = AddLocApp(add_loc_root,self)
        add_app.mainloop()

    def add_req_formula(self):
        add_req_root = tk.Tk()
        add_app = AddReqApp(add_req_root,self)
        add_app.mainloop()

class AddReqApp(tk.Frame):
    def __init__(self,master,parent):
        super().__init__(master)
        self.master = master
        self.master.geometry('500x150+900+300')
        self.master.title('Add Requirement')
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        self.req_entry = tk.Entry(self.master)
        self.req_entry.place(x=20,y=20,width=400)
        self.req_entry.insert(0,'Type in SaSTL formula')
        self.exp_entry = tk.Entry(self.master)
        self.exp_entry.place(x=20,y=50,width=400)
        self.exp_entry.insert(0,'Type in explanation')
        add_button = tk.Button(self.master,command=self.add,bg='green',fg='white',text='+')
        add_button.place(x=430,y=50,height=20,width=20)

    def add(self):
        req = sc_lib.requirement()
        req.set_req_str(self.req_entry.get().strip())
        req.set_pretty_str(self.exp_entry.get().strip())
        self.parent.reqs.append(req)
        self.parent.refresh_req_list()
        self.req_entry.delete(0,'end')
        self.exp_entry.delete(0,'end')

class AddLocApp(tk.Frame):
    def __init__(self,master,parent):
        super().__init__(master)
        self.master = master
        self.master.geometry('550x75+900+150')
        self.master.title("Add Location")
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        add_label = tk.Label(self.master,text='Add new location to monitor')
        add_label.place(x=5,y=10)
        name_label = tk.Label(self.master,text='Name')
        name_label.place(x=5,y=35)
        self.name_entry = tk.Entry(self.master)
        self.name_entry.place(x=50,y=35,width=100)
        gps_label = tk.Label(self.master,text='GPS Coordinates')
        gps_label.place(x=160,y=35)
        self.gps_entry = tk.Entry(self.master)
        self.gps_entry.place(x=275,y=35,width=170)
        add_button = tk.Button(self.master,command=self.add,bg='white',fg='black',text='Add')
        add_button.place(x=460,y=35)

    def add(self):
        name = self.name_entry.get().strip()
        coords = tuple([float(a) for a in self.gps_entry.get().strip().split(',')])
        self.parent.labels.append(name)
        new_node = sc_lib.node(name,coords)
        new_node.data_node=False
        new_node.add_tag(name)
        self.parent.label_to_nodes[name].append(new_node)
        self.gps_entry.delete(0,'end')
        self.name_entry.delete(0,'end')
        self.parent.refresh_label_menu_and_list()

class AddLabelApp(tk.Frame):
    def __init__(self,master,parent):
        super().__init__(master)
        self.master = master
        self.master.title("Add Label")
        self.master.geometry('625x125+900+150')
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        create_label = tk.Label(self.master,text='Add new location to existing label')
        create_label.place(x=5,y=10)
        label_label = tk.Label(self.master,text='Label')
        label_label.place(x=5,y=35)
        self.label_entry = tk.Entry(self.master)
        self.label_entry.place(x=50,y=35,width=100)
        name_label = tk.Label(self.master,text='Name')
        name_label.place(x=160,y=35)
        self.name_entry = tk.Entry(self.master)
        self.name_entry.place(x=205,y=35,width=100)
        gps_label = tk.Label(self.master,text='GPS Coordinates')
        gps_label.place(x=310,y=35)
        self.gps_entry = tk.Entry(self.master)
        self.gps_entry.place(x=425,y=35,width=170)
        or_label = tk.Label(self.master,text='OR')
        or_label.place(x=5,y=55)
        create_label = tk.Label(self.master,text='Create a new label')
        create_label.place(x=5,y=75)
        self.create_entry = tk.Entry(self.master)
        self.create_entry.place(x=150,y=75,width=100)
        add_button = tk.Button(self.master,command=self.add_to_map,bg='white',fg='black',text='Add to Map')
        add_button.place(x=350,y=70)
    
    def add_to_map(self):
        new_label = self.create_entry.get().strip()
        if len(new_label):
            self.parent.labels.append(new_label)
            self.parent.refresh_label_menu_and_list()
            self.create_entry.delete(0,'end')
        else:
            label = self.label_entry.get().strip()
            name = self.name_entry.get().strip()
            coords = tuple([float(a) for a in self.gps_entry.get().strip().split(',')])
            new_node = sc_lib.node(name,coords)
            new_node.data_node=False
            new_node.add_tag(label)
            self.parent.label_to_nodes[label].append(new_node)
            self.gps_entry.delete(0,'end')
            self.label_entry.delete(0,'end')
            self.name_entry.delete(0,'end')

root = tk.Tk()
app = Application(master=root)
app.mainloop()

