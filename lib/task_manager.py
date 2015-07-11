#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from lib.module import Lib
import operator

class TaskManager(object):

    def __init__(self):


        self.tm_departments = {"Script": 0, "Storyboard": 1, "References": 2, "Concepts": 3, "Modeling": 4, "Texturing": 5,
                            "Rigging": 6, "Animation": 7, "Simulation": 8, "Shading": 9, "Layout": 10,
                            "DMP": 11, "Compositing": 12, "Editing": 13, "RnD": 14}

        self.tm_departments_shortname = {"Script": "spt", "Storyboard": "stb", "References": "ref", "Concepts": "cpt",
                                         "Modeling": "mod", "Texturing": "tex", "Rigging": "rig", "Animation": "anm",
                                         "Simulation": "sim", "Shading": "shd", "Layout": "lay", "DMP": "dmp",
                                         "Compositing": "cmp", "Editing": "edt", "RnD": "rnd"}

        self.status = {"Ready to Start": 0, "In Progress": 1, "On Hold": 2, "Waiting for Approval": 3, "Retake": 4,
                       "Done": 5}

        self.members_id = {"achaput": 0, "costiguy": 1, "cgonnord": 2, "dcayerdesforges": 3,
                           "earismendez": 4, "erodrigue": 5, "jberger": 6, "lgregoire": 7,
                           "lclavet": 8, "mchretien": 9, "mbeaudoin": 10,
                           "mroz": 11, "obolduc": 12, "slachapelle": 13, "thoudon": 14,
                           "vdelbroucq": 15, "yjobin": 16, "yshan": 17}

        # The itemChanged signal connection of the QTableWidget is fired every time
        # an item changes on the tablewidget. Therefore whenever we're adding an entry to the tablewidget, the itemChanged
        # slot is fired. The item_added variable is used to know when the user adds a row and when a user update a row
        # if item_added is set to true, then the user is simply adding a row and not updating it.
        # Therefore, the update_task function is disabled when the item_added variable is set to true.

        self.item_added = False
        self.tmTableWidget.setStyleSheet("color: white;")
        self.tmAddTaskBtn.clicked.connect(self.add_task)
        self.tmRemoveTaskBtn.clicked.connect(self.remove_task)
        self.tmCompleteTaskBtn.clicked.connect(self.complete_task)

        self.tmHideDoneCheckBox.setCheckState(QtCore.Qt.Checked)
        self.tmHideDoneCheckBox.clicked.connect(self.hide_done_tasks)

        self.tmRemoveTaskBtn.setStyleSheet("QPushButton {background-color: #872d2c;} QPushButton:hover {background-color: #1b81ca;}")
        self.tmCompleteTaskBtn.setStyleSheet("QPushButton {background-color: #98cd00;} QPushButton:hover {background-color: #1b81ca;}")

        self.tmFilterByProjectComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterBySequenceComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByShotComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByDeptComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByStatusComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByMemberComboBox.currentIndexChanged.connect(self.filter)
        self.tmBidOperationComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByBidComboBox.valueChanged.connect(self.filter)

        self.tmFilterByProjectComboBox.addItem("None")
        self.tmFilterByProjectComboBox.currentIndexChanged.connect(self.tm_load_sequences)

        self.tmFilterBySequenceComboBox.addItem("None")
        self.tmFilterBySequenceComboBox.currentIndexChanged.connect(self.tm_load_shots)

        self.tmFilterByShotComboBox.addItem("None")
        self.tmFilterByDeptComboBox.addItem("None")
        self.tmFilterByDeptComboBox.addItems(self.tm_departments.keys())
        self.tmFilterByStatusComboBox.addItem("None")
        self.tmFilterByStatusComboBox.addItems(self.status.keys())
        self.tmFilterByMemberComboBox.addItem("None")
        self.tmFilterByMemberComboBox.addItems(sorted(self.members.values()))

        # Add project to project filter combobox
        for project in self.projects:
            self.tmFilterByProjectComboBox.addItem(project)

        self.add_tasks_from_database()

    def add_tasks_from_database(self):

        for i in reversed(xrange(self.tmTableWidget.rowCount())):
            self.tmTableWidget.removeRow(i)


        all_tasks = self.cursor.execute('''SELECT * FROM tasks''').fetchall()

        self.widgets = {}

        inversed_index = len(all_tasks) - 1

        # Add existing tasks to task table
        for row_index, task in enumerate(reversed(all_tasks)):

            self.tmTableWidget.insertRow(0)

            # Adding tasks id
            task_id = task[0] #Ex: 1, 5, 8
            task_id_item = QtGui.QTableWidgetItem()
            task_id_item.setText(str(task_id))
            task_id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_id_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.tmTableWidget.setItem(0, 0, task_id_item)
            self.widgets[str(inversed_index) + ":0"] = task_id_item

            # Adding tasks description
            task_description = task[5] #Ex: Ajouter références pour le musée
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task_description)
            self.tmTableWidget.setItem(0, 1, task_description_item)
            self.widgets[str(inversed_index) + ":1"] = task_description_item

            # Adding department combo boxes
            task_department = task[6] #Ex: Compositing
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Script", "Storyboard", "References", "Concepts", "Modeling", "Texturing",
                            "Rigging", "Animation", "Simulation", "Shading", "Layout",
                            "DMP", "Compositing", "Editing", "RnD"])
            combo_box.setCurrentIndex(self.tm_departments[task_department])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 2, combo_box)
            self.widgets[str(inversed_index) + ":2"] = combo_box

            # Adding task status
            task_status = task[7] #Ex: En cours
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake", "Done"])
            combo_box.setCurrentIndex(self.status[task_status])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.change_cell_status_color(combo_box, task_status)
            self.tmTableWidget.setCellWidget(0, 3, combo_box)
            self.widgets[str(inversed_index) + ":3"] = combo_box

            # Adding assigned to
            task_assignation = task[8] #Ex: Amélie
            combo_box = QtGui.QComboBox()
            combo_box.addItems(
                [u"Amelie", u"Chloe", u"Christopher", u"David", u"Edwin", u"Etienne", u"Jeremy",
                 u"Laurence", u"Louis-Philippe", u"Marc-Antoine", u"Mathieu", u"Maxime", u"Olivier", u"Simon", u"Thibault",
                 u"Valentin", u"Yann", u"Yi"])
            combo_box.setCurrentIndex(self.members_id[task_assignation])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 4, combo_box)
            self.widgets[str(inversed_index) + ":4"] = combo_box

            # Adding task start
            task_date_start = task[9]
            date_start = QtCore.QDate.fromString(task_date_start, 'dd/MM/yyyy')
            date_start_edit = QtGui.QDateEdit()
            date_start_edit.setDate(date_start)
            date_start_edit.setDisplayFormat("dd/MM/yyyy")
            date_start_edit.setFrame(False)
            self.set_calendar(date_start_edit)
            self.tmTableWidget.setCellWidget(0, 5, date_start_edit)
            self.widgets[str(inversed_index) + ":5"] = date_start_edit

            # Adding task end
            task_date_end = task[10]
            date_end = QtCore.QDate.fromString(task_date_end, 'dd/MM/yyyy')
            date_end_edit = QtGui.QDateEdit()
            date_end_edit.setDate(date_end)
            date_end_edit.setDisplayFormat("dd/MM/yyyy")
            date_end_edit.setFrame(False)
            self.set_calendar(date_end_edit)
            self.tmTableWidget.setCellWidget(0, 6, date_end_edit)
            self.widgets[str(inversed_index) + ":6"] = date_end_edit

            # Adding days left
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tmTableWidget.setItem(0, 7, days_left_item)
            self.widgets[str(inversed_index) + ":7"] = days_left_item

            # Adding task bid
            task_bid = task[11]
            task_bid_item = QtGui.QSpinBox()
            task_bid_item.setValue(int(task_bid))
            task_bid_item.setAlignment(QtCore.Qt.AlignCenter)
            task_bid_item.setFrame(False)
            task_bid_item.setMaximum(500)
            task_bid_item.setMinimum(0)
            task_bid_item.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
            task_bid_item.valueChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 8, task_bid_item)
            self.widgets[str(inversed_index) + ":8"] = task_bid_item

            # Adding sequence name
            all_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''', (self.selected_project_name,)).fetchall()
            all_sequences = [str(i[0]) for i in all_sequences]
            all_sequences.insert(0, "xxx")
            task_sequence_name = task[2] #Ex: mus, cri, fru
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_sequences)
            index = combo_box.findText(task_sequence_name, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 9, combo_box)
            self.widgets[str(inversed_index) + ":9"] = combo_box

            # Adding shot number
            all_shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, task_sequence_name)).fetchall()
            all_shots = [str(i[0]) for i in all_shots]
            all_shots.insert(0, "xxxx")
            task_shot_number = task[3] #Ex: 0010, 0025, 0200
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_shots)
            index = combo_box.findText(task_shot_number, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 10, combo_box)
            self.widgets[str(inversed_index) + ":10"] = combo_box

            # Adding assets
            all_assets = self.cursor.execute('''SELECT asset_name FROM assets WHERE project_name=? AND sequence_name=? AND shot_number=?''', (self.selected_project_name, task_sequence_name, task_shot_number)).fetchall()
            all_assets = [str(i[0]) for i in all_assets]
            all_assets.insert(0, "xxxxx")
            task_asset_name = task[4] #Ex: lion, pierrePrecieuse
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_assets)
            index = combo_box.findText(task_asset_name, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 11, combo_box)
            self.widgets[str(inversed_index) + ":11"] = combo_box

            # If hide done checkbox is checked and current task is done, hide it
            if self.tmHideDoneCheckBox.isChecked():
                if task_status == "Done":
                    self.tmTableWidget.hideRow(0)

            inversed_index -= 1


        self.tmTableWidget.cellChanged.connect(self.update_tasks)
        self.tmTableWidget.resizeColumnsToContents()

        self.item_added = False

    def update_tasks(self, value):
        if self.item_added == True:
            return

        # Get which item was clicked and its value
        clicked_widget = self.sender()
        clicked_widget_value = value

        # Get index from clicked_widget position
        if type(clicked_widget) == QtGui.QTableWidget:
            widget_index = self.tmTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = clicked_widget_value
            widget_row_column = widget_index.column()
        else:
            widget_index = self.tmTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = widget_index.row()
            widget_row_column = widget_index.column()

        # Get widgets and their values from row index
        task_id_widget = self.widgets[str(widget_row_index) + ":0"]
        task_id = str(task_id_widget.text())

        task_description_widget = self.widgets[str(widget_row_index) + ":1"]
        task_description = unicode(task_description_widget.text())

        task_department_widget = self.widgets[str(widget_row_index) + ":2"]
        task_department = str(task_department_widget.currentText())

        task_status_widget = self.widgets[str(widget_row_index) + ":3"]
        task_status = str(task_status_widget.currentText())

        task_assignation_widget = self.widgets[str(widget_row_index) + ":4"]
        task_assignation = unicode(task_assignation_widget.currentText()).encode('UTF-8')
        # Get username from name (Ex: achaput from Amélie)
        for key, val in self.members.items():
            if task_assignation.decode('UTF-8') == val.decode('UTF-8'):
                task_assignation = key

        task_start_widget = self.widgets[str(widget_row_index) + ":5"]
        task_start = str(task_start_widget.date().toString("dd/MM/yyyy"))

        task_end_widget = self.widgets[str(widget_row_index) + ":6"]
        task_end = str(task_end_widget.date().toString("dd/MM/yyyy"))

        task_time_left_widget = self.widgets[str(widget_row_index) + ":7"]

        task_bid_widget = self.widgets[str(widget_row_index) + ":8"]
        task_bid = str(task_bid_widget.value())

        task_sequence_widget = self.widgets[str(widget_row_index) + ":9"]
        task_sequence = str(task_sequence_widget.currentText())

        task_shot_widget = self.widgets[str(widget_row_index) + ":10"]
        task_shot = str(task_shot_widget.currentText())

        task_asset_widget = self.widgets[str(widget_row_index) + ":11"]
        task_asset = str(task_asset_widget.currentText())

        # Sequence was changed -> Filter shots and assets from sequence and department
        if widget_row_column == 9 or widget_row_column == 2:
            # Get shots from current sequence
            shots_from_sequence = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, task_sequence,)).fetchall()
            shots_from_sequence = [str(i[0]) for i in shots_from_sequence]
            shots_from_sequence.insert(0, "xxxx")
            # Add shots to shots combo box
            shot_combobox = self.widgets[str(widget_row_index) + ":10"]
            shot_combobox.clear()
            shot_combobox.addItems(shots_from_sequence)

            # Get assets from current sequence and shot
            assets_from_sequence = self.cursor.execute('''SELECT asset_name FROM assets WHERE project_name=? AND sequence_name=? AND asset_type=?''', (self.selected_project_name, task_sequence, self.tm_departments_shortname[task_department],)).fetchall()
            assets_from_sequence = [str(i[0]) for i in assets_from_sequence]
            assets_from_sequence.insert(0, "xxxxx")
            # Add assets to asset combo box
            shot_combobox = self.widgets[str(widget_row_index) + ":11"]
            shot_combobox.clear()
            shot_combobox.addItems(assets_from_sequence)

        # Shot was changed -> Filter assets from sequence, shots and department
        elif widget_row_column == 10 or widget_row_column == 2:
            assets_from_shots = self.cursor.execute('''SELECT asset_name FROM assets WHERE project_name=? AND sequence_name=? AND shot_number=? AND asset_type=?''', (self.selected_project_name, task_sequence, task_shot, self.tm_departments_shortname[task_department])).fetchall()
            assets_from_shots = [str(i[0]) for i in assets_from_shots]
            assets_from_shots.insert(0, "xxxxx")
            shot_combobox = self.widgets[str(widget_row_index) + ":11"]
            shot_combobox.clear()
            shot_combobox.addItems(assets_from_shots)

        task_sequence_widget = self.widgets[str(widget_row_index) + ":9"]
        task_sequence = str(task_sequence_widget.currentText())

        task_shot_widget = self.widgets[str(widget_row_index) + ":10"]
        task_shot = str(task_shot_widget.currentText())

        task_asset_widget = self.widgets[str(widget_row_index) + ":11"]
        task_asset = str(task_asset_widget.currentText())

        self.cursor.execute(
            '''UPDATE tasks SET task_description=?, task_department=?, task_status=?, task_assignation=?, task_start=?, task_end=?, task_bid=?, sequence_name=?, shot_number=?, asset_name=? WHERE task_id=?''',
            (task_description, task_department, task_status, task_assignation, task_start, task_end, task_bid, task_sequence, task_shot, task_asset,
             task_id,))

        self.calculate_days_left(task_start_widget, task_end_widget, task_time_left_widget)
        self.change_cell_status_color(task_status_widget, task_status)

        self.db.commit()

    def add_task(self, item_added):

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            Lib.message_box(self, text="Please select a project first")
            return

        self.item_added = True

        number_of_rows_to_add = self.tmNbrOfRowsToAddSpinBox.value()

        for i in xrange(number_of_rows_to_add):
            self.cursor.execute(
                '''INSERT INTO tasks(project_name, sequence_name, shot_number, asset_name, task_description, task_department, task_status, task_assignation, task_start, task_end, task_bid) VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                (self.selected_project_name, "xxx", "xxxx", "xxxxx", "", "Script", "Ready to Start", u"achaput", self.today, self.today, "0"))

        self.db.commit()
        self.add_tasks_from_database()
        self.item_added = False

    def remove_task(self):

        selected_rows = self.tmTableWidget.selectedItems()
        for row in selected_rows:
            task_id_widget = self.widgets[str(row.row()) + ":0"]
            task_id = str(task_id_widget.text())
            self.cursor.execute('''DELETE FROM tasks WHERE task_id=?''', (task_id,))

        self.db.commit()

        self.item_added = True
        self.add_tasks_from_database()

    def complete_task(self):
        selected_rows = self.tmTableWidget.selectedItems()
        bid = 0
        for row in selected_rows:

            # Add bid value from each row
            cur_row_bid = self.widgets[str(row.row()) + ":8"]
            cur_row_bid = cur_row_bid.value()
            bid += cur_row_bid

            # Get task id for current row
            task_id_widget = self.widgets[str(row.row()) + ":0"]
            task_id = str(task_id_widget.text())
            self.cursor.execute('''UPDATE tasks SET task_status=? WHERE task_id=? ''', ("Done", task_id,))



        today_bid = self.cursor.execute('''SELECT bid_log_amount FROM bid_log WHERE bid_log_day=?''', (self.today,)).fetchone()

        # Check if an entry already exists for today. If yes, add the bid to the daily bid. If not, create an entry
        if today_bid:
            today_bid = int(today_bid[0])
            bid += today_bid
            self.cursor.execute('''UPDATE bid_log SET bid_log_amount=? WHERE project_name=? AND bid_log_day=?''', (bid, self.selected_project_name, self.today,))
        else:
            self.cursor.execute('''INSERT INTO bid_log(project_name, bid_log_day, bid_log_amount) VALUES(?,?,?)''', (self.selected_project_name, self.today, bid))


        self.db.commit()
        self.item_added = True
        self.add_tasks_from_database()

    def filter(self):

        number_of_rows = self.tmTableWidget.rowCount()
        for row_index in xrange(number_of_rows):
            # Retrieve text / value of filter widgets
            project_filter = str(self.tmFilterByProjectComboBox.currentText())
            sequence_filter = str(self.tmFilterBySequenceComboBox.currentText())
            shot_filter = str(self.tmFilterByShotComboBox.currentText())
            department_filter = self.tmFilterByDeptComboBox.currentText()
            status_filter = self.tmFilterByStatusComboBox.currentText()
            member_filter = self.tmFilterByMemberComboBox.currentText()
            bid_filter = self.tmFilterByBidComboBox.value()
            bid_operation = self.tmBidOperationComboBox.currentText()

            # Retrieve value of current row items
            task_id = str(self.tmTableWidget.item(row_index, 0).text())
            project = str(self.cursor.execute('''SELECT project_name FROM tasks WHERE task_id=?''', (task_id,)).fetchone()[0])
            sequence = str(self.tmTableWidget.cellWidget(row_index, 9).currentText())
            shot = str(self.tmTableWidget.cellWidget(row_index, 10).currentText())
            department = self.tmTableWidget.cellWidget(row_index, 2).currentText()
            status = self.tmTableWidget.cellWidget(row_index, 3).currentText()
            member = self.tmTableWidget.cellWidget(row_index, 4).currentText()
            bid = self.tmTableWidget.cellWidget(row_index, 8).value()

            # If filters are set to default value, set the filters variables to the current row values
            if project_filter == "None": project_filter = project
            if sequence_filter == "None": sequence_filter = sequence
            if shot_filter == "None": shot_filter = shot
            if department_filter == "None": department_filter = department
            if status_filter == "None" : status_filter = status
            if member_filter == "None" : member_filter = member
            if bid_filter == 0: bid_filter = bid

            if str(bid_operation) == ">=": bid_result = operator.le(bid_filter, bid)
            elif str(bid_operation) == "<=": bid_result = operator.ge(bid_filter, bid)

            if project_filter == project and sequence_filter == sequence and shot_filter == shot and department_filter == department and status_filter == status and member_filter == member and bid_result:
                self.tmTableWidget.showRow(row_index)
            else:
                self.tmTableWidget.hideRow(row_index)

    def calculate_days_left(self, task_start_widget, task_end_widget, task_time_left_widget):

        date_start = task_start_widget.date()
        date_end = task_end_widget.date()
        days_left = str(date_start.daysTo(date_end))
        task_time_left_widget.setText(days_left)

    def set_calendar(self, QDateEdit):
        calendar_widget = QtGui.QCalendarWidget()
        calendar_widget.showToday()
        calendar_widget.setStyleSheet("background-color: white;")
        QDateEdit.setCalendarPopup(True)
        QDateEdit.setCalendarWidget(calendar_widget)
        QDateEdit.dateChanged.connect(self.update_tasks)

    def change_cell_status_color(self, cell_item, task_status):

        if task_status == "Ready to Start":
            cell_item.setStyleSheet("background-color: #872d2c;")
        elif task_status == "In Progress":
            cell_item.setStyleSheet("background-color: #3292d5;")
        elif task_status == "On Hold":
            cell_item.setStyleSheet("background-color: #eb8a18;")
        elif task_status == "Waiting for Approval":
            cell_item.setStyleSheet("background-color: #eb8a18")
        elif task_status == "Retake":
            cell_item.setStyleSheet("background-color: #872d2c")
        elif task_status == "Done":
            cell_item.setStyleSheet("background-color: #4b4b4b;")

    def tm_load_sequences(self):
        current_project = str(self.tmFilterByProjectComboBox.currentText())
        if current_project == "None":
            return

        self.tm_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''', (current_project,)).fetchall()
        self.tm_sequences = [str(i[0]) for i in self.tm_sequences]

        self.tmFilterBySequenceComboBox.clear()
        self.tmFilterBySequenceComboBox.addItem("None")
        for seq in self.tm_sequences:
            self.tmFilterBySequenceComboBox.addItem(seq)

    def tm_load_shots(self):
        current_sequence = str(self.tmFilterBySequenceComboBox.currentText())
        if current_sequence == "None":
            return

        shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE sequence_name=?''', (current_sequence,)).fetchall()
        shots = [str(i[0]) for i in shots]

        self.tmFilterByShotComboBox.clear()
        self.tmFilterByShotComboBox.addItem("None")
        for shot in shots:
            self.tmFilterByShotComboBox.addItem(shot)

    def hide_done_tasks(self):
        number_of_rows = self.tmTableWidget.rowCount()
        for row_index in xrange(number_of_rows):

            if self.tmHideDoneCheckBox.isChecked():
                status = self.tmTableWidget.cellWidget(row_index, 3).currentText()
                if status == "Done":
                    self.tmTableWidget.hideRow(row_index)
                else:
                    self.tmTableWidget.showRow(row_index)
            else:
                self.tmTableWidget.showRow(row_index)

