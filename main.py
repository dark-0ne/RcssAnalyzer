import tkinter as tk
import Analyzer as Alz
import xml.etree.cElementTree as Et
import tkinter.messagebox as msg
from tkinter import Menu
from tkinter import ttk
from tkinter import filedialog

####################
# Globals
####################

left_passes_pos = []
right_passes_pos = []

####################
# Functions
####################


def _create_circle(x, y, r):
    return x-r, y-r, x+r, y+r


def _quit():
    main_win.quit()
    main_win.destroy()
    exit()


def draw_field():
    canvas.delete("all")
    canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill='#12ce1e')  # Background
    canvas.create_rectangle(x_start, y_start, x_end, y_end)  # Outer Field
    canvas.create_line(canvas_width / 2, y_start, canvas_width / 2, y_end, fill="#000000")  # Middle Line
    canvas.create_oval(_create_circle(canvas_width / 2, canvas_height / 2, x_bound * 12 / 100))  # Middle Circle
    canvas.create_rectangle(x_start, canvas_height / 2 + y_bound * 10 / 100, x_start - x_bound * 0.05,
                            canvas_height / 2 - y_bound * 10 / 100, fill="#000000")  # Left Goal
    canvas.create_rectangle(x_end, canvas_height / 2 + y_bound * 10 / 100, x_bound * 0.05 + x_end,
                            canvas_height / 2 - y_bound * 10 / 100, fill="#000000")  # Right Goal

    canvas.create_rectangle(x_start, canvas_height / 2 + y_bound * 27.5 / 100, x_start + 0.2 * x_bound,
                            canvas_height / 2 - y_bound * 27.5 / 100)  # Left Danger zone
    canvas.create_rectangle(x_end, canvas_height / 2 + y_bound * 27.5 / 100, x_end - 0.2 * x_bound,
                            canvas_height / 2 - y_bound * 27.5 / 100)  # Right Danger zone


def _open_log_file():

    global left_passes_pos, right_passes_pos

    analyzer = Alz.Analyzer()
    analyzer.xmlPath = filedialog.askopenfilename(filetypes=(("XML Game Files", "*.xml"), ("all files", "*.*")),
                                                  initialdir=".", title="Select XML File")
    if analyzer.xmlPath == '':
        return

    analyzer.logPath = filedialog.askopenfilename(filetypes=(("Log Files", "*.rcl"), ("all files", "*.*")),
                                                  initialdir=".", title="Select Log File")
    if analyzer.logPath == '':
        return

    analyzer.extract_rcg_file()
    analyzer.extract_log_file()
    tmpLeft, tmpRight = analyzer.analyze_possession()
    total = tmpLeft + tmpRight

    possessionLeft.set(str(100 * tmpLeft / total)[:5]+' %')
    possessionRight.set(str(100 * tmpRight/total)[:5]+' %')

    teamNameLeft.set(analyzer.teams['Left']['Name'])
    teamNameRight.set(analyzer.teams['Right']['Name'])

    goalsLeft.set(str(analyzer.teams['Left']['Score']))
    goalsRight.set(str(analyzer.teams['Right']['Score']))

    tmpLeft, tmpRight = analyzer.analyze_stamina()
    staminaLeft.set(str(tmpLeft)[:6])
    staminaRight.set(str(tmpRight)[:6])

    CompletedLeftPasses, WrongLeftPasses, CompletedRight,\
    WrongRight, LeftCorrectShoots,LeftWrongShoots,\
    RightCorrectShoots, RightWrongShoots, left_passes_pos, right_passes_pos = analyzer.analyze_kicks()

    totalLeftPasses = CompletedLeftPasses + WrongLeftPasses
    totalRightPasses = CompletedRight + WrongRight

    totalLeftShoots = LeftCorrectShoots + LeftWrongShoots
    totalRightShoots = RightCorrectShoots + RightWrongShoots

    passesLeft.set(str(totalLeftPasses)+' ('+str(CompletedLeftPasses)+')')
    passesRight.set(str(totalRightPasses) + ' (' + str(CompletedRight) + ')')

    passAccLeft.set(str(100 * CompletedLeftPasses / totalLeftPasses)[:5]+' %')
    passAccRight.set(str(100 * CompletedRight / totalRightPasses)[:5]+' %')

    shotsLeft.set(str(totalLeftShoots)+' ('+str(LeftWrongShoots)+')')
    shotsRight.set(str(totalRightShoots)+' ('+str(RightWrongShoots)+')')

    shotAccLeft.set(str(100 * LeftCorrectShoots / totalLeftShoots)[:5]+' %')
    shotAccRight.set(str(100 * RightCorrectShoots / totalRightShoots)[:5]+' %')

    left_opps, right_opps, left_clear, right_clear = analyzer.analyze_opportunities_and_clearances()

    opportunitiesLeft.set(str(left_opps))
    opportunitiesRight.set(str(right_opps))

    clearancesLeft.set(str(left_clear))
    clearancesRight.set(str(right_clear))


def draw_left_passes():
    draw_field()
    for item in left_passes_pos:
        canvas.create_oval(
            _create_circle(x_start + (item[0][0] + 53) * x_bound / 106, y_start + (item[0][1] + 35) * y_bound / 70,
                           x_bound * 0.01), fill='#ff0010')
        canvas.create_line(x_start + (item[1][0] + 53) * x_bound / 106 + x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 + y_bound * 0.0125,
                           x_start + (item[1][0] + 53) * x_bound / 106 - x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 - y_bound * 0.0125, fill='#1749ed', width=3)
        canvas.create_line(x_start + (item[1][0] + 53) * x_bound / 106 + x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 - y_bound * 0.0125,
                           x_start + (item[1][0] + 53) * x_bound / 106 - x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 + y_bound * 0.0125, fill='#1749ed', width=3)
        canvas.create_line(x_start + (item[0][0] + 53) * x_bound / 106, y_start + (item[0][1] + 35) * y_bound / 70,
                           x_start + (item[1][0] + 53) * x_bound / 106, y_start + (item[1][1] + 35) * y_bound / 70,
                           width=2, dash=(5, 3))


def draw_right_passes():
    draw_field()
    for item in right_passes_pos:
        canvas.create_oval(
            _create_circle(x_start + (item[0][0] + 53) * x_bound / 106, y_start + (item[0][1] + 35) * y_bound / 70,
                           x_bound * 0.01), fill='#ff0010')
        canvas.create_line(x_start + (item[1][0] + 53) * x_bound / 106 + x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 + y_bound * 0.0125,
                           x_start + (item[1][0] + 53) * x_bound / 106 - x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 - y_bound * 0.0125, fill='#1749ed', width=3)
        canvas.create_line(x_start + (item[1][0] + 53) * x_bound / 106 + x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 - y_bound * 0.0125,
                           x_start + (item[1][0] + 53) * x_bound / 106 - x_bound * 0.0125,
                           y_start + (item[1][1] + 35) * y_bound / 70 + y_bound * 0.0125, fill='#1749ed', width=3)
        canvas.create_line(x_start + (item[0][0] + 53) * x_bound / 106, y_start + (item[0][1] + 35) * y_bound / 70,
                           x_start + (item[1][0] + 53) * x_bound / 106, y_start + (item[1][1] + 35) * y_bound / 70,
                           width=2, dash=(5, 3))


def _save_results():

    save_file_path = filedialog.asksaveasfilename(initialdir="~/", title="Save file"
                                                  , filetypes=(("Analyze Result File", "*.azr"), ("all files", "*.*")))
    if save_file_path == ():
        return

    root = Et.Element('Data')
    left = Et.SubElement(root, 'Left')
    right = Et.SubElement(root, 'Right')

    Et.SubElement(left, 'Name').text = teamNameLeft.get()
    Et.SubElement(left, 'Possession').text = possessionLeft.get()
    Et.SubElement(left, 'Goals').text = goalsLeft.get()
    Et.SubElement(left, 'Shoots').text = shotsLeft.get()
    Et.SubElement(left, 'ShootAcc').text = shotAccLeft.get()
    Et.SubElement(left, 'Passes').text = passesLeft.get()
    Et.SubElement(left, 'PassAcc').text = passAccLeft.get()
    Et.SubElement(left, 'Opportunities').text = opportunitiesLeft.get()
    Et.SubElement(left, 'Saves').text = savesLeft.get()
    Et.SubElement(left, 'Clearances').text = clearancesLeft.get()
    Et.SubElement(left, 'Stamina').text = staminaLeft.get()

    Et.SubElement(right, 'Name').text = teamNameRight.get()
    Et.SubElement(right, 'Possession').text = possessionRight.get()
    Et.SubElement(right, 'Goals').text = goalsRight.get()
    Et.SubElement(right, 'Shoots').text = shotsRight.get()
    Et.SubElement(right, 'ShootAcc').text = shotAccRight.get()
    Et.SubElement(right, 'Passes').text = passesRight.get()
    Et.SubElement(right, 'PassAcc').text = passAccRight.get()
    Et.SubElement(right, 'Opportunities').text = opportunitiesRight.get()
    Et.SubElement(right, 'Saves').text = savesRight.get()
    Et.SubElement(right, 'Clearances').text = clearancesRight.get()
    Et.SubElement(right, 'Stamina').text = staminaRight.get()

    tree = Et.ElementTree(root)
    tree.write(save_file_path)


def _open_results():
    open_restult_file = filedialog.askopenfilename(filetypes=(("Analyze Result File", "*.azr"), ("all files", "*.*"))
                                                   , initialdir="~/", title="Select Result File")
    if open_restult_file == ():
        return
    tree = Et.parse(open_restult_file)
    root = tree.getroot()

    teamNameLeft.set(root[0].find('Name').text)
    possessionLeft.set(root[0].find('Possession').text)
    goalsLeft.set(root[0].find('Goals').text)
    shotsLeft.set(root[0].find('Shoots').text)
    shotAccLeft.set(root[0].find('ShootAcc').text)
    passesLeft.set(root[0].find('Passes').text)
    passAccLeft.set(root[0].find('PassAcc').text)
    opportunitiesLeft.set(root[0].find('Opportunities').text)
    savesLeft.set(root[0].find('Saves').text)
    clearancesLeft.set(root[0].find('Clearances').text)
    staminaLeft.set(root[0].find('Stamina').text)

    teamNameRight.set(root[1].find('Name').text)
    possessionRight.set(root[1].find('Possession').text)
    goalsRight.set(root[1].find('Goals').text)
    shotsRight.set(root[1].find('Shoots').text)
    shotAccRight.set(root[1].find('ShootAcc').text)
    passesRight.set(root[1].find('Passes').text)
    passAccRight.set(root[1].find('PassAcc').text)
    opportunitiesRight.set(root[1].find('Opportunities').text)
    savesRight.set(root[1].find('Saves').text)
    clearancesRight.set(root[1].find('Clearances').text)
    staminaRight.set(root[1].find('Stamina').text)


def _show_about():
    msg.showinfo('About', "Developed in KN2C® Robotics Lab 2018")

###################
# Procedural Code
###################

## Create Window
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 600

main_win = tk.Tk()

main_win.title("RCSS Analyzer")
main_win.minsize(height=WINDOW_HEIGHT, width=WINDOW_WIDTH)
main_win.resizable(0, 0)
## Add Menu

menuBar = Menu()
main_win.config(menu=menuBar)

## Add File Menu

fileMenu = Menu(menuBar, tearoff=0)
fileMenu.add_command(label='Open Log File', command=_open_log_file)
fileMenu.add_separator()
fileMenu.add_command(label='Open Results File', command=_open_results)
fileMenu.add_command(label='Save Results', command=_save_results)
fileMenu.add_separator()
fileMenu.add_command(label='Exit', command=_quit)
menuBar.add_cascade(label='File', menu=fileMenu)

## Add Help Menu
helpMenu = Menu(menuBar, tearoff=0)
helpMenu.add_command(label='About', command=_show_about)
menuBar.add_cascade(label='Help', menu=helpMenu)

## Tab Control
tabControl = ttk.Notebook(main_win)

statsTab = ttk.Frame(tabControl)
tabControl.add(statsTab, text='Stats')

graphTab = ttk.Frame(tabControl)
tabControl.add(graphTab, text='Graph')

tabControl.pack(expand=1, fill='both')

## Creating Frame & Setting up grid
main_frame = ttk.LabelFrame(statsTab, text='Statistics')

main_frame.grid(column=0, row=0, padx=8, pady=4)

#### Adding Labels

ttk.Label(main_frame, text='Left').grid(column=1, row=0)
ttk.Label(main_frame, text='Right').grid(column=2, row=0)

MAX_LABEL_WIDTH = 15

ttk.Label(main_frame, text='Team Name', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=1)
ttk.Label(main_frame, text='Possession', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=2)
ttk.Label(main_frame, text='Goals', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=3)
ttk.Label(main_frame, text='Shoots (Out)', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=4)
ttk.Label(main_frame, text='Shoot Accuracy', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=5)
ttk.Label(main_frame, text='Passes (Completed)', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=6)
ttk.Label(main_frame, text='Pass Accuracy', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=7)
ttk.Label(main_frame, text='Opportunities', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=8)
ttk.Label(main_frame, text='Saves', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=9)
ttk.Label(main_frame, text='Clearances', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=10)
ttk.Label(main_frame, text='Avg. Stamina', width=MAX_LABEL_WIDTH, font=("Courier 10 Pitch", 20), anchor='center').grid(column=0, row=11)

#### Text Entries

MAX_ENTRY_WIDTH = 14
ENTRY_IPADY = 7
ENTRY_PADY = 5
ENTRY_PADX = 7

teamNameLeft = tk.StringVar()
teamNameLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=teamNameLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
teamNameLeftEntry.grid(column=1, row=1,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

teamNameRight = tk.StringVar()
teamNameRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=teamNameRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
teamNameRightEntry.grid(column=2, row=1,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

possessionLeft = tk.StringVar()
possessionLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=possessionLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
possessionLeftEntry.grid(column=1, row=2,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

possessionRight = tk.StringVar()
possessionRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=possessionRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
possessionRightEntry.grid(column=2, row=2,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

goalsLeft = tk.StringVar()
goalsLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=goalsLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
goalsLeftEntry.grid(column=1, row=3,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

goalsRight = tk.StringVar()
goalsRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=goalsRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
goalsRightEntry.grid(column=2, row=3,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotsLeft = tk.StringVar()
shotsLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotsLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
shotsLeftEntry.grid(column=1, row=4,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotsRight = tk.StringVar()
shotsRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotsRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
shotsRightEntry.grid(column=2, row=4,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotAccLeft = tk.StringVar()
shotAccLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotAccLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
shotAccLeftEntry.grid(column=1, row=5,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotAccRight = tk.StringVar()
shotAccRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotAccRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
shotAccRightEntry.grid(column=2, row=5,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passesLeft = tk.StringVar()
passesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passesLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
passesLeftEntry.grid(column=1, row=6,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passesRight = tk.StringVar()
passesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passesRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
passesRightEntry.grid(column=2, row=6,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passAccLeft = tk.StringVar()
passAccLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passAccLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
passAccLeftEntry.grid(column=1, row=7,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passAccRight = tk.StringVar()
passAccRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passAccRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
passAccRightEntry.grid(column=2, row=7,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

opportunitiesLeft = tk.StringVar()
opportunitiesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=opportunitiesLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
opportunitiesLeftEntry.grid(column=1, row=8,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

opportunitiesRight = tk.StringVar()
opportunitiesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=opportunitiesRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
opportunitiesRightEntry.grid(column=2, row=8,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

savesLeft = tk.StringVar()
savesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=savesLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
savesLeftEntry.grid(column=1, row=9,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

savesRight = tk.StringVar()
savesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=savesRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
savesRightEntry.grid(column=2, row=9,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

clearancesLeft = tk.StringVar()
clearancesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=clearancesLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
clearancesLeftEntry.grid(column=1, row=10,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

clearancesRight = tk.StringVar()
clearancesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=clearancesRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
clearancesRightEntry.grid(column=2, row=10,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

staminaLeft = tk.StringVar()
staminaLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=staminaLeft, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
staminaLeftEntry.grid(column=1, row=11,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

staminaRight = tk.StringVar()
staminaRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=staminaRight, state='readonly', font=("Courier 10 Pitch", 20), justify='center')
staminaRightEntry.grid(column=2, row=11,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

graphFrame = ttk.LabelFrame(graphTab, text='Graphical Visualization')
graphFrame.grid(column=0, row=0, padx=8, pady=4)

canvas_width = WINDOW_WIDTH
canvas_height = WINDOW_HEIGHT * 5 / 6

canvas = tk.Canvas(graphFrame, width=canvas_width, height=canvas_height)
canvas.pack()

ttk.Label(graphFrame, text='Show passes for team: ', font=("Courier 10 Pitch", 16)).pack()
ttk.Button(graphFrame, text='Left', command=draw_left_passes,).pack()
ttk.Button(graphFrame, text='Right', command=draw_right_passes).pack()
ttk.Label(graphFrame, text='Red circles show passers,', font=("Courier 10 Pitch", 16)).pack()
ttk.Label(graphFrame, text='Blue crosses are receivers.', font=("Courier 10 Pitch", 16)).pack()


x_bound = canvas_width * 90 / 100
y_bound = canvas_height * 90 / 100

x_start = (canvas_width - x_bound)/2
y_start = (canvas_height - y_bound)/2

x_end = (canvas_width - x_bound)/2 + x_bound
y_end = (canvas_height - y_bound)/2 + y_bound

draw_field()

## Start GUI

main_win.mainloop()