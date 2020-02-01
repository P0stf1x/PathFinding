import math
from tkinter import *
from tkinter import messagebox as mb
from tkinter.ttk import Combobox

startcolor = '#ffffff'
cells = 10

startCell = None
finishCell = None

root = Tk()

instrument = 'wall'


def drawPath(path, loop=False):  # Закрасить путь от Начальной точки до конечной
    if not loop:
        clearPath()
    global startCell
    global finishCell
    try:
        if path[0] != startCell and path[0] != finishCell:
            path[0].state = 'path'
            path[0].changeColor()
        newPath = path
        newPath.remove(path[0])
        root.after(100, drawPath, newPath, True)
    except:
        return None


def buildPath(toNode, path=[]):  # Построить путь от старта до финиша
    path.append(toNode)
    toNode = toNode.previous
    if toNode == None:
        root.after(250, drawPath, path)
        return path
    else:
        root.after(10, buildPath, toNode, path)


def distance(a, b):
    return abs(a.getCoords()[0] - b.getCoords()[0]) + abs(a.getCoords()[1] - b.getCoords()[1])


def chooseNextCell(arr):
    global alg
    if alg == 'Случайный':
        import random
        return arr[random.randrange(0, len(arr))]
    elif alg == 'По порядку':
        return arr[0]
    else:
        min_cost = None
        best_node = None
        global finishCell

        for node in arr:
            cost_start_to_node = node.cost
            cost_node_to_goal = distance(node, finishCell)
            total_cost = cost_start_to_node + cost_node_to_goal

            if min_cost == None or min_cost > total_cost:
                min_cost = total_cost
                best_node = node

        return best_node


def findPath(loop=True, reachable=[startCell], explored=[]):
    global startCell
    global finishCell
    if startCell == None or finishCell == None:
        print('Не задана начальная или конечная точка')
        return None
    if len(reachable) == 0:
        loop = False
    if loop == True:
        cell = chooseNextCell(reachable)  # Выбор новой клетки

        if cell == finishCell:  # Если текущаю клетка совпадает с конечной - завершить функицю
            return buildPath(finishCell)

        reachable.remove(cell)  # Если клетка не совпадает, удалить её из reachable и добавить в explored
        explored.append(cell)
        if cell.state == 'empty':
            cell.state = 'explored'
            cell.changeColor()

        newReachable = cell.getNearbyCells()
        if newReachable != []:
            for x in explored:  # Найти новые доступные клетки
                if x in newReachable:
                    newReachable.remove(x)
            for nearby in newReachable:
                if nearby.state == 'empty' or nearby.state == 'flag' or nearby.state == 'empty':
                    if nearby not in reachable:
                        nearby.previous = cell  # Записать предыдущую клетку
                        reachable.append(nearby)
                    if cell.cost + 1 < nearby.cost:
                        nearby.previous = cell
                        nearby.cost = cell.cost + 1
        root.after(150, findPath, True, reachable, explored)
    else:
        return None


class myButton(Button):  # Собственный класс кнопки на основе уже существуюшего в tkinter
    def __init__(self, *args, x, y, **kwargs):
        Button.__init__(self, *args, command=self.onClick,
                        **kwargs)  # Создание кнопки с вызовом onClick по нажатию
        self.x = x
        self.y = y
        self.state = 'empty'
        self.changingColor = False
        self.previous = None
        self.cost = math.inf

    def onClick(self):  # Обработка действия с кнопкой на основе выбранного инструмента
        global instrument
        if instrument == 'flag':  # Удалить конец во всех других клетках
            clearFinish()
            global finishCell
            finishCell = self
        if instrument == 'start':  # Удалить начало во всех других клетках
            clearStart()
            global startCell
            startCell = self
            self.cost = 0
        self.state = instrument
        self.changeColor()

    def changeColor(self, loop=False, step=1):  # Считает разницу цвета для анимации изменения цвета
        if self.state == 'wall':  # Выбор цвета по состоянию клетки
            nextColor = '#000000'
        elif self.state == 'path':
            nextColor = '#0000ff'
        elif self.state == 'explored':
            nextColor = '#ff0000'
        elif self.state == 'start':
            nextColor = '#00f000'
        elif self.state == 'flag':
            nextColor = '#ffff00'
        else:  # Состояние empty
            nextColor = '#ffffff'
        if self.changingColor == False:
            if self.cget('bg') == nextColor:
                self.state = 'empty'
                nextColor = '#ffffff'

        if loop:
            decColor = hex_to_rgb(self.cget('bg'))  # Получение цвета в формате rgb
            steps = 30  # За сколько шагов выполнится смена цвета
            newDecColor = (  # Нахождение нового цвета с учётом количество шагов цикла steps
                int(decColor[0] + (self.dR / steps)), int(decColor[1] + self.dG / steps),
                int(decColor[2] + self.dB / steps))
            newDecColor = self.roundColor(newDecColor)
            newHexColor = rgb_to_hex(newDecColor)
            self.configure(bg=newHexColor)
            self.configure(activebackground=newHexColor)
            if step < steps:  # Проверка на выполненость цикла, если нет - через 16 мс цикл запускается ещё раз
                root.after(10, self.changeColor, True, step + 1)
            else:
                self.configure(bg=nextColor)  # После выполнения цикла, в связи с округлением возникает неточность
                self.configure(activebackground=nextColor)  # Чтобы её исправить меняем цвет точно на заданный
                self.configure(state=NORMAL)
                self.changingColor = False

        elif self.changingColor == False:
            self.changingColor = True  # Блокировка изменения цвета кнопки ещё раз пока она не закончит изменяться
            currentColor = hex_to_rgb(self.cget('bg'))
            newColor = hex_to_rgb(nextColor)
            self.dR = newColor[0] - currentColor[0]  # Поиск разницы цвета благодаря вычитанию старого цвета из нового
            self.dG = newColor[1] - currentColor[1]
            self.dB = newColor[2] - currentColor[2]
            self.configure(state=DISABLED)
            self.changeColor(True)

    def roundColor(self, color):  # Так как нельзя использовать нецелые числа, один из цветов может получиться меньше
        newColor = [0, 0, 0]  # 0, или больше 255, чтобы избежать этого нужна эта функция, которая ограничивает число
        newColor[0] = min(max(color[0], 0), 255)
        newColor[1] = min(max(color[1], 0), 255)
        newColor[2] = min(max(color[2], 0), 255)
        return tuple(newColor)

    def reset(self):  # Очистить клетку
        self.state = 'empty'
        self.changingColor = False
        self.changeColor()

    def resetStart(self):
        if self.state == 'start':
            self.cost = math.inf
            self.reset()

    def resetPath(self):
        if self.state == 'path':
            self.reset()

    def resetExplored(self):
        if self.state == 'explored':
            self.reset()

    def resetFinish(self):
        if self.state == 'flag':
            self.reset()

    def getNearbyCells(self):
        global cells
        coords = self.getCoords()
        givenCoords = []
        if coords[0] > 2:
            givenCoords.append(self.getCoords(-1, 0, True))
        if coords[0] < cells + 1:
            givenCoords.append(self.getCoords(1, 0, True))
        if coords[1] > 0:
            givenCoords.append(self.getCoords(0, -1, True))
        if coords[1] < cells - 1:
            givenCoords.append(self.getCoords(0, 1, True))
        for i in givenCoords:
            if i.state != 'empty' and i.state != 'flag':
                givenCoords.remove(i)
        return givenCoords

    def getCoords(self, xoffset=0, yoffset=0, obj=False):
        if obj == False:
            return (self.x + xoffset, self.y + yoffset)
        else:
            return widgets[self.x + xoffset][self.y + yoffset]


widgets = [  # Создание 2д массива размером 4x3
    [myButton(x=x, y=y, width=2, height=1, bg=startcolor, activebackground=startcolor, relief=FLAT, padx=3, pady=3)
     for y in range(cells)]
    for x in range(cells + 2)]

for x in range(len(widgets)):
    Grid.columnconfigure(root, x, weight=1)
    for y in range(len(widgets[x])):
        Grid.rowconfigure(root, y, weight=1)

for y in range(len(widgets[0])):  # Заполнение 1-2 столбца таблицы пустыми строками для работы с функцией place
    widgets[0][y] = ''
    widgets[1][y] = ''

alg = 'A*'


def changeAlg():
    global alg
    newAlg = widgets[0][0].get()
    print(newAlg)
    alg = newAlg


#  Боковые виджеты управления
sortAlgs = ['A*', 'Случайный', 'По порядку']
if True:
    widgets[0][0] = Combobox(root)
    widgets[0][0]['values'] = sortAlgs
    widgets[0][0].current(0)
    widgets[0][0].bind("<<ComboboxSelected>>", lambda event: changeAlg())
    widgets[0][3] = Button(text='Очистить путь', command=lambda: clearExplored())
    widgets[0][2] = Button(text='Очистить поле', command=lambda: clear())
    widgets[0][5] = Button(text='Начальная точка', command=lambda: changeInstrument('start'))
    widgets[1][5] = Button(text='Конечная точка', command=lambda: changeInstrument('flag'))
    widgets[0][6] = Button(text='Стена', command=lambda: changeInstrument('wall'))
    widgets[0][8] = Button(text='Найти путь', command=lambda: FNDPTH())
    widgets[0][9] = Button(text='О программе', command=lambda: about())


# for item in sortAlgs:
#     widgets[0][0].insert(END, item)

def about():
    mb.showinfo("О программе",
                "Алгоритм нахождения пути\n\nДля конкурса «Нам с IT по пути»\nВ номинации «Обучающее приложение»\nАвтор программы: Щербаков Никита Сергеевич\n\nВерсия 2")


def FNDPTH():
    clearPrevious()
    clearExplored()
    global startCell
    root.after(250, findPath, True, [startCell], [])


def getByXY(coord):
    return widgets[coord[0]][coord[1]]


def changeInstrument(inst):
    global instrument
    instrument = inst


def clear():
    global startCell
    global finishCell
    startCell = None
    finishCell = None
    for x in range(2, len(widgets)):
        for y in range(len(widgets[x])):
            widgets[x][y].reset()


def clearStart():
    global startCell
    startCell = None
    for x in range(2, len(widgets)):
        for y in range(len(widgets[x])):
            widgets[x][y].resetStart()


def clearFinish():
    global finishCell
    finishCell = None
    for x in range(2, len(widgets)):
        for y in range(len(widgets[x])):
            widgets[x][y].resetFinish()


def clearPath():
    for x in range(2, len(widgets)):
        for y in range(len(widgets[x])):
            widgets[x][y].resetPath()


def clearPrevious():
    for x in range(2, len(widgets)):
        for y in range(len(widgets[x])):
            widgets[x][y].previous = None


def clearExplored():
    clearPath()
    for x in range(2, len(widgets)):
        for y in range(len(widgets[x])):
            widgets[x][y].resetExplored()


def place(x, y, colspan=1, rowspan=1):  # Функция отрисовки виджетов соответственно их расположению в массиве widgets
    if widgets[x][y] != '':
        if x == 0 and y != 5:
            colspan = 2
        return widgets[x][y].grid(column=x, row=y, padx=1, pady=1, sticky=N + S + E + W, columnspan=colspan,
                                  rowspan=rowspan)


def hex_to_rgb(value):  # Перевод цвета из hex в dec систему счисления
    value = value[1:]
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_hex(rgb):  # Перевод цвета из dec в hex систему счисления
    return '#%02x%02x%02x' % rgb


for x in range(len(widgets)):  # Отрисовка всех виджетов
    for y in range(len(widgets[x])):
        place(x, y)

root.title('Поиск пути')
root.mainloop()
