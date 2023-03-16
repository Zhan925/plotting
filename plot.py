from tkinter import *  # tkinter module
from tkinter import ttk  # modern themed widget set
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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


def plot_quick(file_name, ramp_start_peak, ramp_end_peak):
    fig = Figure(figsize=(5, 5), dpi=100)
    fig1 = Figure(figsize=(5, 5), dpi=100)
    index = 0

    #file = open("measurement4.csv", 'r')
    #data = file.readlines()
    #data = data[42:]
    #print(data[0])
    #data = data[:-1]  # remove the last \n
    #data = [float(i) for i in data]
    f = open(file_name, "r")
    data  =f.read()
    f.close()
    readings = []
    data = data.replace(",", "")
    data = data.split("-")[1:]
    good = 0
    bad = 0
    for each in data:
        try:
            if "." in each:
                
                temp = float(each)
                if temp<1000 and temp >50:
                    readings.append(temp)
                good+=1
                
        except:
            bad+=1
            print(each)
    store_plots.append(parse_swv_data(readings, ramp_start_peak, ramp_end_peak))

    plot1 = fig.add_subplot()
    plot2 = fig1.add_subplot()
    voltage_h = []
    first_range = []
    second_range = []
    added_range = []
    subtracted_range = []
    for graph_elements in store_plots:
        voltage_h.append(graph_elements[0])
        first_range.append(graph_elements[1])
        second_range.append(graph_elements[2])
        added_range.append(graph_elements[3])
        subtracted_range.append(graph_elements[4])
        plot1.plot(graph_elements[0], graph_elements[1], label="forward pulse " + str(index), linewidth=1)
        plot1.plot(graph_elements[0], graph_elements[2], label="reverse pulse " + str(index), linewidth=1)

        plot2.plot(graph_elements[0], graph_elements[3], label="added pulses " + str(index), linewidth=1)
        plot2.plot(graph_elements[0], graph_elements[4], label="subtracted pulses " + str(index), linewidth=1)
        index = index + 1
    plot1.legend(loc='upper right')
    plot2.legend(loc='upper right')
    plot1.set_xlabel("Potential (V)")
    plot1.set_ylabel("Current (μA)")
    plot2.set_xlabel("Potential (V)")
    plot2.set_ylabel("Current (μA)")

    plot1.set_title("forward/reverse pulse")
    plot2.set_title("added/subtracted pulse")

    fig1 = plt.figure(1)
    plt.plot(voltage_h[0], first_range[0], label="forward pulse")
    plt.plot(voltage_h[0], second_range[0], label="reverse pulse ")
    plt.legend(["forward pulse", "reverse pulse"])
    plt.xlabel("Potential (V)")
    plt.ylabel("Current (μA)")
    plt.draw()
    plt.waitforbuttonpress(0)
    plt.close()

    fig2 = plt.figure(2)
    plt.plot(voltage_h[0], added_range[0], label="added pulses " )
    plt.plot(voltage_h[0], subtracted_range[0], label="subtracted pulses ")
    plt.legend(["added pulses ", "subtracted pulses " ])
    plt.xlabel("Potential (V)")
    plt.ylabel("Current (μA)")
    plt.draw()
    plt.waitforbuttonpress(0)
    plt.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Enter the file_name: ")
    file_name = input()
    print("Enter ramp start peak: ")
    ramp_start_peak = float(input())
    print("Enter ramp end peak: ")
    ramp_end_peak = float(input())
    plot_quick(file_name,ramp_start_peak, ramp_end_peak)