#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import operator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pyperclip as clipboard
from operator import itemgetter


from random import randint

class TaskManager(object):

    def __init__(self):

        self.tm_departments = {"Misc": 0, "Script": 1, "Storyboard": 2, "References": 3, "Concepts": 4, "Modeling": 5, "Texturing": 6,
                               "Rigging": 7, "Animation": 8, "Simulation": 9, "Shading": 10, "Camera": 11, "Lighting": 12, "Layout": 13,
                               "DMP": 14, "Compositing": 15, "Editing": 16, "RnD": 17}

        self.tm_departments_shortname = {"Script": "spt", "Storyboard": "stb", "References": "ref", "Concepts": "cpt",
                                         "Modeling": "mod", "Texturing": "tex", "Rigging": "rig", "Animation": "anm",
                                         "Simulation": "sim", "Shading": "shd", "Layout": "lay", "DMP": "dmp",
                                         "Compositing": "cmp", "Editing": "edt", "RnD": "rnd"}

        self.status = {"Ready to Start": 0, "In Progress": 1, "On Hold": 2, "Waiting for Approval": 3, "Retake": 4,
                       "Done": 5}

        self.task_priority_dic = {"High": 0, "Default": 1, "Low": 2}

        self.members_id = {"costiguy": 0, "cgonnord": 1, "erodrigue": 2, "jberger": 3, "lgregoire": 4,
                           "lclavet": 5, "mbeaudoin": 6,
                           "mroz": 7, "obolduc": 8, "slachapelle": 9, "thoudon": 10,
                           "vdelbroucq": 11, "yjobin": 12, "yshan": 13, "acorbin": 14, "fpasquarelli":15}

        # The itemChanged signal connection of the QTableWidget is fired every time
        # an item changes on the tablewidget. Therefore whenever we're adding an entry to the tablewidget, the itemChanged
        # slot is fired. The item_added variable is used to know when the user adds a row and when a user update a row
        # if item_added is set to true, then the user is simply adding a row and not updating it.
        # Therefore, the update_task function is disabled when the item_added variable is set to true.

        self.item_added = False
        self.tmTableWidget.setStyleSheet("color: black;")
        self.tmTableWidget.itemDoubleClicked.connect(self.tmTableWidget_DoubleClicked)
        self.tmAddTaskBtn.clicked.connect(self.add_task)
        self.tmRemoveTaskBtn.clicked.connect(self.remove_task)
        self.tmCompleteTaskBtn.clicked.connect(self.complete_task)
        self.tmShowBidCurveBtn.clicked.connect(self.show_bid_curve)


        self.tmHideDoneCheckBox.setCheckState(QtCore.Qt.Checked)
        self.tmHideDoneCheckBox.clicked.connect(self.filter)
        self.tmHideConfirmedCheckBox.clicked.connect(self.filter)

        self.tmFilterBySequenceComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByShotComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByDeptComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByStatusComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByMemberComboBox.currentIndexChanged.connect(self.filter)
        self.tmBidOperationComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByDaysLeftComboBox.valueChanged.connect(self.filter)
        self.tmDaysLeftOperationComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByBidComboBox.valueChanged.connect(self.filter)

        self.tmFilterBySequenceComboBox.addItem("None")
        self.tmFilterBySequenceComboBox.currentIndexChanged.connect(self.tm_load_shots)

        self.tmFilterByShotComboBox.addItem("None")
        self.tmFilterByDeptComboBox.addItem("None")
        self.tmFilterByDeptComboBox.addItems(self.tm_departments.keys())
        self.tmFilterByStatusComboBox.addItem("None")
        self.tmFilterByStatusComboBox.addItems(self.status.keys())
        self.tmFilterByMemberComboBox.addItem("None")
        self.tmFilterByMemberComboBox.addItems(sorted(self.members.values()))

        self.tmCopyDaysBtn.clicked.connect(self.copy_days)
        self.tmCopyBidTimesBtn.clicked.connect(self.copy_bid_times)

        self.tm_load_sequences()

        self.tmShowBidPerUserBtn.clicked.connect(self.show_bid_per_user)

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

            id = task[0]
            project_name = task[1]
            sequence_name = task[2]
            shot_number = task[3]
            asset_id = task[4]
            description = task[5]
            department = task[6]
            status = task[7]
            assignation = task[8]
            end = task[9]
            bid = task[10]
            confirmation = task[11]
            priority = task[12]
            if id == None: id = ""
            if project_name == None: project_name = ""
            if sequence_name == None: sequence_name = ""
            if shot_number == None: shot_number = ""
            if asset_id == None: asset_id = ""
            if description == None: description = ""
            if department == None: department = ""
            if status == None: status = ""
            if assignation == None: assignation = ""
            if end == None: end = ""
            if bid == None: bid = ""
            if confirmation == None: confirmation = ""
            if priority == None: priority = ""

            task = self.Task(self, id, project_name, sequence_name, shot_number, asset_id, description, department, status, assignation, end, bid, confirmation, priority)

            # Adding tasks id
            number_of_comments = self.cursor.execute('''SELECT asset_id FROM comments WHERE comment_type="task" AND asset_id=?''', (task.id,)).fetchall()
            task_id_item = QtGui.QTableWidgetItem()
            task_id_item.setData(QtCore.Qt.UserRole, task)
            task_id_item.setText(str(task.id))
            task_id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_id_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            if task.confirmation == "0":
                if len(number_of_comments) > 0:
                    task_id_item.setBackground(QtGui.QColor(226, 79, 77))
                else:
                    task_id_item.setBackground(QtGui.QColor(135, 45, 44))
            else:
                if len(number_of_comments) > 0:
                    task_id_item.setBackground(QtGui.QColor(189, 255, 0))
                else:
                    task_id_item.setBackground(QtGui.QColor(152, 205, 0))
            self.tmTableWidget.setItem(0, 0, task_id_item)
            self.widgets[str(inversed_index) + ":0"] = task_id_item

            # Adding tasks description
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task.description)
            self.tmTableWidget.setItem(0, 1, task_description_item)
            self.widgets[str(inversed_index) + ":1"] = task_description_item

            # Adding department combo boxes
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Misc", "Script", "Storyboard", "References", "Concepts", "Modeling", "Texturing",
                            "Rigging", "Animation", "Simulation", "Shading", "Camera", "Lighting", "Layout",
                            "DMP", "Compositing", "Editing", "RnD"])
            combo_box.setCurrentIndex(self.tm_departments[task.department])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 2, combo_box)
            self.widgets[str(inversed_index) + ":2"] = combo_box

            # Adding task status
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake", "Done"])
            combo_box.setCurrentIndex(self.status[task.status])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.change_cell_status_color(combo_box, task.status)
            self.tmTableWidget.setCellWidget(0, 3, combo_box)
            self.widgets[str(inversed_index) + ":3"] = combo_box

            # Adding assigned to
            combo_box = QtGui.QComboBox()
            combo_box.addItems(
                [u"Chloe", u"Christopher", u"Etienne", u"Jeremy",
                 u"Laurence", u"Louis-Philippe", u"Mathieu", u"Maxime", u"Olivier", u"Simon", u"Thibault",
                 u"Valentin", u"Yann", u"Yi"])
            combo_box.setCurrentIndex(self.members_id[task.assignation])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 4, combo_box)
            self.widgets[str(inversed_index) + ":4"] = combo_box

            # Adding task end
            date_end = QtCore.QDate.fromString(task.end, 'dd/MM/yyyy')
            date_end_edit = QtGui.QDateEdit()
            date_end_edit.setDate(date_end)
            date_end_edit.setDisplayFormat("dd/MM/yyyy")
            date_end_edit.setFrame(False)
            self.set_calendar(date_end_edit)
            self.tmTableWidget.setCellWidget(0, 5, date_end_edit)
            self.widgets[str(inversed_index) + ":5"] = date_end_edit

            # Adding days left
            date_start = QtCore.QDate.currentDate()
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tmTableWidget.setItem(0, 6, days_left_item)
            self.widgets[str(inversed_index) + ":6"] = days_left_item

            # Adding task bid
            task_bid_item = QtGui.QSpinBox()
            task_bid_item.setValue(int(task.bid))
            task_bid_item.setAlignment(QtCore.Qt.AlignCenter)
            task_bid_item.setFrame(False)
            task_bid_item.setMaximum(500)
            task_bid_item.setMinimum(0)
            task_bid_item.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
            task_bid_item.valueChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 7, task_bid_item)
            self.widgets[str(inversed_index) + ":7"] = task_bid_item

            # Adding sequence name
            all_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''', (task.project,)).fetchall()
            all_sequences = [str(i[0]) for i in all_sequences]
            all_sequences.insert(0, "xxx")
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_sequences)
            index = combo_box.findText(task.sequence, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 8, combo_box)
            self.widgets[str(inversed_index) + ":8"] = combo_box

            # Adding shot number
            all_shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (task.project, task.sequence)).fetchall()
            all_shots = [str(i[0]) for i in all_shots]
            all_shots.insert(0, "xxxx")
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_shots)
            index = combo_box.findText(task.shot, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 9, combo_box)
            self.widgets[str(inversed_index) + ":9"] = combo_box

            # Adding assets
            line_edit = QtGui.QLineEdit()
            line_edit.setText(str(task.asset_id))
            line_edit.textChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 10, line_edit)
            self.widgets[str(inversed_index) + ":10"] = line_edit

            # Add confirm task button
            if task.confirmation == "0":
                confirm_button = QtGui.QPushButton("Confirm")
            else:
                confirm_button = QtGui.QPushButton("UnConfirm")
            confirm_button.clicked.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 11, confirm_button)
            self.widgets[str(inversed_index) + ":11"] = confirm_button

            # Add remind task button
            remind_button = QtGui.QPushButton("Remind")
            remind_button.clicked.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 12, remind_button)
            self.widgets[str(inversed_index) + ":12"] = remind_button

            # Add priority
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["High", "Default", "Low"])
            combo_box.setCurrentIndex(self.task_priority_dic[task.priority])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.change_cell_status_color(combo_box, task.priority)
            self.tmTableWidget.setCellWidget(0, 13, combo_box)
            self.widgets[str(inversed_index) + ":13"] = combo_box

            # If hide done checkbox is checked and current task is done, hide it
            if self.tmHideDoneCheckBox.isChecked():
                if task.status == "Done":
                    self.tmTableWidget.hideRow(0)

            inversed_index -= 1


        self.tmTableWidget.cellChanged.connect(self.update_tasks)
        self.tmTableWidget.resizeColumnsToContents()
        self.tmTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

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

        task_end_widget = self.widgets[str(widget_row_index) + ":5"]
        task_end = str(task_end_widget.date().toString("dd/MM/yyyy"))

        task_time_left_widget = self.widgets[str(widget_row_index) + ":6"]

        task_bid_widget = self.widgets[str(widget_row_index) + ":7"]
        task_bid = str(task_bid_widget.value())

        task_sequence_widget = self.widgets[str(widget_row_index) + ":8"]
        task_sequence = str(task_sequence_widget.currentText())

        task_shot_widget = self.widgets[str(widget_row_index) + ":9"]
        task_shot = str(task_shot_widget.currentText())

        task_asset_widget = self.widgets[str(widget_row_index) + ":10"]
        task_asset_name = str(task_asset_widget.text())
        task = self.Task(self, task_id)
        task.get_infos_from_id()

        # If clicked widget is column 11, then confirm/unconfirm task
        if widget_row_column == 11:
            if task.confirmation == "0":
                clicked_widget.setText("UnConfirm")
                task_id_widget.setBackground(QtGui.QColor(152, 205, 0))
                task.change_confirmation(1)

                # Add Log Entry
                log_entry = self.LogEntry(self, 0, task.id, [], [task.assignation], self.username, task.assignation, "task", u"{0} has assigned a new {1} task to {2}: {3}".format(self.members[self.username], task.department, self.members[task.assignation], task.description), datetime.datetime.now().strftime("%d/%m/%Y at %H:%M"))
                log_entry.add_log_to_database()

                email = self.cursor.execute('''SELECT email FROM preferences WHERE username=?''', (task.assignation,)).fetchone()[0]

                subject = QtCore.QString("A new task has been assigned to you")
                subject = unicode(self.utf8_codec.fromUnicode(subject), 'utf-8')

                message = QtCore.QString(u"{0} has assigned a new {1} task to {2}: {3} (You have {4} days left to complete it)".format(self.members[self.username], task.department, self.members[task.assignation], task.description, task_time_left_widget.text()))
                message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8')

                self.Lib.send_email(self, from_addr="nad.update@gmail.com", addr_list=[email], subject=subject, message=message, username=self.members[self.username])

            else:
                clicked_widget.setText("Confirm")
                task_id_widget.setBackground(QtGui.QColor(135, 45, 44))
                task.change_confirmation(0)
                # Delete Log Entry
                self.cursor.execute('''DELETE FROM log WHERE log_dependancy=? AND log_type="task"''', (task.id,))
                self.db.commit()
            self.tmTableWidget.resizeColumnsToContents()
            self.tmTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)


            return

        elif widget_row_column == 12:
            email = self.cursor.execute('''SELECT email FROM preferences WHERE username=?''', (task.assignation,)).fetchone()[0]

            subject = QtCore.QString("Task Reminder")
            subject = unicode(self.utf8_codec.fromUnicode(subject), 'utf-8')

            message = QtCore.QString(u"This is a reminder to let you know that you have a pending {0} task: {1} (You have {2} days left to complete it)".format(task.department, task.description, task_time_left_widget.text()))
            message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8')

            self.Lib.send_email(self, from_addr="nad.update@gmail.com", addr_list=[email], subject=subject, message=message, username=self.members[self.username])

        if task_description != task.description: task.change_description(task_description)
        if task_department != task.department: task.change_department(task_department)
        if task_status != task.status: task.change_status(task_status)
        if task_assignation != task.assignation: task.change_assignation(task_assignation)
        if task_end != task.end: task.change_end(task_end)
        if task_bid != task.bid: task.change_bid(task_bid)

        # Sequence was changed -> Filter shots and assets from sequence and department
        if widget_row_column == 8:
            # Get shots from current sequence
            shots_from_sequence = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, task_sequence,)).fetchall()
            shots_from_sequence = [str(i[0]) for i in shots_from_sequence]
            shots_from_sequence.insert(0, "xxxx")
            # Add shots to shots combo box
            shot_combobox = self.widgets[str(widget_row_index) + ":9"]
            shot_combobox.clear()
            shot_combobox.addItems(shots_from_sequence)


        task_sequence_widget = self.widgets[str(widget_row_index) + ":8"]
        task_sequence = str(task_sequence_widget.currentText())

        task_shot_widget = self.widgets[str(widget_row_index) + ":9"]
        task_shot = str(task_shot_widget.currentText())

        task_asset_widget = self.widgets[str(widget_row_index) + ":10"]
        task_asset_id = str(task_asset_widget.text())

        if task_sequence != task.sequence: task.change_sequence(task_sequence)
        if task_shot != task.shot: task.change_shot(task_shot)
        if task_asset_id != task.asset_id: task.change_asset_id(task_asset_id)

        task_priority_widget = self.widgets[str(widget_row_index) + ":13"]
        task_priority = str(task_priority_widget.currentText())
        if task_priority != task.priority: task.change_priority(task_priority)

        self.calculate_days_left(task_end_widget, task_time_left_widget)
        self.change_cell_status_color(task_status_widget, task.status)
        self.change_cell_status_color(task_priority_widget, task.priority)

    def add_task(self, item_added=None, asset_id=0):
        # Check if a project is selected
        if len(self.projectList.currentText()) == 0:
            self.Lib.message_box(self, text="Please select a project first")
            return

        self.item_added = True

        number_of_rows_to_add = self.tmNbrOfRowsToAddSpinBox.value()

        for i in xrange(number_of_rows_to_add):
            task = self.Task(self, 0, self.selected_project_name, "xxx", "xxxx", asset_id, "", "Script", "Ready to Start", u"costiguy", self.today, "0", "0", "Default")
            task.add_task_to_db()

        self.add_tasks_from_database()
        self.item_added = False

    def remove_task(self):
        selected_rows = self.tmTableWidget.selectedItems()
        for row in selected_rows:
            task_id_widget = self.widgets[str(row.row()) + ":0"]
            task_id = str(task_id_widget.text())
            task = self.Task(self, task_id)
            task.get_infos_from_id()
            task.remove_task_from_db()
            self.Lib.remove_log_entry_from_asset_id(self, task_id)

        self.item_added = True
        self.add_tasks_from_database()

    def complete_task(self):
        selected_rows = self.tmTableWidget.selectedItems()
        bid = 0
        for row in selected_rows:

            # Add bid value from each row
            cur_row_bid = self.widgets[str(row.row()) + ":7"]
            cur_row_bid = cur_row_bid.value()
            bid += cur_row_bid

            # Get task id for current row
            task_id_widget = self.widgets[str(row.row()) + ":0"]
            task_id = str(task_id_widget.text())
            task = self.Task(self, task_id)
            task.get_infos_from_id()
            task.change_confirmation(0)
            task.change_status("Done")


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
            sequence_filter = str(self.tmFilterBySequenceComboBox.currentText())
            shot_filter = str(self.tmFilterByShotComboBox.currentText())
            department_filter = self.tmFilterByDeptComboBox.currentText()
            status_filter = self.tmFilterByStatusComboBox.currentText()
            member_filter = self.tmFilterByMemberComboBox.currentText()
            daysleft_filter = self.tmFilterByDaysLeftComboBox.value()
            daysleft_operation = self.tmDaysLeftOperationComboBox.currentText()
            bid_filter = self.tmFilterByBidComboBox.value()
            bid_operation = self.tmBidOperationComboBox.currentText()

            task_id = str(self.tmTableWidget.item(row_index, 0).text())
            task = self.Task(self, task_id)
            task.get_infos_from_id()

            # If filters are set to default value, set the filters variables to the current row values
            if sequence_filter == "None": sequence_filter = task.sequence
            if shot_filter == "None": shot_filter = task.shot
            if department_filter == "None": department_filter = task.department
            if status_filter == "None" : status_filter = task.status
            if member_filter == "None" : member_filter = self.members[task.assignation]
            if bid_filter == 0: bid_filter = task.bid
            days_left = QtCore.QDate.currentDate().daysTo(QtCore.QDate.fromString(task.end, "dd/MM/yyyy"))
            if daysleft_filter == 0:
                daysleft_filter = days_left

            if str(bid_operation) == ">=": bid_result = operator.le(int(bid_filter), int(task.bid))
            elif str(bid_operation) == "<=": bid_result = operator.ge(int(bid_filter), int(task.bid))

            if str(daysleft_operation) == ">=": days_left_result = operator.le(int(daysleft_filter), int(days_left))
            elif str(daysleft_operation) == "<=": days_left_result = operator.ge(int(daysleft_filter), int(days_left))

            if sequence_filter == task.sequence and shot_filter == task.shot and department_filter == task.department and status_filter == task.status and member_filter == self.members[task.assignation] and bid_result and days_left_result:
                # Check each row for "Done" and "Confirmed"
                if self.tmHideDoneCheckBox.isChecked() and self.tmHideConfirmedCheckBox.isChecked():
                    if task.status == "Done":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    if task.confirmation == "1":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    self.tmTableWidget.showRow(row_index)
                # Check each row for "Done" only
                elif self.tmHideDoneCheckBox.isChecked() and not self.tmHideConfirmedCheckBox.isChecked():
                    if task.status == "Done":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    self.tmTableWidget.showRow(row_index)
                # Check each row for "Confirmed" only
                elif not self.tmHideDoneCheckBox.isChecked() and self.tmHideConfirmedCheckBox.isChecked():
                    if task.confirmation == "1":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    self.tmTableWidget.showRow(row_index)
                else:
                    self.tmTableWidget.showRow(row_index)
            else:
                self.tmTableWidget.hideRow(row_index)

        self.tmTableWidget.resizeColumnsToContents()
        self.tmTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

    def tmTableWidget_DoubleClicked(self, value):
        row = value.row()
        column = value.column()

        task_item = self.tmTableWidget.item(row, column)
        self.selected_asset = task_item.data(QtCore.Qt.UserRole).toPyObject()
        if self.selected_asset == None: return # User clicked on the days left cell

        self.commentLineEdit.setFocus()
        self.CommentWidget.load_comments(self)

    def calculate_days_left(self, task_end_widget, task_time_left_widget):

        date_start = QtCore.QDate.currentDate()
        date_end = task_end_widget.date()
        days_left = str(date_start.daysTo(date_end))
        task_time_left_widget.setText(days_left)

    def set_calendar(self, QDateEdit):
        calendar_widget = QtGui.QCalendarWidget()
        calendar_widget.showToday()
        #calendar_widget.setStyleSheet("background-color: white;")
        QDateEdit.setCalendarPopup(True)
        QDateEdit.setCalendarWidget(calendar_widget)
        QDateEdit.dateChanged.connect(self.update_tasks)

    def change_cell_status_color(self, cell_item, task_status):
        task_status = str(task_status)

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
        elif task_status == "High":
            cell_item.setStyleSheet("background-color: #d84848;")
        elif task_status == "Default":
            cell_item.setStyleSheet("background-color: #e8c14c;")
        elif task_status == "Low":
            cell_item.setStyleSheet("background-color: #4296d7;")

    def tm_load_sequences(self):
        current_project = str(self.projectList.currentText())
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

    def show_bid_curve(self):

        d1 = datetime.datetime(2015,07,11)
        d2 = datetime.datetime.now()
        total_days = (d2-d1).days

        bid_log_days = self.cursor.execute('''SELECT bid_log_day FROM bid_log WHERE project_name=? LIMIT ?''', (self.selected_project_name, total_days,)).fetchall()
        bid_log_amounts = self.cursor.execute('''SELECT bid_log_amount FROM bid_log WHERE project_name=? LIMIT ?''', (self.selected_project_name, total_days,)).fetchall()
        bid_log_days = [str(i[0]) for i in bid_log_days]
        bid_log_days = [datetime.datetime.strptime(d,'%d/%m/%Y').date() for d in bid_log_days]
        bid_log_amounts = [int(str(i[0])) for i in bid_log_amounts]

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.ylabel('Number of bidded hours')
        plt.xlabel('Date')
        plt.plot(bid_log_days, bid_log_amounts)
        plt.gcf().autofmt_xdate()
        plt.show()

    def copy_days(self):
        d1 = datetime.datetime(2015,07,11)
        d2 = datetime.datetime.now()
        total_days = (d2-d1).days

        bid_log_days = self.cursor.execute('''SELECT bid_log_day FROM bid_log WHERE project_name=? LIMIT ?''', (self.selected_project_name, total_days,)).fetchall()
        bid_log_days = [i[0] for i in bid_log_days]
        bid_log_days = "\n".join(bid_log_days)

        clipboard.copy(bid_log_days)

    def copy_bid_times(self):
        d1 = datetime.datetime(2015, 07, 11)
        d2 = datetime.datetime.now()
        total_days = (d2 - d1).days

        bid_log_amounts = self.cursor.execute('''SELECT bid_log_amount FROM bid_log WHERE project_name=? LIMIT ?''', (self.selected_project_name, total_days,)).fetchall()
        bid_log_amounts = [i[0] for i in bid_log_amounts]
        bid_log_amounts = "\n".join(bid_log_amounts)

        clipboard.copy(bid_log_amounts)

    def show_bid_per_user(self):
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Bid per User")
        self.Lib.apply_style(self, dialog)
        dialog.setMinimumWidth(150)
        layout = QtGui.QGridLayout(dialog)

        total_bids = []

        for i, member in enumerate(self.members_id.keys()):
            total_user_bid = self.cursor.execute('''SELECT sum(task_bid) FROM tasks WHERE task_assignation=? AND task_status!="Done"''', (member,)).fetchone()[0]
            if total_user_bid == None:
                total_user_bid = 0
            total_bids.append((self.members[member], total_user_bid))

        total_bids = sorted(total_bids, key=itemgetter(1), reverse=True)

        for i, item in enumerate(total_bids):
            user_label = QtGui.QLabel(dialog)
            user_label.setText(item[0] + ":")
            total_user_bid_label = QtGui.QLabel(dialog)
            total_user_bid_label.setText(str(item[1]))
            layout.addWidget(user_label, i, 0)
            layout.addWidget(total_user_bid_label, i, 1)

        dialog.exec_()




