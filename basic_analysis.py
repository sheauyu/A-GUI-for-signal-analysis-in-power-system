import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt
from scipy import signal
import seaborn as sns; sns.set_theme()
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.colors import LogNorm, Normalize
import csv

def dyn_analysis(df,comp_var,meas_var,bsc_frame,ax):
    dyn_top = tk.Toplevel()
    dyn_top.title('Multiple dynamic performance indices')
    
    t = df.iloc[:,-1].to_numpy(dtype=float)
    y = df[comp_var.get()][meas_var.get()].to_numpy(dtype=float)
    
    steady_state = y[-1]
    max_value = np.max(y)
    t_max = t[y.argmax()]
    min_value = np.min(y)
    t_min = t[y.argmin()]
    yr = y[y.argmin()+1:]
    t_rise = t[np.where(yr>steady_state)[0][0]+y.argmin()+1]
    y_rise = y[np.where(yr>steady_state)[0][0]+y.argmin()+1]
    
    results_frame = tk.LabelFrame(dyn_top, text='', padx=10, pady=10)
    results_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
            
    results_title = tk.Label(results_frame, text='Dynamic performance indices:', font=('bold',12, "underline"))
    results_title.grid(row=0, column=0, sticky='w')
    results_label = tk.Label(results_frame, text=
                             'steady state= '+f'{steady_state}'+
                             '\nt_rise= '+f"{'%.3f' % t_rise}"+
                             '\nt_max= '+f"{'%.3f' % t_max}"+', max= '+f'{max_value}'+
                             '\nt_min= '+f"{'%.3f' % float(t_min)}"+', min= '+f"{min_value}"+
                             "\nResults are saved in csv file")
    results_label.grid(row=1, column=0, sticky='w')
    
    ax.plot(t[-1], y[-1], 'o')
    ax.plot(t_max, max_value, 'o')
    ax.plot(t_min, min_value, 'o')
    ax.plot(t_rise, y_rise, 'o')
    
    #write data to csv file
    dyn_data = [comp_var.get()+ meas_var.get()] + [steady_state, max_value, min_value, t_max, t_min, t_rise] 
    header_dyn = ['', 'steady_state', 'max_value', 'min_value', 't_max (s)', 't_min (s)', 't_rise (s)']
    
    with open('Dynamic performance indices.csv', 'w', newline='') as dyn:
        writer = csv.writer(dyn)
        writer.writerow(header_dyn)
        writer.writerow(dyn_data)

def trans(df,s,e,comp_var,meas_var):
    trans_top = tk.Toplevel()
    trans_top.title('Transience Analysis')
    
    trans_frame = tk.LabelFrame(trans_top, text='', padx=10, pady=10)
    trans_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
    
    trs_btn = tk.Button(trans_top, text='save as csv', command = lambda: trans_csv())
    trs_btn.grid(row=1, column=0, padx=10, pady=10, sticky='nw')
    
    t = df.iloc[:,-1].to_numpy(dtype=float)
    y = df[comp_var.get()][meas_var.get()].to_numpy(dtype=float)

    #Transient part
    ##window from entry
    ts = float(s.get())
    ids = int(ts*1000)
    te = float(e.get())
    ide = int(te*1000)
    t = t[ids:ide]
    y = y[ids:ide]
    idt = np.argwhere(np.diff(y)).flatten()[0]#index of the last point before transient change
    ##first point P1(td,yd) after transient change
    td = t[idt+1]
    yd = y[idt+1]
    ##last point P2(tu,yu) before stepping up again
    tu = t[idt+150]
    yu = y[idt+150]
    ##calculate slope
    k = (yu-yd)/(tu-td)
    #calculate area
    Ar = np.sum(y[idt+1:idt+151])*(tu-td)/150
    #plot transient part
    figure1, ax = plt.subplots(figsize=(12,5))
    ax.plot(t, y,label=meas_var.get())
    ax.set_ylabel(meas_var.get(), fontsize=12)
    ax.set_title(comp_var.get() + meas_var.get(), fontsize=16)   
    ax.set_xlabel('time [$s$]', fontsize=12)
    ax.legend(bbox_to_anchor=(1.0, 1.0), loc='upper right')
    #plot P1 to P2
    x_values = [td, tu]
    y_values = [yd, yu]
    ax.plot(x_values, y_values, 'ro', linestyle="--")
    ax.text(td-0.03, yd, "P1")
    ax.text(tu+0.02, yu, "P2")
    ax.text((td+tu)/2, (yd+yu)/2+0.02, f"Slope k= {'%.3f' % k}")
    ax.text((td+tu)/2, (yd+yu)/4, f"Area = {'%.3f' % Ar}")
    ax.fill_between(t[idt+1:idt+151], y[idt+1:idt+151], color = "green", alpha = 0.2, hatch = '|')
    
    canvas = FigureCanvasTkAgg(figure1, trans_frame)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, trans_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def on_key_press(event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, canvas, toolbar)
    
    canvas.mpl_connect("key_press_event", on_key_press)
    
    def trans_csv():#write data to csv file
        trs_data = [comp_var.get()+ meas_var.get()] + [td, tu, yd, yu, k, Ar] 
        header_trs = ['', 't1 (s)', 't2 (s)', 'yd', 'yu', 'Slope', 'Area']
        
        with open('Transient parameters.csv', 'w', newline='') as trs:
            writer = csv.writer(trs)
            writer.writerow(header_trs)
            writer.writerow(trs_data)
    
def osci(df,comp_var,meas_var):
    osci_top = tk.Toplevel()
    osci_top.title('Oscillation Analysis')
    
    plot_frame = tk.LabelFrame(osci_top, text='', padx=10, pady=10)
    plot_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
    
    area_frame = tk.LabelFrame(osci_top, text='', padx=10, pady=10)
    area_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nw')
    
    osci_frame = tk.LabelFrame(plot_frame, text='', padx=10, pady=10)
    osci_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
    
    osci_btn = tk.Button(area_frame, text='save as csv', command = lambda: osci_csv())
    osci_btn.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
       
    t = df.iloc[:,-1].to_numpy(dtype=float)
    y = df[comp_var.get()][meas_var.get()].to_numpy(dtype=float)
    
    #define where Oscillation part starts (tb), ends (te)
    #re_min_y = y[signal.argrelextrema(y, np.less)]
    nadir_ind = signal.argrelextrema(y,np.less)[0]
    tb = np.max(nadir_ind)
    te = len(y)
    
    #Oscillation part
    x2 = t[tb:]
    y2 = y[tb:]
    
    #to draw line y=last_value_g
    g = y[-1]
    g2 = np.array([g] * (te-tb))
    x_coordinates = [t[tb], t[te-1]]
    y_coordinates = [g, g]
    
    #plot oscillation part
    figure2, ax = plt.subplots(figsize=(12,5))
    ax.plot(x2, y2, label=meas_var.get())
    ax.plot(x_coordinates, y_coordinates, color='red')
    
    ax.set_ylabel(meas_var.get(), fontsize=12)
    ax.set_title(comp_var.get() + meas_var.get(), fontsize=16)   
    ax.set_xlabel('time [$s$]', fontsize=12)
    ax.legend(bbox_to_anchor=(1.0, 1.0), loc='upper right')
    
    #finding intersections of data plot and y=g
    idx = np.argwhere(np.diff(np.sign(y2 - g2))).flatten()#idx: relative indexes of intersections
    ax.plot(x2[idx], y2[idx], 'ro')
    
    Area_list = []
    for i in range(len(idx)-1):
        n = idx[i]
        m = idx[i+1]
        ya = np.sum(y2[n:m+1])*(x2[m]-x2[n])/(m-n+1)
        ga = g*(x2[m]-x2[n])
        Area = abs(ya-ga)
        Area_list.append(Area)
        Area_result = tk.Label(area_frame, text=f"Area{i} = ({'%.3e' % Area})")
        Area_result.grid(row=int(f'{i}')+1, column=1, sticky='w')
        #Area_result.grid.pack()
        ax.fill_between(x2[n:m+1], g2[n:m+1], y2[n:m+1], color = "yellow", alpha = 0.2, hatch = '|')
        ax.text((x2[n]+x2[m])/2, g-0.001, f'A{i}')
        #ax.text(x2[idx[-1]], g-0.001, f'P{len(idx)-1}')
            
    Area_arr = np.array(Area_list)        
    #print(Area_arr)
    def osci_csv():#write data to csv file
        osci_data = [comp_var.get()+ meas_var.get()] + [*Area_list]
        header_osci = ['Area'] + list(range(100))
        
        with open('Oscillation parameters.csv', 'w', newline='') as osci:
            writer = csv.writer(osci)
            writer.writerow(header_osci)
            writer.writerow(osci_data)
    
    canvas = FigureCanvasTkAgg(figure2, osci_frame)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, osci_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    #heat map
    hm_frame = tk.LabelFrame(plot_frame, text='', padx=10, pady=10)
    hm_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nw')
    
    figure3, ax = plt.subplots(figsize=(12,3))
    ax = sns.heatmap([Area_arr], square=True, norm=LogNorm())
    
    canvas = FigureCanvasTkAgg(figure3, hm_frame)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, hm_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    
    