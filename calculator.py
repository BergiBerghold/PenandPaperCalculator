from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
from random import randint
import xml.etree.ElementTree as ET
import sys
import csv
import os


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('frontend.ui', self)

        self.create_new = self.findChild(QtWidgets.QPushButton, "create_new")
        self.create_new.clicked.connect(self.open_character_creation)

        self.shuffle_button = self.findChild(QtWidgets.QPushButton, "shuffle_button")
        self.shuffle_button.clicked.connect(self.shuffle)

        self.newline_button = self.findChild(QtWidgets.QPushButton, "newline_button")
        self.newline_button.clicked.connect(self.new_line)

        self.output_table = self.findChild(QtWidgets.QTableWidget, "output_table")
        self.output_table.cellPressed.connect(self.table_buttons)

        self.rounds_counter = 0
        self.max_rounds = 0

        self.scrollarea_player = self.findChild(QtWidgets.QScrollArea, "scrollarea_player").findChild(QtWidgets.QWidget, "scrollAreaWidgetContents")
        self.scrollarea_npc = self.findChild(QtWidgets.QScrollArea, "scrollarea_npc").findChild(QtWidgets.QWidget, "scrollAreaWidgetContents_2")

        self.characters = []
        self.load_characters()
        self.layout_saved_table()

        self.show()

    def open_character_creation(self):
        self.character_creation_window = CharacterCreation()
        self.character_creation_window.show()

    def load_characters(self):
        for character in os.listdir('characters'):
            if character[:-4] not in [x['name'] for x in self.characters]:
                tree = ET.parse('characters/' + character)
                root = tree.getroot()

                name = root[0].text
                type = root[1].text
                value = root[2].text
                life = root[3].text

                checkbox = QCheckBox(name)
                checkbox.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                             QtWidgets.QSizePolicy.Fixed))
                checkbox.setMinimumSize(0, 20)

                character_dict = {'name':name, 'type':type, 'value':value, 'life':life, 'checkbox':checkbox}
                self.characters.append(character_dict)
                self.layout_character(character_dict)

    def save_table(self):
        with open('last_state.csv', mode='w') as file:
            file_writer = csv.writer(file, delimiter='|', quotechar='"', quoting=csv.QUOTE_NONE)

            for row in range(self.output_table.rowCount()):
                row_list = []
                for column in range(self.output_table.columnCount()-3):
                    row_list.append(self.output_table.item(row, column).text())

                file_writer.writerow(row_list)

    def layout_character(self, character_dict):
        if character_dict['type'] == 'Player':
            self.scrollarea_player.layout().addWidget(character_dict['checkbox'])

        else:
            self.scrollarea_npc.layout().addWidget(character_dict['checkbox'])

    def layout_saved_table(self):
        try:
            with open('last_state.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='|')
                csv_list = []
                for row in csv_reader:
                    csv_list.append(row)

        except:
            pass

        else:
            if csv_list:
                self.output_table.setRowCount(len(csv_list))
                self.output_table.setColumnCount(8)

                self.output_table.setHorizontalHeaderLabels(['Character Name', 'Dice', 'Life Points', 'Status', 'Rounds left on Status', 'Move Down', 'Move Up', 'Delete'])

                for row, elem in enumerate(csv_list):
                    for column, cell_text in enumerate(elem):
                        item = QTableWidgetItem(cell_text)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.output_table.setItem(row, column, item)

                    item = QTableWidgetItem('↓')
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.output_table.setItem(row, 5, item)
                    self.output_table.item(row, 5).setBackground(QtGui.QColor(227, 219, 195))

                    item = QTableWidgetItem('↑')
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.output_table.setItem(row, 6, item)
                    self.output_table.item(row, 6).setBackground(QtGui.QColor(227, 219, 195))

                    item = QTableWidgetItem('Delete')
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.output_table.setItem(row, 7, item)
                    self.output_table.item(row, 7).setBackground(QtGui.QColor(227, 219, 195))

                header = self.output_table.horizontalHeader()
                for column in range(self.output_table.columnCount() - 3):
                    header.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)

                self.rounds_counter = 0
                self.max_rounds = len(csv_list) - 1
                self.select_row(0)

    def shuffle(self):
        selected_characters = [x for x in self.characters if x['checkbox'].isChecked()]
        characters_random_score = [int(x['value']) + randint(1,20) for x in selected_characters]

        sorting_tuple = (characters_random_score, selected_characters)

        while True:
            try:
                sorted_tuple = sorted(zip(*sorting_tuple))
            except:
                characters_random_score = [randint(1, 20) for x in selected_characters]
                sorting_tuple = sorting_tuple[:-1] + (characters_random_score,) + (sorting_tuple[-1],)
            else:
                break

        sorted_tuple = sorted_tuple[::-1]

        self.output_table.setRowCount(len(sorted_tuple))
        self.output_table.setColumnCount(8)

        self.output_table.setHorizontalHeaderLabels(['Character Name', 'Dice', 'Life Points', 'Status', 'Rounds left on Status', 'Move Down', 'Move Up', 'Delete'])

        for idx, character in enumerate(sorted_tuple):
            item = QTableWidgetItem(character[-1]['name'])
            item.setTextAlignment(Qt.AlignCenter)
            self.output_table.setItem(idx, 0, item)

            item = QTableWidgetItem(str(sorted_tuple[idx][:-1]))
            item.setTextAlignment(Qt.AlignCenter)
            self.output_table.setItem(idx, 1, item)

            item = QTableWidgetItem(character[-1]['life'])
            item.setTextAlignment(Qt.AlignCenter)
            self.output_table.setItem(idx, 2, item)

            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            self.output_table.setItem(idx, 3, item)

            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            self.output_table.setItem(idx, 4, item)

            item = QTableWidgetItem('↓')
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.output_table.setItem(idx, 5, item)
            self.output_table.item(idx, 5).setBackground(QtGui.QColor(227, 219, 195))

            item = QTableWidgetItem('↑')
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.output_table.setItem(idx, 6, item)
            self.output_table.item(idx, 6).setBackground(QtGui.QColor(227, 219, 195))

            item = QTableWidgetItem('Delete')
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.output_table.setItem(idx, 7, item)
            self.output_table.item(idx, 7).setBackground(QtGui.QColor(227, 219, 195))

        header = self.output_table.horizontalHeader()
        for column in range(self.output_table.columnCount()-3):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)

        self.rounds_counter = 0
        self.max_rounds = len(sorted_tuple)-1
        self.select_row(0)

    def table_buttons(self, row, column):
        if column == 7:
            self.output_table.removeRow(row)
            self.max_rounds -= 1

        if column == 5 and row != self.output_table.rowCount()-1:
            self.switch_row(row, move_down=True)

        if column == 6 and row != 0:
            self.switch_row(row, move_down=False)

    def switch_row(self, row, move_down):
        for column in range(self.output_table.columnCount()):
            item_to_move = self.output_table.takeItem(row, column)

            if move_down:
                item_to_move_away = self.output_table.takeItem(row+1, column)

                self.output_table.setItem(row, column, item_to_move_away)
                self.output_table.setItem(row+1, column, item_to_move)

            else:
                item_to_move_away = self.output_table.takeItem(row-1, column)

                self.output_table.setItem(row, column, item_to_move_away)
                self.output_table.setItem(row-1, column, item_to_move)

        self.select_row(self.rounds_counter)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            try:
                rounds_on_status = int(self.output_table.item(self.rounds_counter, 4).text())
            except:
                pass
            else:
                if rounds_on_status > 1:
                    item = QTableWidgetItem(str(rounds_on_status - 1))
                else:
                    item = QTableWidgetItem()
                    self.output_table.setItem(self.rounds_counter, 3, item)

                    item = QTableWidgetItem()

                item.setTextAlignment(Qt.AlignCenter)
                self.output_table.setItem(self.rounds_counter, 4, item)

            if self.rounds_counter < self.max_rounds:
                self.rounds_counter += 1
                self.select_row(self.rounds_counter)

            else:
                self.rounds_counter = 0
                self.select_row(self.rounds_counter)

        if event.key() == Qt.Key_1:
            self.save_table()

    def select_row(self, row_idx):
        for row in range(self.output_table.rowCount()):
            for column in range(self.output_table.columnCount()-3):
                self.output_table.item(row, column).setBackground(QtGui.QColor(255, 255, 255))

        for column in range(self.output_table.columnCount()-3):
            self.output_table.item(row_idx, column).setBackground(QtGui.QColor(70, 198, 200))

    def new_line(self):
        new_line_idx = self.output_table.rowCount()
        self.output_table.insertRow(new_line_idx)
        self.max_rounds += 1

        for i in range(5):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            self.output_table.setItem(new_line_idx, i, item)

        item = QTableWidgetItem('↓')
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.output_table.setItem(new_line_idx, 5, item)
        self.output_table.item(new_line_idx, 5).setBackground(QtGui.QColor(227, 219, 195))

        item = QTableWidgetItem('↑')
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.output_table.setItem(new_line_idx, 6, item)
        self.output_table.item(new_line_idx, 6).setBackground(QtGui.QColor(227, 219, 195))

        item = QTableWidgetItem('Delete')
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.output_table.setItem(new_line_idx, 7, item)
        self.output_table.item(new_line_idx, 7).setBackground(QtGui.QColor(227, 219, 195))

    def closeEvent(self, event):
        self.save_table()

class CharacterCreation(QtWidgets.QDialog):
    def __init__(self):
        super(CharacterCreation, self).__init__()
        uic.loadUi('character_creation_window.ui', self)

        self.character_name = self.findChild(QtWidgets.QLineEdit, "character_name")
        self.character_type = self.findChild(QtWidgets.QComboBox, "character_type")
        self.character_value = self.findChild(QtWidgets.QSpinBox, "character_value")
        self.character_life = self.findChild(QtWidgets.QSpinBox, "character_life")

        self.save_character = self.findChild(QtWidgets.QPushButton, "save_character")
        self.save_character.clicked.connect(self.save)

    def save(self):
        character_data = ET.Element('character_data')

        character_name = ET.SubElement(character_data, 'character_name')
        character_type = ET.SubElement(character_data, 'character_type')
        character_value = ET.SubElement(character_data, 'character_value')
        character_life = ET.SubElement(character_data, 'character_life')

        name = self.character_name.text()

        while name in os.listdir('characters'):
            name += "_new"

        character_name.text = name
        character_type.text = str(self.character_type.currentText())
        character_value.text = str(self.character_value.value())
        character_life.text = str(self.character_life.value())

        with open('characters/' + name + '.xml', 'w') as file:
            file.write(ET.tostring(character_data).decode("utf-8"))

        self.character_name.setText('')
        self.character_value.setValue(0)
        self.character_life.setValue(0)

        window.load_characters()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()