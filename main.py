import tkinter as tk
from tkinter import ttk
from calc_main import start_calc
from tkinter import messagebox
from pandas import read_csv
from tkinter import filedialog as fd

root = tk.Tk()
root.title("Single Transferable Vote calculator")
root.option_add("*tearOff", False)

spreadsheet = tk.StringVar()
question = tk.StringVar()
seats = tk.StringVar()

try:
	with open("settings.txt", "r") as file:
		df = read_csv(file)

	if df.columns[0] == "Unnamed: 0":
		spreadsheet.set("")
	else:
		spreadsheet.set(df.columns[0])
	if df.columns[1] == "Unnamed: 1":
		question.set("")
	else:
		question.set(df.columns[1])
	if df.columns[2] == "Unnamed: 2":
		seats.set("")
	else:
		seats.set(df.columns[2])
except FileNotFoundError:
	pass


def error_msg() -> None:
	messagebox.showerror('Value Error', 'Error: Number of Seats needs to be a whole number that is larger than 0!')


def save_values(*kwargs) -> None:
	with open("settings.txt", "w") as file:
		file.write(",".join([*kwargs]))


def quit_program() -> None:
	_sheet = spreadsheet.get()
	_quest = question.get()
	_seats = seats.get()
	save_values(_sheet, _quest, _seats)
	root.destroy()


def call_calculator() -> None:
	_sheet = spreadsheet.get()
	_quest = question.get()
	_seats = seats.get()

	if not _seats.isnumeric() or int(_seats) < 1:
		save_values(_sheet, _quest, _seats)
		error_msg()
		return

	save_values(_sheet, _quest, _seats)
	start_calc(_sheet,  _quest, int(_seats))
	root.destroy()

def filedialoguename():
    name = fd.askopenfilename()
    entry.delete(0,tk.END)
    entry.insert(0,name)


input_frame = ttk.Frame(root, borderwidth = 3, relief = "groove")
input_frame.pack(side = "top", fill = "both", expand = True)

ttk.Label(input_frame, text = "Inputs").pack(side = "top", expand = False, fill = "y")

frame = ttk.Frame(input_frame)
frame.pack(side = "top", fill = "x", expand = True, pady = 4)
ttk.Label(frame, text = "Spreadsheet Name: ").pack(side = "left", expand = False)
entry = ttk.Entry(frame, textvariable = spreadsheet, width = 30)
entry.pack(side = "left", expand = True, fill = "x")
entry.focus()
button = ttk.Button(frame, text="Browse", command=filedialoguename)
button.pack()

frame = ttk.Frame(input_frame)
frame.pack(side = "top", fill = "x", expand = True, pady = 4)
ttk.Label(frame, text = "Question Name: ").pack(side = "left", expand = False)
ttk.Entry(frame, textvariable = question, width = 30).pack(side = "left", expand = True, fill = "x")

frame = ttk.Frame(input_frame)
frame.pack(side = "top", fill = "x", expand = True, pady = 4)
ttk.Label(frame, text = "Number of Seats: ").pack(side = "left", expand = False)
ttk.Entry(frame, textvariable = seats, width = 30).pack(side = "left", expand = True, fill = "x")


ttk.Button(root, text = "Save & Calculate", command = call_calculator).pack(side = "left", pady = (6, 4), padx = (4, 0))
ttk.Button(root, text = "Save & Quit", command = quit_program).pack(side = "right", pady = (6, 4), padx = (0, 4))

root.mainloop()
