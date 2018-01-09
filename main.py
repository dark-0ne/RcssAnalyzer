import tkinter as tk
import Analyzer as alz
from tkinter import  Menu
from tkinter import ttk
from tkinter import filedialog
####################
#### Functions
####################
def _quit():
    main_win.quit()
    main_win.destroy()
    exit()

def _open_log_file():

    analyzer = alz.Analyzer()
    analyzer.xmlPath = filedialog.askopenfilename(filetypes=(("XML Game Files", "*.xml"), ("all files", "*.*")),
                                                  initialdir=".", title="Select XML File")
    analyzer.logPath = filedialog.askopenfilename(filetypes=(("Log Files", "*.rcl"), ("all files", "*.*")),
                                                  initialdir=".", title="Select Log File")
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
    staminaLeft.set(str(tmpLeft))
    staminaRight.set(str(tmpRight))

    tmpCompletedLeft, tmpCompletedRight, tmpWrongLeft, tmpWrongRight, tmpLeftShoots, tmpRightShoots = analyzer.analyze_kicks()

    totalLeft = tmpCompletedLeft + tmpWrongLeft;
    totalRight = tmpCompletedRight + tmpWrongRight

    passesLeft.set(str(totalLeft)+' ('+str(tmpCompletedLeft)+')')
    passesRight.set(str(totalRight) + ' (' + str(tmpCompletedRight) + ')')

    passAccLeft.set(str(100 * tmpCompletedLeft / totalLeft)[:5]+' %')
    passAccRight.set(str(100 * tmpCompletedRight / totalRight)[:5]+' %')

    shotsLeft.set(str(tmpLeftShoots))
    shotsRight.set(str(tmpRightShoots))

    shotAccLeft.set(str(100 * analyzer.teams['Left']['Score'] / (analyzer.teams['Left']['Score'] + tmpLeftShoots))[:5]+' %')
    shotAccRight.set(str(100 * analyzer.teams['Right']['Score'] / (analyzer.teams['Right']['Score'] + tmpRightShoots))[:5]+' %')



###################
###### Procedural Code
###################

## Create Window
main_win = tk.Tk()

main_win.title("RCSS Analyzer")
main_win.minsize(height=300, width=360)
main_win.resizable(0, 0)
## Add Menu

menuBar = Menu()
main_win.config(menu=menuBar)

## Add File Menu

fileMenu = Menu(menuBar, tearoff=0)
fileMenu.add_command(label='Open Log File',command=_open_log_file)
fileMenu.add_separator()
fileMenu.add_command(label='Open Results File')
fileMenu.add_command(label='Save Results')
fileMenu.add_separator()
fileMenu.add_command(label='Exit', command=_quit)
menuBar.add_cascade(label='File', menu=fileMenu)

## Add Help Menu
helpMenu = Menu(menuBar, tearoff=0)
helpMenu.add_command(label='About')
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

MAX_LABEL_WIDTH = 20

ttk.Label(main_frame, text='Team Name', width=MAX_LABEL_WIDTH).grid(column=0, row=1)
ttk.Label(main_frame, text='Possession', width=MAX_LABEL_WIDTH).grid(column=0, row=2)
ttk.Label(main_frame, text='Goals', width=MAX_LABEL_WIDTH).grid(column=0, row=3)
ttk.Label(main_frame, text='Out of bound Shoots', width=MAX_LABEL_WIDTH).grid(column=0, row=4)
ttk.Label(main_frame, text='Shoot Accuracy', width=MAX_LABEL_WIDTH).grid(column=0, row=5)
ttk.Label(main_frame, text='Passes (Completed)', width=MAX_LABEL_WIDTH).grid(column=0, row=6)
ttk.Label(main_frame, text='Pass Accuracy', width=MAX_LABEL_WIDTH).grid(column=0, row=7)
ttk.Label(main_frame, text='Opportunities', width=MAX_LABEL_WIDTH).grid(column=0, row=8)
ttk.Label(main_frame, text='Saves', width=MAX_LABEL_WIDTH).grid(column=0, row=9)
ttk.Label(main_frame, text='Clearances', width=MAX_LABEL_WIDTH).grid(column=0, row=10)
ttk.Label(main_frame, text='Avg. Stamina', width=MAX_LABEL_WIDTH).grid(column=0, row=11)

#### Text Entries

MAX_ENTRY_WIDTH = 12
ENTRY_IPADY = 5
ENTRY_PADY = 3
ENTRY_PADX = 5

teamNameLeft = tk.StringVar()
teamNameLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=teamNameLeft, state='readonly')
teamNameLeftEntry.grid(column=1, row=1,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

teamNameRight = tk.StringVar()
teamNameRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=teamNameRight, state='readonly')
teamNameRightEntry.grid(column=2, row=1,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

possessionLeft = tk.StringVar()
possessionLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=possessionLeft, state='readonly')
possessionLeftEntry.grid(column=1, row=2,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

possessionRight = tk.StringVar()
possessionRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=possessionRight, state='readonly')
possessionRightEntry.grid(column=2, row=2,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

goalsLeft = tk.StringVar()
goalsLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=goalsLeft, state='readonly')
goalsLeftEntry.grid(column=1, row=3,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

goalsRight = tk.StringVar()
goalsRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=goalsRight, state='readonly')
goalsRightEntry.grid(column=2, row=3,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotsLeft = tk.StringVar()
shotsLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotsLeft, state='readonly')
shotsLeftEntry.grid(column=1, row=4,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotsRight = tk.StringVar()
shotsRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotsRight, state='readonly')
shotsRightEntry.grid(column=2, row=4,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotAccLeft = tk.StringVar()
shotAccLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotAccLeft, state='readonly')
shotAccLeftEntry.grid(column=1, row=5,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

shotAccRight = tk.StringVar()
shotAccRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=shotAccRight, state='readonly')
shotAccRightEntry.grid(column=2, row=5,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passesLeft = tk.StringVar()
passesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passesLeft, state='readonly')
passesLeftEntry.grid(column=1, row=6,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passesRight = tk.StringVar()
passesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passesRight, state='readonly')
passesRightEntry.grid(column=2, row=6,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passAccLeft = tk.StringVar()
passAccLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passAccLeft, state='readonly')
passAccLeftEntry.grid(column=1, row=7,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

passAccRight = tk.StringVar()
passAccRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=passAccRight, state='readonly')
passAccRightEntry.grid(column=2, row=7,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

opportunitiesLeft = tk.StringVar()
opportunitiesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=opportunitiesLeft, state='readonly')
opportunitiesLeftEntry.grid(column=1, row=8,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

opportunitiesRight = tk.StringVar()
opportunitiesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=opportunitiesRight, state='readonly')
opportunitiesRightEntry.grid(column=2, row=8,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

savesLeft = tk.StringVar()
savesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=savesLeft, state='readonly')
savesLeftEntry.grid(column=1, row=9,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

savesRight = tk.StringVar()
savesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=savesRight, state='readonly')
savesRightEntry.grid(column=2, row=9,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

clearancesLeft = tk.StringVar()
clearancesLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=clearancesLeft, state='readonly')
clearancesLeftEntry.grid(column=1, row=10,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

clearancesRight = tk.StringVar()
clearancesRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=clearancesRight, state='readonly')
clearancesRightEntry.grid(column=2, row=10,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

staminaLeft = tk.StringVar()
staminaLeftEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=staminaLeft, state='readonly')
staminaLeftEntry.grid(column=1, row=11,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)

staminaRight = tk.StringVar()
staminaRightEntry = ttk.Entry(main_frame, width=MAX_ENTRY_WIDTH, textvariable=staminaRight, state='readonly')
staminaRightEntry.grid(column=2, row=11,ipady=ENTRY_IPADY, pady=ENTRY_PADY, padx=ENTRY_PADX)




## Start GUI

main_win.mainloop()