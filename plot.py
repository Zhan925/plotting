from tkinter import *  # tkinter module
from tkinter import ttk  # modern themed widget set and API
import csv
from time import sleep
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas
import random

store_plots = []  # list
measurement_index = 0
end_of_comment_index = 0


def parse_swv_data(data, ramp_start_peak, ramp_end_peak):
    length = len(data)  # number of elements in my data.txt

    # Create Voltage List
    # Considers the direction of the measurement.
    # Example: If ramp_start_peak is 1200 and ramp_end_peak is 0 it will create a list
    # that starts at 1200 and decrements by 5 to the ramp_end_peak; 1200 1195  1190 ... 0
    if ramp_start_peak > ramp_end_peak:
        voltage_h = np.arange(ramp_start_peak, ramp_end_peak, -5).tolist()
    else:
        # If ramp_start_peak is 0 and ramp_end_peak is 1200 it will create a list
        # that starts at 0 and increases by 5 to the ramp_end_peak; 0 5 10 15 20 ... 1200
        voltage_h = np.arange(ramp_start_peak, ramp_end_peak, 5).tolist()

    # Separate data.txt into individual lists
    first_range = []  # rising edge
    second_range = []  # falling edge

    for i in range(length):
        if i % 2 == 0:
            first_range.append(data[i])
        else:
            second_range.append(data[i])

    # Now we have the first and second range separated we need to perform some checks
    if len(first_range) > len(second_range):
        first_range = first_range[0: len(second_range)]
    elif len(second_range) > len(first_range):
        second_range = second_range[0: len(first_range)]

    voltage_h = voltage_h[0:len(first_range)]
    if len(voltage_h) < len(first_range):
        first_range = first_range[0: len(voltage_h)]
        second_range = second_range[0: len(voltage_h)]
    if len(voltage_h) < len(second_range):
        first_range = first_range[0: len(voltage_h)]
        second_range = second_range[0: len(voltage_h)]
    # 3. Lets perform addition and subtraction
    added_range = []

    subtracted_range = []
    for i in range(len(first_range)):
        added_range.append(first_range[i] + second_range[i])
        subtracted_range.append(first_range[i] - second_range[i])  # TODO make a permanent fix for this
    return voltage_h, first_range, second_range, added_range, subtracted_range


def initialize_params():
    # swv_chg_ramp_s_p <> <>
    print(command.get())
    tmp = command.get()
    ser.write(bytes(tmp, encoding='utf8') + b'\r\n')
    sleep(2)
    print(ser.readall().decode("utf-8"))
    ser.flush()


def start_measurement():
    global store_plots, measurement_index, end_of_comment_index
    file_name = "measurement" + str(measurement_index) + ".csv"
    measurement_index = measurement_index + 1
    txt_file = open(file_name, "w")

    ser.readall()  # flush any pre-existing data that might be stuck in serial from failed measurement
    ser.flush()
    # initialize_params()

    ser.write(b'swvstart\r\n')
    sleep(10)
    temp_str = ''
    count = 0
    while count < 10:
        x = ser.read()
        if x == b'':
            if temp_str == '\n':
                count += 1
            else:
                count = 0
            continue
        print(x)
        temp_str = x.decode("ascii")
        txt_file.write(temp_str)
    txt_file.close()

    print("Reading in saved values")
    txt_file = open(file_name, "r")
    file_content = txt_file.read()
    retrieved_data = file_content.split("\n")

    end_of_comment_index = 0
    for data in retrieved_data:
        print(data)
        try:
            float(data)
            break
        except ValueError:
            # example initial raw data:
            # RampStartVoltage: 0.000000\n
            # RampPeakVoltage: 1200.000000\n
            # I split at the space, strip the new line at the end and then cast to a float
            if "RampStartVoltage" in data:
                ramp_start_voltage = float(data.split(" ")[1].strip())

            if "RampPeakVoltage" in data:
                ramp_peak_voltage = float(data.split(" ")[1].strip())
            end_of_comment_index = end_of_comment_index + 1

    print(retrieved_data)
    retrieved_data = retrieved_data[end_of_comment_index:]
    retrieved_data = retrieved_data[:-1]  # remove the last \n
    retrieved_data = [float(i) for i in retrieved_data]
    print(retrieved_data)
    txt_file.close()
    graph_elements = parse_swv_data(retrieved_data, ramp_start_voltage, ramp_peak_voltage)
    store_plots.append(graph_elements)
    print(store_plots)
    graph_output()
    # save_to_csv()


def graph_output():
    print("Graphing elements")
    index = 0

    # Global variables
    fig, ax = plt.subplots(2, 2)
    for graph_elements in store_plots:
        # rgb = (random.random(), random.random(), random.random())
        forward = ax[0, 0].plot(graph_elements[0], graph_elements[1], label="forward pulse " + str(index), linewidth=1)
        reverse = ax[0, 1].plot(graph_elements[0], graph_elements[2], label="reverse pulse " + str(index), linewidth=1)
        add = ax[1, 0].plot(graph_elements[0], graph_elements[3], label="added pulses " + str(index), linewidth=1)
        sub = ax[1, 1].plot(graph_elements[0], graph_elements[4], label="subtracted pulses " + str(index), linewidth=1)
        index = index + 1
        lines = [forward, reverse, add, sub]

    for x in range(2):
        for y in range(2):
            ax[x, y].legend(loc='upper right')
            # ax[x, y].set_picker(True)
            # ax[x, y].set_pickradius(10)
            ax[x, y].set_xlabel("Potential (V)")
            ax[x, y].set_ylabel("Current (μA)")

    ax[0, 0].set_title("forward pulse")
    ax[0, 1].set_title("reverse pulse")
    ax[1, 0].set_title("added pulse")
    ax[1, 1].set_title("subtracted pulse")

    fig.tight_layout()

    # fig.suptitle("200mM Blue Methylene")
    fig.show()
    # plt.connect('pick_event', on_pick)
    plt.show()


def on_pick(event, graphs):
    legend = event.artist
    is_visible = legend.get_visible()

    graphs[legend].set_visible(not is_visible)
    legend.set_visible(not is_visible)

    plt.draw()


def _quit():
    root.quit()
    root.destroy()


def plot_quick():
    fig = Figure(figsize=(5, 5), dpi=100)
    fig1 = Figure(figsize=(5, 5), dpi=100)
    index = 0

    #file = open("measurement4.csv", 'r')
    #data = file.readlines()
    #data = data[42:]
    #print(data[0])
    #data = data[:-1]  # remove the last \n
    #data = [float(i) for i in data]
    f = open("data03-15_18_00_44.txt", "r")
    data  =f.read()
    f.close()
    readings = []
    data = data.replace(",", "")
    data = data.split("-")[1:]
    print(data)
    good = 0
    bad = 0
    store_plots.append(parse_swv_data(data, 0., 800.))

    plot1 = fig.add_subplot()
    plot2 = fig1.add_subplot()

    for graph_elements in store_plots:
        forward = plot1.plot(graph_elements[0], graph_elements[1], label="forward pulse " + str(index), linewidth=1)
        reverse = plot1.plot(graph_elements[0], graph_elements[2], label="reverse pulse " + str(index), linewidth=1)

        add = plot2.plot(graph_elements[0], graph_elements[3], label="added pulses " + str(index), linewidth=1)
        sub = plot2.plot(graph_elements[0], graph_elements[4], label="subtracted pulses " + str(index), linewidth=1)
        index = index + 1
        lines = [forward, reverse, add, sub]

    plot1.legend(loc='upper right')
    plot2.legend(loc='upper right')
    plot1.set_xlabel("Potential (V)")
    plot1.set_ylabel("Current (μA)")
    plot2.set_xlabel("Potential (V)")
    plot2.set_ylabel("Current (μA)")

    plot1.set_title("forward/reverse pulse")
    plot2.set_title("added/subtracted pulse")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(column=0, row=7)

    canvas1 = FigureCanvasTkAgg(fig1, master=root)
    canvas1.draw()
    canvas1.get_tk_widget().grid(column=1, row=7)

    # toolbar = NavigationToolbar2Tk(canvas, root)
    # toolbar.update()
    # canvas.get_tk_widget().grid(column = 1, row=8)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    plot_quick()