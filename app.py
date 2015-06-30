#!/usr/bin/env python
# coding=utf-8
''' 

Author: Thibault Houdon
Email: houdon.thibault@gmail.com


    Files/Folders Structure:

- lib folder contains utilities scripts:
    QtUiConverter to convert .ui file contained in media folder to main_window.py file in ui folder.
    make_exe to create an executable files to launch the application (inside the dist folder).
- media folder which contains all images, the .ui file and the css files.
- ui folder which contains all python scripts which generates GUIs.

The setup.py file is used by py2exe to create the executable file (it is run from the make_exe file which is inside the lib folder).
The _Asset Manager shortcut is pointing toward the app.exe file inside the lib/dist folder
The app.py file is the main python file


'''

import sys
import os
import subprocess
from functools import partial
import sqlite3
import time
from thibh import screenshot
import urllib
import shutil

from PyQt4 import QtGui, QtCore, Qt
from ui.main_window import Ui_Form


class Main(QtGui.QWidget, Ui_Form):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_Form.__init__(self)

        self.Form = self.setupUi(self)
        self.Form.center_window()

        # Global Variables
        self.cur_path = os.path.dirname(os.path.realpath(__file__))  # H:\01-NAD\_pipeline\_utilities\_asset_manager
        self.cur_path_one_folder_up = self.cur_path.replace("\\_asset_manager", "")  # H:\01-NAD\_pipeline\_utilities
        self.screenshot_dir = self.cur_path_one_folder_up + "\\_database\\screenshots\\"
        self.username = os.getenv('USERNAME')
        self.members = {"achaput": "Amélie", "costiguy": "Chloé", "cgonnord": "Christopher", "dcayerdesforges": "David",
                        "earismendez": "Edwin", "erodrigue": "Étienne", "jberger": "Jérémy", "lgregoire": "Laurence",
                        "lclavet": "Louis-Philippe", "mchretien": "Marc-Antoine", "mbeaudoin": "Mathieu",
                        "mroz": "Maxime", "obolduc": "Olivier", "slachapelle": "Simon", "thoudon": "Thibault",
                        "yjobin": "Yann", "yshan": "Yi", "vdelbroucq": "Valentin"}
        pixmap = QtGui.QPixmap(self.screenshot_dir + "default\\no_img.png").scaled(1000, 200, QtCore.Qt.KeepAspectRatio,
                                                                                   QtCore.Qt.SmoothTransformation)
        self.assetImg.setPixmap(pixmap)


        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile(self.cur_path + "\\media\\favicon.png",
                         QtCore.QSize(16, 16))
        self.Form.setWindowIcon(app_icon)


        # Set the StyleSheet
        css = QtCore.QFile(self.cur_path + "\\media\\style.css")
        css.open(QtCore.QIODevice.ReadOnly)
        if css.isOpen():
            self.Form.setStyleSheet(QtCore.QVariant(css.readAll()).toString())


        # Overrides
        self.publishBtn.setStyleSheet("background-color: #77D482;")
        self.loadBtn.setStyleSheet(
            "QPushButton {background-color: #77B0D4;} QPushButton:hover {background-color: #1BCAA7;}")
        self.assetDependencyList.setEnabled(False)
        self.webGroupBox.setDisabled(True)

        # Admin Setup
        if not self.username == "thoudon" or self.username == "lclavet":
            self.addProjectFrame.hide()
            self.addSequenceFrame.hide()
            self.addShotFrame.hide()





        # Database Setup
        self.db_path = self.cur_path_one_folder_up + "\\_database\\db.sqlite"
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        # Get projects from database and add them to the projects list
        projects = self.cursor.execute('''SELECT * FROM projects''')
        for project in projects:
            self.projectList.addItem(project[1])

        # Get software paths from database and put them in preference
        self.photoshop_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Photoshop"''').fetchone()[0])
        self.maya_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Maya"''').fetchone()[
                0])
        self.softimage_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Softimage"''').fetchone()[0])
        self.houdini_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Houdini"''').fetchone()[0])
        self.cinema4d_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Cinema 4D"''').fetchone()[0])
        self.nuke_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Nuke"''').fetchone()[
                0])
        self.zbrush_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="ZBrush"''').fetchone()[
                0])
        self.mari_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Mari"''').fetchone()[
                0])
        self.blender_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Blender"''').fetchone()[0])

        self.photoshopPathLineEdit.setText(self.photoshop_path)
        self.mayaPathLineEdit.setText(self.maya_path)
        self.softimagePathLineEdit.setText(self.softimage_path)
        self.houdiniPathLineEdit.setText(self.houdini_path)
        self.cinema4dPathLineEdit.setText(self.cinema4d_path)
        self.nukePathLineEdit.setText(self.nuke_path)
        self.zbrushPathLineEdit.setText(self.zbrush_path)
        self.mariPathLineEdit.setText(self.mari_path)
        self.blenderPathLineEdit.setText(self.blender_path)

        # Connect the filter textboxes
        self.seqFilter.textChanged.connect(partial(self.filterList_textChanged, "sequence"))
        self.assetFilter.textChanged.connect(partial(self.filterList_textChanged, "asset"))

        # Connect the lists
        self.projectList.itemClicked.connect(self.projectList_Clicked)
        self.projectList.itemDoubleClicked.connect(self.projectList_DoubleClicked)
        self.departmentList.itemClicked.connect(self.departmentList_Clicked)
        self.seqList.itemClicked.connect(self.seqList_Clicked)
        self.assetList.itemClicked.connect(self.assetList_Clicked)
        self.departmentCreationList.itemClicked.connect(self.departmentCreationList_Clicked)


        # Connect the buttons
        self.addProjectBtn.clicked.connect(self.add_project)
        self.addSequenceBtn.clicked.connect(self.add_sequence)
        self.addShotBtn.clicked.connect(self.add_shot)

        self.seqFilterClearBtn.clicked.connect(partial(self.clear_filter, "seq"))
        self.assetFilterClearBtn.clicked.connect(partial(self.clear_filter, "asset"))
        self.loadBtn.clicked.connect(self.load_asset)
        self.openInExplorerBtn.clicked.connect(self.open_in_explorer)
        self.addCommentBtn.clicked.connect(self.add_comment)
        self.updateThumbBtn.clicked.connect(self.update_thumb)

        self.savePrefBtn.clicked.connect(self.save_prefs)
        self.createAssetBtn.clicked.connect(self.create_asset)


    def add_project(self):
        if not str(self.addProjectLineEdit.text()):
            self.message_box(text="Please enter a project name")
            return

        project_name = str(self.addProjectLineEdit.text())

        selected_folder = str(QtGui.QFileDialog.getExistingDirectory())

        # Prevent two projects from having the same name
        all_projects_name = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        all_projects_name = [i[0] for i in all_projects_name]
        if project_name in all_projects_name:
            self.message_box(text="Project name is already taken.")
            return

        # Create project's folder
        project_path = selected_folder + "\\" + project_name
        os.makedirs(project_path + "\\assets")
        os.makedirs(project_path + "\\assets\\spt")
        os.makedirs(project_path + "\\assets\\stb")
        os.makedirs(project_path + "\\assets\\ref")
        os.makedirs(project_path + "\\assets\\cpt")
        os.makedirs(project_path + "\\assets\\mod")
        os.makedirs(project_path + "\\assets\\tex")
        os.makedirs(project_path + "\\assets\\rig")
        os.makedirs(project_path + "\\assets\\anm")
        os.makedirs(project_path + "\\assets\\sim")
        os.makedirs(project_path + "\\assets\\shd")
        os.makedirs(project_path + "\\assets\\lay")
        os.makedirs(project_path + "\\assets\\dmp")
        os.makedirs(project_path + "\\assets\\cmp")
        os.makedirs(project_path + "\\assets\\edt")
        os.makedirs(project_path + "\\assets\\rnd")

        # Add project to database
        self.cursor.execute('''INSERT INTO projects(project_name, project_path) VALUES (?, ?)''',
                            (project_name, project_path))
        self.db.commit()

        # Get projects from database and add them to the projects list
        self.projectList.clear()
        projects = self.cursor.execute('''SELECT * FROM projects''')
        for project in projects:
            self.projectList.addItem(project[1])

    def add_sequence(self):

        """Add specified sequence to the selected project
        """

        sequence_name = str(self.addSequenceLineEdit.text())

        # Check if user entered a 3 letter sequence name
        if len(sequence_name) == 0:
            self.message_box(text="Please enter a sequence name")
            return
        elif len(sequence_name) < 3:
            self.message_box(text="Please enter a 3 letters name")
            return

        # Check if a project is selected
        if not self.projectList.selectedItems():
            self.message_box(text="Please select a project first")
            return

        # Prevent two sequences from having the same name
        all_sequences_name = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''',
                                                 (self.selected_project_name,)).fetchall()
        all_sequences_name = [i[0] for i in all_sequences_name]
        if sequence_name in all_sequences_name:
            self.message_box(text="Sequence name is already taken.")
            return

        # Add sequence to database
        self.cursor.execute('''INSERT INTO sequences(project_name, sequence_name) VALUES (?, ?)''',
                            (self.selected_project_name, sequence_name))

        self.db.commit()

        # Add sequence to GUI
        self.seqList.addItem(sequence_name)
        self.seqList_Clicked()

    def add_shot(self):

        shot_number = str(self.shotSpinBox.text()).zfill(4)

        # Check if a project and a sequence are selected
        if not (self.projectList.selectedItems() and self.seqList.selectedItems()):
            self.message_box(text="Please select a project and a sequence first.")
            return

        # Prevent two shots from having the same number
        all_shots_number = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                               (self.selected_project_name, self.selected_sequence_name)).fetchall()
        all_shots_number = [i[0] for i in all_shots_number]
        if shot_number in all_shots_number:
            self.message_box(text="Shot number already exists.")
            return

        # Add shot to database
        self.cursor.execute('''INSERT INTO shots(project_name, sequence_name, shot_number) VALUES (?, ?, ?)''',
                            (self.selected_project_name, self.selected_sequence_name, shot_number))

        self.db.commit()

        # Add shot to GUI
        self.shotList.addItem(shot_number)
        self.seqList_Clicked()

    def filterList_textChanged(self, list_type):

        if list_type == "sequence":
            seq_filter_str = str(self.seqFilter.text())
            if seq_filter_str > 0:
                for i in xrange(0, self.seqList.count()):
                    if seq_filter_str.lower() in self.seqList.item(i).text():
                        self.seqList.setItemHidden(self.seqList.item(i), False)
                    else:
                        self.seqList.setItemHidden(self.seqList.item(i), True)


        elif list_type == "asset":
            asset_filter_str = str(self.assetFilter.text())
            if asset_filter_str > 0:
                for i in xrange(0, self.assetList.count()):
                    if asset_filter_str.lower() in self.assetList.item(i).text():
                        self.assetList.setItemHidden(self.assetList.item(i), False)
                    else:
                        self.assetList.setItemHidden(self.assetList.item(i), True)

    def projectList_Clicked(self):

        # Query the project id based on the name of the selected project
        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_project_path = str(
            self.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''',
                                (self.selected_project_name,)).fetchone()[0])

        # Query the departments associated with the project
        self.departments = (self.cursor.execute('''SELECT DISTINCT asset_type FROM assets WHERE project_name=?''',
                                                (self.selected_project_name,))).fetchall()

        # Populate the departments list
        self.departmentList.clear()
        self.departmentList.addItem("All")
        [self.departmentList.addItem(department[0]) for department in self.departments]

        # Query the sequences associated with the project
        self.sequences = (self.cursor.execute('''SELECT DISTINCT sequence_name FROM sequences WHERE project_name=?''',
                                              (self.selected_project_name,))).fetchall()
        self.sequences = sorted(self.sequences)

        # Populate the sequences lists
        self.seqList.clear()
        self.seqList.addItem("All")
        self.seqCreationList.clear()
        self.seqCreationList.addItem("All")
        self.shotList.clear()
        [self.seqList.addItem(sequence[0]) for sequence in self.sequences]
        [self.seqCreationList.addItem(sequence[0]) for sequence in self.sequences]

        # Populate the assets list
        self.all_assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''',
                                              (self.selected_project_name,)).fetchall()
        self.add_assets_to_asset_list(self.all_assets)

        # Populate the asset dependency list
        self.assetDependencyList.clear()
        for asset in self.all_assets:
            self.assetDependencyList.addItem(asset[5] + "_" + asset[3] + "_" + str(asset[6]))

    def projectList_DoubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_project_path))

    def departmentList_Clicked(self):
        self.selected_department = str(self.departmentList.selectedItems()[0].text())

        if len(self.seqList.selectedItems()) == 0:
            if self.selected_department == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''', (self.selected_project_name,))
            else:
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type=?''',
                                             (self.selected_project_name, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

        else:

            if self.selected_department == "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''', (self.selected_project_name,))
            elif self.selected_department == "All" and self.selected_sequence_name != "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND sequence_id=?''',
                                             (self.selected_project_name, self.selected_sequence_id))
            elif self.selected_department != "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type=?''',
                                             (self.selected_project_name, self.selected_department))
            else:
                self.selected_sequence_id = str(
                    self.cursor.execute('''SELECT sequence_id FROM sequences WHERE sequence_name=?''',
                                        (self.selected_sequence_name,)).fetchone()[0])
                assets = self.cursor.execute(
                    '''SELECT * FROM assets WHERE project_name=? AND sequence_id=? AND asset_type=?''',
                    (self.selected_project_name, self.selected_sequence_id, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

    def seqList_Clicked(self):
        self.selected_sequence_name = str(self.seqList.selectedItems()[0].text())

        # Add shots to shot list
        if not self.selected_sequence_name == "All":
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                             (self.selected_project_name, self.selected_sequence_name,)).fetchall()
            self.shotList.clear()
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [self.shotList.addItem(shot) for shot in shots]
        else:
            self.shotList.clear()


        if len(self.departmentList.selectedItems()) == 0:
            if self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''', (self.selected_project_name,))
            else:
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND sequence_name=?''',
                                             (self.selected_project_name, self.selected_sequence_name,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

        else:
            if self.selected_department == "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''', (self.selected_project_name,))
            elif self.selected_department == "All" and self.selected_sequence_name != "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND sequence_name=?''',
                                             (self.selected_project_name, self.selected_sequence_name))
            elif self.selected_department != "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type=?''',
                                             (self.selected_project_name, self.selected_department))
            else:
                assets = self.cursor.execute(
                    '''SELECT * FROM assets WHERE project_name=? AND sequence_name=? AND asset_type=?''',
                    (self.selected_project_name, self.selected_sequence_name, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

    def assetList_Clicked(self):

        self.selected_asset_type = str(self.assetList.selectedItems()[0].text()).split("_")[0]
        self.selected_asset_name = str(self.assetList.selectedItems()[0].text()).split("_")[1]
        self.selected_asset_version = str(self.assetList.selectedItems()[0].text()).split("_")[2]
        self.selected_asset_path = self.cursor.execute(
            '''SELECT asset_path FROM assets WHERE project_name=? AND asset_type=? AND asset_name=? AND asset_version=?''',
            (self.selected_project_name, self.selected_asset_type, self.selected_asset_name,
             self.selected_asset_version)).fetchone()[0]

        cur_asset = Asset(self.selected_asset_name, self.selected_asset_path)
        print(cur_asset.name)
        cur_asset.create_version(self.selected_project_name)

        asset_extension = os.path.splitext(self.selected_asset_path)[-1]
        if self.selected_asset_path.endswith(".jpg") or self.selected_asset_path.endswith(".png"):

            self.fileTypeLbl.setText("Image (" + asset_extension + ")")

            for i in reversed(range(self.actionFrameLayout.count())):  # Delete all items from layout
                self.actionFrameLayout.itemAt(i).widget().close()

            # Create action interface
            self.loadInKuadroBtn = QtGui.QPushButton(self.actionFrame)
            self.actionFrameLayout.addWidget(self.loadInKuadroBtn)
            self.loadInKuadroBtn.setText("Load in Kuadro")
            self.loadInKuadroBtn.clicked.connect(partial(self.load_asset, "Kuadro"))

        elif self.selected_asset_path.endswith(".mb") or self.selected_asset_path.endswith(".ma"):
            self.fileTypeLbl.setText("Maya (" + asset_extension + ")")

        elif self.selected_asset_path.endswith(".obj"):
            self.fileTypeLbl.setText("Geometry (" + asset_extension + ")")


        # Load thumbnail image
        if self.selected_asset_path.endswith(".jpg") or self.selected_asset_path.endswith(".png"):
            pixmap = QtGui.QPixmap(self.selected_asset_path).scaled(1000, 200, QtCore.Qt.KeepAspectRatio,
                                                                    QtCore.Qt.SmoothTransformation)
            self.assetImg.setPixmap(pixmap)
        else:
            asset_name = "_".join([self.selected_asset_type, self.selected_asset_name, self.selected_asset_version])
            thumb_path = self.screenshot_dir + asset_name + ".jpg"
            if os.path.isfile(thumb_path):
                pixmap = QtGui.QPixmap(thumb_path).scaled(1000, 200, QtCore.Qt.KeepAspectRatio,
                                                          QtCore.Qt.SmoothTransformation)
                self.assetImg.setPixmap(pixmap)
            else:
                pixmap = QtGui.QPixmap(self.screenshot_dir + "default\\no_img_found.png").scaled(1000, 200,
                                                                                                 QtCore.Qt.KeepAspectRatio,
                                                                                                 QtCore.Qt.SmoothTransformation)
                self.assetImg.setPixmap(pixmap)


        # Change path label
        self.assetPathLbl.setText(self.selected_asset_path)

        # Load comments
        self.commentTxt.setText("")  # Clear comment section
        asset_comment = self.cursor.execute(
            '''SELECT asset_comment FROM assets WHERE project_name=? AND asset_type=? AND asset_name=? AND asset_version=?''',
            (self.selected_project_name, self.selected_asset_type, self.selected_asset_name,
             self.selected_asset_version)).fetchone()[0]
        if asset_comment:
            self.commentTxt.setText(asset_comment)

    def departmentCreationList_Clicked(self):
        '''Filter the softwareCreationList based on the type of department selected.
        ex. if "Concept" is selected, only show Photoshop.
        '''

        selected_department = str(self.departmentCreationList.selectedItems()[0].text())
        self.webGroupBox.setEnabled(False)

        if selected_department == "Concept":
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(0), True)  # Blender
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(1), True)  # Cinema 4D
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(2), True)  # Houdini
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(3), True)  # Maya
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(4), False)  # Photoshop
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(5), True)  # Softimage
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(6), True)  # ZBrush

            self.assetDependencyList.setEnabled(False)
            self.webGroupBox.setEnabled(True)
            self.conceptWebLineEdit.setEnabled(True)
            try:
                self.softwareCreationList.setItemSelected(
                    self.softwareCreationList.setItemSelected(self.softwareCreationList.item(4), True))
            except:
                pass

        elif selected_department == "Modeling":
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(1), False)  # Cinema 4D
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(0), False)  # Blender
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(2), False)  # Houdini
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(3), False)  # Maya
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(4), True)  # Photoshop
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(5), False)  # Softimage
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(6), False)  # ZBrush
            self.assetDependencyList.setEnabled(False)

        elif selected_department == "Layout":
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(1), True)  # Cinema 4D
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(0), False)  # Blender
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(2), True)  # Houdini
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(3), False)  # Maya
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(4), True)  # Photoshop
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(5), False)  # Softimage
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(6), False)  # ZBrush
            self.assetDependencyList.setEnabled(True)

    def create_asset(self):
        '''Create asset
        '''

        asset_name = ""
        asset_path = ""

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.message_box(text="Please select a project first")
            return


        # Check if a department is selected
        try:
            selected_department = str(self.departmentCreationList.selectedItems()[0].text())
        except:
            self.message_box(text="You must first select a project and department")
            return

        # Check if a name is defined for the asset
        if len(str(self.assetNameCreationLineEdit.text())) == 0:
            self.message_box(text="Please enter a name for the asset")
            return
        else:
            asset_name = str(self.assetNameCreationLineEdit.text())

        # Check if a sequence is selected and starts building the path for the asset
        if len(self.seqCreationList.selectedItems()) > 0:
            selected_sequence = str(self.seqCreationList.selectedItems()[0].text())
            selected_sequence_id = str(
                self.cursor.execute('''SELECT sequence_id FROM sequences WHERE sequence_name=?''',
                                    (selected_sequence,)).fetchone()[0])
            asset_path = self.selected_project_path + "\\seq\\" + selected_sequence
        else:
            asset_path = self.selected_project_path + "\\assets"
            selected_sequence_id = "None"

        if selected_department == "Concept":

            oUrl = str(self.conceptWebLineEdit.text())
            if not len(oUrl) == 0:
                asset_path += "\\concepts\\concept_{0}_01.jpg".format(asset_name)
                asset_path, asset_name = self.check_if_asset_already_exists(asset_path, asset_name, "jpg")
                urllib.urlretrieve(oUrl, asset_path)
            else:
                asset_path += "\\concepts\\concept_{0}_01.psd".format(asset_name)
                asset_path, asset_name = self.check_if_asset_already_exists(asset_path, asset_name, "psd")
                shutil.copyfile("H:\\01-NAD\\_pipeline\\_utilities\\default_scenes\\photoshop.psd",
                                asset_path)

            self.cursor.execute(
                '''INSERT INTO assets(project_id, sequence_id, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?)''',
                (
                    self.selected_project_name, selected_sequence_id, asset_name, asset_path, "concept", "01",
                    self.username))

            self.db.commit()

        elif selected_department == "Modeling":
            pass

        elif selected_department == "Layout":
            pass

        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            subprocess.Popen([self.photoshop_path, asset_path])

    def check_if_asset_already_exists(self, asset_path, asset_name, asset_type):
        if not os.path.isfile(asset_path):
            return (asset_path, asset_name)
        else:

            asset_tmp = asset_name
            folder_path = "\\".join(asset_path.split("\\")[0:-1])
            assets_name_list = []

            new_asset_name = asset_name

            for cur_file in next(os.walk(folder_path))[2]:
                if asset_tmp in cur_file and asset_type in cur_file:
                    assets_name_list.append(cur_file.split("_")[1])

            assets_name_list = sorted(assets_name_list)
            try:
                asset_nbr = int(assets_name_list[-1].split("-")[-1])
                asset_nbr += 1
                new_asset_name += "-" + str(asset_nbr).zfill(3)
            except:
                new_asset_name += "-001"

            asset_path = asset_path.replace(asset_name, new_asset_name)

            return (asset_path, new_asset_name)

    def load_asset(self, action):
        if action == "Kuadro":

            if not QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
                os.system("taskkill /im kuadro.exe /f")
            subprocess.Popen(
                ["H:\\01-NAD\\_pipeline\\_utilities\\_soft\\kuadro.exe", self.selected_asset_path])
            return




        # Add last_access entry to database
        last_access = time.strftime("%B %d %Y at %H:%M:%S") + " by " + self.username
        self.cursor.execute('''UPDATE assets SET last_access = ? WHERE asset_path = ?''',
                            (last_access, self.selected_asset_path))

        self.db.commit()

        if self.selected_asset_path.endswith(".jpg") or self.selected_asset_path.endswith(
                ".png") or self.selected_asset_path.endswith(".obj"):
            SoftwareDialog(self.selected_asset_path, self).exec_()
        elif self.selected_asset_path.endswith(".ma") or self.selected_asset_path.endswith(".mb"):
            subprocess.Popen(["C:\\Program Files\\Autodesk\\Maya2015\\bin\\maya.exe", self.selected_asset_path])

    def add_assets_to_asset_list(self, assets_list):
        """
        Add assets from assets_list to self.assetList

        """

        self.assetList.clear()
        for asset in assets_list:
            self.assetList.addItem(asset[5] + "_" + asset[3] + "_" + str(asset[6]))

    def add_comment(self):
        if self.username == "Thibault":
            username = "<font color=red>Thibault</font>"

        # Check if there is already a comment or not to avoid empty first line due to HTML
        if self.commentTxt.toPlainText():
            comments = str(self.commentTxt.toHtml())
        else:
            comments = str(self.commentTxt.toPlainText())

        new_comment = "<b>{1}</b>: {0} ({2})\n".format(str(self.commentTxtLine.text()), username,
                                                       time.strftime("%d/%m/%Y"))
        new_comment = comments + new_comment
        self.cursor.execute('''UPDATE assets SET asset_comment = ? WHERE asset_path = ?''',
                            (new_comment, self.selected_asset_path,))
        self.db.commit()

        # Update comment field
        asset_comment = self.cursor.execute('''SELECT asset_comment FROM assets WHERE asset_path=?''',
                                            (self.selected_asset_path,)).fetchone()[0]
        self.commentTxt.setText(asset_comment)

    def save_prefs(self):
        """
        Save preferences

        """
        photoshop_path = str(self.photoshopPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Photoshop"''',
                            (photoshop_path,))

        maya_path = str(self.mayaPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Maya"''', (maya_path,))

        softimage_path = str(self.softimagePathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Softimage"''',
                            (softimage_path,))

        houdini_path = str(self.houdiniPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Houdini"''',
                            (houdini_path,))

        cinema4d_path = str(self.cinema4dPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Cinema 4D"''',
                            (cinema4d_path,))

        nuke_path = str(self.nukePathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Nuke"''', (nuke_path,))

        zbrush_path = str(self.zbrushPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="ZBrush"''',
                            (zbrush_path,))

        mari_path = str(self.mariPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Mari"''', (mari_path,))

        blender_path = str(self.blenderPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Blender"''',
                            (blender_path,))

        self.db.commit()

    def message_box(self, type="Warning", text="Warning"):
        self.msgBox = QtGui.QMessageBox()

        # Apply custom CSS to msgBox
        css = QtCore.QFile(self.cur_path + "\\media\\style.css")
        css.open(QtCore.QIODevice.ReadOnly)
        if css.isOpen():
            self.msgBox.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
        css.close()

        self.msgBox.setWindowTitle("Warning!")
        self.msgBox.setText(text)

        self.msgBox_okBtn = self.msgBox.addButton(QtGui.QMessageBox.Ok)
        self.msgBox.setDefaultButton(self.msgBox_okBtn)

        if type == "Warning":
            self.msgBox.setIcon(QtGui.QMessageBox.Warning)
        elif type == "Error":
            self.msgBox.setIcon(QtGui.QMessageBox.Critical)

        return self.msgBox.exec_()

    def center_window(self):
        """
        Move the window to the center of the screen

        """
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def open_in_explorer(self):
        """
        Open selected assets in explorer
        """
        subprocess.Popen(r'explorer /select,' + str(self.assetPathLbl.text()))

    def clear_filter(self, filter_type):
        """
        Clear the filter edit line
        """
        if filter_type == "seq":
            self.seqFilter.setText("")
        elif filter_type == "asset":
            self.assetFilter.setText("")

    def update_thumb(self):
        """
        Update selected asset thumbnail
        """
        self.Form.showMinimized()

        screenshot.take(self.screenshot_dir, self.selected_asset_name)

        pixmap = QtGui.QPixmap(self.screenshot_dir + self.selected_asset_name + ".jpg").scaled(1000, 200,
                                                                                               QtCore.Qt.KeepAspectRatio,
                                                                                               QtCore.Qt.SmoothTransformation)
        self.assetImg.setPixmap(pixmap)
        self.Form.showMaximized()
        self.Form.showNormal()


class Asset(Main):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def create_version(self, project_id):
        print(project_id)


class SoftwareDialog(QtGui.QDialog):
    def __init__(self, asset, parent=None):
        super(SoftwareDialog, self).__init__(parent)

        self.asset = asset

        self.setWindowTitle("Choose a software")
        self.horizontalLayout = QtGui.QHBoxLayout(self)

        if self.asset.endswith(".jpg"):
            self.photoshopBtn = QtGui.QPushButton("Photoshop")
            self.pictureviewerBtn = QtGui.QPushButton("Picture Viewer")

            self.photoshopBtn.clicked.connect(partial(self.btn_clicked, "photoshop"))
            self.pictureviewerBtn.clicked.connect(partial(self.btn_clicked, "pictureviewer"))

            self.horizontalLayout.addWidget(self.photoshopBtn)
            self.horizontalLayout.addWidget(self.pictureviewerBtn)

        elif self.asset.endswith(".obj"):
            self.mayaBtn = QtGui.QPushButton("Maya")
            self.softimageBtn = QtGui.QPushButton("Softimage")
            self.blenderBtn = QtGui.QPushButton("Blender")
            self.c4dBtn = QtGui.QPushButton("Cinema 4D")

            self.mayaBtn.clicked.connect(partial(self.btn_clicked, "maya"))
            self.softimageBtn.clicked.connect(partial(self.btn_clicked, "softimage"))
            self.blenderBtn.clicked.connect(partial(self.btn_clicked, "blender"))
            self.c4dBtn.clicked.connect(partial(self.btn_clicked, "c4d"))

            self.horizontalLayout.addWidget(self.mayaBtn)
            self.horizontalLayout.addWidget(self.softimageBtn)
            self.horizontalLayout.addWidget(self.blenderBtn)
            self.horizontalLayout.addWidget(self.c4dBtn)

    def btn_clicked(self, software):
        self.close()
        if software == "photoshop":
            subprocess.Popen(["C:\\Program Files\\Adobe\\Adobe Photoshop CS6 (64 Bit)\\Photoshop.exe", self.asset])
        elif software == "pictureviewer":
            os.system(self.asset)
        elif software == "maya":
            subprocess.Popen(["C:\\Program Files\\Autodesk\\Maya2015\\bin\\maya.exe", self.asset])
        elif software == "softimage":
            subprocess.Popen(["", self.asset])
        elif software == "blender":
            subprocess.Popen(["H:\\Dossiers Importants\\Google Drive\\Blender\\2.74\\blender.exe", "--python",
                              "H:\\01-NAD\\_pipeline\\_utilities\\software_scripts\\blender\\blender_obj_load.py",
                              self.asset])
        elif software == "c4d":
            subprocess.Popen(["H:\\Programmes\\Cinema 4D R16\\CINEMA 4D.exe", self.asset])



























            # Main Loop


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
