#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon
import subprocess
from functools import partial
import os
import shutil
from threading import Thread
from datetime import datetime
import time
from glob import glob
import re
import webbrowser
import pyperclip as clipboard
import distutils.core

from ui.add_assets_to_layout import Ui_addAssetsToLayoutWidget

class AssetLoader(object):
    def __init__(self):
        self.favorite_icon = QtGui.QIcon(self.cur_path + "/media/favorite.png")
        self.unfavorite_icon = QtGui.QIcon(self.cur_path + "/media/unfavorite.png")
        self.comment_icon = QtGui.QIcon(self.cur_path + "/media/comment.png")
        self.comment_disabled_icon = QtGui.QIcon(self.cur_path + "/media/comment_disabled.png")
        self.publish_icon = QtGui.QIcon(self.cur_path + "/media/publish.png")
        self.publish_disabled_icon = QtGui.QIcon(self.cur_path + "/media/publish_disabled.png")
        self.new_version_icon = QtGui.QIcon(self.cur_path + "/media/new_version.png")
        self.new_version_disabled_icon = QtGui.QIcon(self.cur_path + "/media/new_version_disabled.png")
        self.load_asset_icon = QtGui.QIcon(self.cur_path + "/media/load_asset.png")
        self.load_asset_disabled_icon = QtGui.QIcon(self.cur_path + "/media/load_asset_disabled.png")
        self.import_high_res_obj_icon = QtGui.QIcon(self.cur_path + "/media/import_layout_asset.png")
        self.has_uv_icon = QtGui.QIcon(self.cur_path + "/media/hasuv.png")
        self.has_uv_disabled_icon = QtGui.QIcon(self.cur_path + "/media/hasuv_disabled.png")
        self.update_thumb_icon = QtGui.QIcon(self.cur_path + "/media/update_thumb.png")
        self.load_in_gplay_icon = QtGui.QIcon(self.cur_path + "/media/load_in_gplay.png")
        self.delete_asset_icon = QtGui.QIcon(self.cur_path + "/media/delete_asset.png")
        self.open_real_layout_scene_icon = QtGui.QIcon(self.cur_path + "/media/open_real_layout_scene.png")
        self.load_in_headus_icon = QtGui.QIcon(self.cur_path + "/media/loaduv.png")

        self.updateThumbBtn.setIcon(self.update_thumb_icon)
        self.updateThumbBtn.setIconSize(QtCore.QSize(24, 24))
        self.loadObjInGplayBtn.setIcon(self.load_in_gplay_icon)
        self.loadObjInGplayBtn.setIconSize(QtCore.QSize(24, 24))
        self.publishBtn.setIcon(self.publish_disabled_icon)
        self.createVersionBtn.setIcon(self.new_version_disabled_icon)
        self.loadAssetBtn.setIcon(self.load_asset_disabled_icon)
        self.loadObjInHeadusBtn.setIconSize(QtCore.QSize(16, 16))
        self.importIntoSceneBtn.setIcon(self.import_high_res_obj_icon)
        self.deleteAssetBtn.setIcon(self.delete_asset_icon)
        self.openRealLayoutScene.setIcon(self.open_real_layout_scene_icon)
        self.loadObjInHeadusBtn.setIcon(self.load_in_headus_icon)
        self.publishBtn.setDisabled(True)
        self.createVersionBtn.setDisabled(True)
        self.loadAssetBtn.setDisabled(True)
        self.importIntoSceneBtn.setDisabled(True)
        self.loadObjInGplayBtn.setDisabled(True)
        self.deleteAssetBtn.setDisabled(True)
        self.openRealLayoutScene.setDisabled(True)

        if self.username in ["thoudon", "lclavet"]:
            self.deleteAssetBtn.show()
            self.deleteAssetLine.show()
            self.changeAssetSeqShotBtn.show()
        else:
            self.changeAssetSeqShotBtn.hide()
            self.deleteAssetLine.hide()
            self.deleteAssetBtn.hide()

        self.hasUvSeparator.hide()
        self.importIntoSceneBtn.hide()
        self.renderLine.hide()
        self.openRealLayoutScene.hide()
        self.createAssetFromScratchBtn.hide()
        self.changeAssetSoftwareBtn.hide()

        self.assets = {}
        self.selected_asset = None
        self.updateThumbBtn.hide()
        self.loadObjInGplayBtn.hide()

        # Get projects from database and add them to the projects list
        self.projects = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        self.projects = [str(i[0]) for i in self.projects]
        for project in self.projects:
            self.projectList.addItem(project)

        # Select default project
        self.projectList.setCurrentIndex(0)
        self.departmentList.setCurrentIndex(0)
        self.projectList_Clicked()

        #self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_department_name = "xxx"
        self.selected_sequence_name = "xxx"
        self.selected_shot_number = "xxxx"

        # Connect the filter textboxes
        self.assetFilter.textChanged.connect(self.filterList_textChanged)
        self.assetFilter.returnPressed.connect(self.filterList_textChanged)

        # Connect the lists
        self.projectList.currentIndexChanged .connect(self.projectList_Clicked)
        self.departmentList.currentIndexChanged.connect(self.departmentList_Clicked)
        self.seqList.currentIndexChanged.connect(self.seqList_Clicked)
        self.shotList.currentIndexChanged.connect(self.shotList_Clicked)
        self.assetList.itemClicked.connect(self.assetList_Clicked)
        self.versionList.itemClicked.connect(self.versionList_Clicked)
        self.versionList.itemDoubleClicked.connect(self.versionList_DoubleClicked)
        self.connect(self.versionList, QtCore.SIGNAL('version_arrow_key_pressed'), self.versionList_Clicked)
        self.connect(self.versionList, QtCore.SIGNAL('delete_selected_asset_version'), self.remove_version)
        self.connect(self.assetList, QtCore.SIGNAL('asset_arrow_key_pressed'), self.assetList_Clicked)
        self.connect(self.versionList, QtCore.SIGNAL('versionList_simple_view'), self.versionList_simple_view)
        self.connect(self.versionList, QtCore.SIGNAL('versionList_advanced_view'), self.versionList_advanced_view)
        self.connect(self.assetList, QtCore.SIGNAL('versionList_simple_view'), self.versionList_simple_view)
        self.connect(self.assetList, QtCore.SIGNAL('versionList_advanced_view'), self.versionList_advanced_view)
        self.connect(self.departmentList, QtCore.SIGNAL('department_arrow_key_pressed'), self.departmentList_Clicked)
        self.connect(self.seqList, QtCore.SIGNAL('seq_arrow_key_pressed'), self.seqList_Clicked)
        self.connect(self.shotList, QtCore.SIGNAL('shot_arrow_key_pressed'), self.shotList_Clicked)

        # Connect the buttons
        self.addRemoveAssetAsFavoriteBtn.clicked.connect(self.change_favorite_state)
        self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        self.addRemoveAssetAsFavoriteBtn.setDisabled(True)
        self.addRemoveAssetAsFavoriteBtn.setIconSize(QtCore.QSize(24, 24))
        self.addRemoveAssetAsFavoriteBtn.hide()
        self.openRealLayoutScene.clicked.connect(self.open_real_layout_scene)
        self.changeAssetSeqShotBtn.clicked.connect(self.change_seq_shot)
        self.loadObjInHeadusBtn.clicked.connect(self.load_obj_in_headus)
        self.changeAssetSoftwareBtn.clicked.connect(self.change_asset_software_01)

        self.loadObjInGplayBtn.clicked.connect(self.load_obj_in_gplay)

        self.updateThumbBtn.clicked.connect(partial(self.update_thumbnail, True))
        self.loadAssetBtn.clicked.connect(self.load_asset)
        self.importIntoSceneBtn.clicked.connect(self.import_into_scene)

        self.createAssetFromScratchBtn.clicked.connect(self.create_asset_from_scratch)
        self.createAssetFromAssetBtn.clicked.connect(self.create_asset_from_asset)
        self.deleteAssetBtn.clicked.connect(self.delete_asset)

        self.createVersionBtn.clicked.connect(self.create_new_version)
        self.publishBtn.clicked.connect(self.publish_asset)

        self.createAssetFromAssetBtn.hide()

        # Create right click menu on asset list
        self.assetList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assetList.connect(self.assetList, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.show_right_click_menu)
        self.shotList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.shotList.connect(self.shotList, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.show_shot_right_click_menu)
        self.versionList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.versionList.connect(self.versionList, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.show_right_click_menu_version)

        self.batchUpdateThumbnailsBtn.clicked.connect(self.batch_update_thumbnails)

        self.icon_display_type = "user"
        self.batch_thumbnail = False

    def show_right_click_menu(self, QPos):
        # Create a menu
        menu = QtGui.QMenu("Menu", self)
        if self.icon_display_type == "user":
            change_icon_display_action = menu.addAction("Change icon to asset type")
            change_icon_display_action.setIcon(QtGui.QIcon(self.cur_path + "/media/custom_media_icon.png"))
        elif self.icon_display_type == "manager":
            change_icon_display_action = menu.addAction("Change icon to custom media")
            change_icon_display_action.setIcon(QtGui.QIcon(self.cur_path + "/media/asset_type_icon.png"))
        change_icon_display_action.triggered.connect(self.change_icon_display)

        load_pure_ref_action = menu.addAction("Load References")
        load_pure_ref_action.setIcon(QtGui.QIcon(self.cur_path + "/media/eye_icon.png"))
        load_pure_ref_action.triggered.connect(self.load_pure_ref)

        # Show the context menu.
        menu.exec_(self.assetList.mapToGlobal(QPos))

    def show_right_click_menu_version(self, QPos):
        # Create a menu
        menu = QtGui.QMenu("Menu", self)

        show_full_media = menu.addAction("View thumbnail")
        show_full_media.setIcon(QtGui.QIcon(self.cur_path + "/media/asset_type_icon.png"))
        show_full_media.triggered.connect(self.versionList_simple_view)

        # Show the context menu
        menu.exec_(self.versionList.mapToGlobal(QPos))

    def load_pure_ref(self):
        pureref_process = QtCore.QProcess(self)
        pureref_process.start("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/PureRef.exe", ["Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/ref/pureref/" + self.selected_asset.name + ".pur"])

    def change_icon_display(self):
        if self.icon_display_type == "user":
            for asset, asset_item in self.assets.items():
                asset_item.setIcon(QtGui.QIcon(asset.default_media_manager))
            self.icon_display_type = "manager"
        elif self.icon_display_type == "manager":
            for asset, asset_item in self.assets.items():
                if os.path.isfile(asset.default_media_user):
                    asset_item.setIcon(QtGui.QIcon(asset.default_media_user))
                else:
                    asset_item.setIcon(QtGui.QIcon(asset.default_media_manager))
            self.icon_display_type = "user"

    def add_task_to_selected_asset(self):
        if len(self.assetList.selectedItems()) == 0:
            return

        self.tmNbrOfRowsToAddSpinBox.setValue(1)
        self.TaskManager.add_task(self, asset_id=self.selected_asset.id)
        self.Tabs.setCurrentWidget(self.Tabs.widget(1))

    def get_asset_id(self):
        pos = self.assetList.mapFromGlobal(QtGui.QCursor.pos())
        asset_item = self.assetList.itemAt(pos)
        asset = asset_item.data(QtCore.Qt.UserRole).toPyObject()
        clipboard.copy(str(asset.id))

    def show_shot_right_click_menu(self):
        pass
        # # Create a menu
        # menu = QtGui.QMenu("Menu", self)
        #
        # if self.username in ["thoudon", "lclavet"]:
        #     change_shot_framerange = menu.addAction("Add task")
        #     change_shot_framerange.setIcon(QtGui.QIcon(self.cur_path + "/media/change_shot_framerange.png"))
        #     change_shot_framerange.triggered.connect(self.change_shot_framerange)
        #
        # # Show the context menu.
        # menu.exec_(self.shotList.mapToGlobal(QPos))

    def change_favorite_state(self):

        if self.selected_asset == None:
            return

        selected_asset_publish = self.cursor.execute('''SELECT asset_id FROM assets WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_type=? AND asset_version="out"''', (self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, self.selected_asset.type, )).fetchone()
        selected_asset_publish_id = selected_asset_publish[0]

        is_asset_favorited = self.cursor.execute('''SELECT * FROM favorited_assets WHERE asset_id=? AND member=?''', (selected_asset_publish_id, self.username,)).fetchone()
        if is_asset_favorited == None: # Asset is not already favorited by member
            self.cursor.execute('''INSERT INTO favorited_assets(asset_id, member) VALUES(?,?)''', (selected_asset_publish_id, self.username,))
            self.db.commit()
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.favorite_icon)
        else:
            self.cursor.execute('''DELETE FROM favorited_assets WHERE asset_id=? AND member=?''', (is_asset_favorited[0], is_asset_favorited[1],))
            self.db.commit()
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)

    def change_uv_state(self):
        if self.selected_asset == None:
            return

        is_asset_uved = self.cursor.execute('''SELECT * FROM uved_assets WHERE asset_id=?''', (self.selected_asset.id, )).fetchone()
        if is_asset_uved == None:
            self.cursor.execute('''INSERT INTO uved_assets(asset_id, has_uv, username) VALUES(?,?,?)''', (self.selected_asset.id, 1, self.username))
            self.db.commit()
        else:
            self.cursor.execute('''DELETE FROM uved_assets WHERE asset_id=?''', (self.selected_asset.id,))
            self.db.commit()

    def add_project(self):

        # Create soft selection and asset name dialog
        dialog = QtGui.QDialog(self)
        self.Lib.apply_style(self, dialog)

        dialog.setWindowTitle("Enter a name")
        dialog_main_layout = QtGui.QVBoxLayout(dialog)

        name_line_edit = QtGui.QLineEdit()
        name_line_edit.setPlaceholderText("Please enter a name...")
        name_line_edit.returnPressed.connect(dialog.accept)
        shortname_line_edit = QtGui.QLineEdit()
        shortname_line_edit.setPlaceholderText("Please enter a shortname (3 letters)")

        dialog_main_layout.addWidget(name_line_edit)
        dialog_main_layout.addWidget(shortname_line_edit)

        dialog.exec_()

        if dialog.result() == 0:
            return


        # Get asset name
        project_name = unicode(name_line_edit.text())
        project_name = self.Lib.normalize_str(self, project_name)
        project_name = project_name_tmp = self.Lib.convert_to_camel_case(self, project_name)

        project_shortname = str(name_line_edit.text())
        selected_folder = str(QtGui.QFileDialog.getExistingDirectory())

        # Prevent two projects from having the same name
        all_projects_name = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        all_projects_name = [i[0] for i in all_projects_name]
        if project_name in all_projects_name:
            self.Lib.message_box(text="Project name is already taken.")
            return

        # Create project's folder
        project_path = selected_folder + "\\" + project_name
        os.makedirs(project_path + "\\assets")
        os.makedirs(project_path + "\\assets\\anm")
        os.makedirs(project_path + "\\assets\\anm\\.thumb")
        os.makedirs(project_path + "\\assets\\anm\\.comments")
        os.makedirs(project_path + "\\assets\\cam")
        os.makedirs(project_path + "\\assets\\cam\\.thumb")
        os.makedirs(project_path + "\\assets\\cam\\.comments")
        os.makedirs(project_path + "\\assets\\cmp")
        os.makedirs(project_path + "\\assets\\cmp\\.comments")
        os.makedirs(project_path + "\\assets\\dmp")
        os.makedirs(project_path + "\\assets\\dmp\\.comments")
        os.makedirs(project_path + "\\assets\\edt")
        os.makedirs(project_path + "\\assets\\edt\\.comments")
        os.makedirs(project_path + "\\assets\\lay")
        os.makedirs(project_path + "\\assets\\lay\\.thumb")
        os.makedirs(project_path + "\\assets\\lay\\.comments")
        os.makedirs(project_path + "\\assets\\lgt")
        os.makedirs(project_path + "\\assets\\lgt\\.thumb")
        os.makedirs(project_path + "\\assets\\lgt\\.comments")
        os.makedirs(project_path + "\\assets\\mod")
        distutils.dir_util.copy_tree(self.cur_path_one_folder_up + "\\_setup\\system", project_path + "\\assets\\mod\\system")
        os.makedirs(project_path + "\\assets\\mod\\.thumb")
        os.makedirs(project_path + "\\assets\\mod\\.comments")
        os.makedirs(project_path + "\\assets\\ref")
        os.makedirs(project_path + "\\assets\\ref\\.comments")
        os.makedirs(project_path + "\\assets\\rig")
        os.makedirs(project_path + "\\assets\\rig\\.thumb")
        os.makedirs(project_path + "\\assets\\rig\\.comments")
        os.makedirs(project_path + "\\assets\\rnd")
        os.makedirs(project_path + "\\assets\\rnd\\.comments")
        os.makedirs(project_path + "\\assets\\shd")
        os.makedirs(project_path + "\\assets\\shd\\.thumb")
        os.makedirs(project_path + "\\assets\\shd\\.comments")
        os.makedirs(project_path + "\\assets\\sim")
        os.makedirs(project_path + "\\assets\\sim\\.thumb")
        os.makedirs(project_path + "\\assets\\sim\\.comments")
        os.makedirs(project_path + "\\assets\\stb")
        os.makedirs(project_path + "\\assets\\stb\\.comments")
        os.makedirs(project_path + "\\assets\\tex")
        os.makedirs(project_path + "\\assets\\tex\\.thumb")
        os.makedirs(project_path + "\\assets\\tex\\.comments")

        # Add project to database
        self.cursor.execute('''INSERT INTO projects(project_name, project_shortname, project_path) VALUES (?, ?, ?)''',
                            (project_name, project_shortname, project_path))
        self.db.commit()

    def add_sequence(self):
        """Add specified sequence to the selected project
        """

        # Create sequence name dialog
        dialog = QtGui.QDialog(self)
        self.Lib.apply_style(self, dialog)

        dialog.setWindowTitle("Enter a name")
        dialog_main_layout = QtGui.QVBoxLayout(dialog)

        name_line_edit = QtGui.QLineEdit()
        name_line_edit.setPlaceholderText("Please enter a name...")
        name_line_edit.returnPressed.connect(dialog.accept)

        dialog_main_layout.addWidget(name_line_edit)

        dialog.exec_()

        if dialog.result() == 0:
            return

        sequence_name = str(name_line_edit.text())

        # Check if user entered a 3 letter sequence name
        if len(sequence_name) == 0:
            self.Lib.message_box(text="Please enter a sequence name")
            return
        elif len(sequence_name) < 3:
            self.Lib.message_box(text="Please enter a 3 letters name")
            return

        # Check if a project is selected
        if not self.projectList.currentText():
            self.Lib.message_box(text="Please select a project first")
            return

        # Prevent two sequences from having the same name
        all_sequences_name = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''',
                                                 (self.selected_project_name,)).fetchall()
        all_sequences_name = [i[0] for i in all_sequences_name]
        if sequence_name in all_sequences_name:
            self.Lib.message_box(text="Sequence name is already taken.")
            return

        # Add sequence to database
        self.cursor.execute('''INSERT INTO sequences(project_name, sequence_name) VALUES (?, ?)''',
                            (self.selected_project_name, sequence_name))

        self.db.commit()

        # Add sequence to GUI
        self.seqList.addItem(sequence_name)
        self.seqList_Clicked()

    def add_shot(self):

        # Check if a project and a sequence are selected
        if self.selected_sequence_name in ["All", "None", "xxx"]:
            self.Lib.message_box(self, type="error", text="Please select a project and a sequence first.")
            return

        # Create shot number dialog
        dialog = QtGui.QDialog(self)
        self.Lib.apply_style(self, dialog)

        dialog.setWindowTitle("Enter a number")
        dialog_main_layout = QtGui.QVBoxLayout(dialog)
        dialog.setMinimumWidth(150)

        shot_number_spinbox = QtGui.QSpinBox()
        shot_number_spinbox.setMinimum(10)
        shot_number_spinbox.setMaximum(2000)
        shot_number_spinbox.setValue(10)
        shot_number_spinbox.setSingleStep(10)
        accept_btn = QtGui.QPushButton("Create Shot")
        accept_btn.clicked.connect(dialog.accept)

        dialog_main_layout.addWidget(shot_number_spinbox)
        dialog_main_layout.addWidget(accept_btn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        shot_number = str(shot_number_spinbox.text()).zfill(4)

        # Prevent two shots from having the same number
        all_shots_number = self.cursor.execute(
            '''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
            (self.selected_project_name, self.selected_sequence_name)).fetchall()
        all_shots_number = [i[0] for i in all_shots_number]
        if shot_number in all_shots_number:
            self.Lib.message_box(text="Shot number already exists.")
            return

        # Add shot to database
        self.cursor.execute('''INSERT INTO shots(project_name, sequence_name, shot_number, frame_start, frame_end) VALUES (?, ?, ?, ?, ?)''',
                            (self.selected_project_name, self.selected_sequence_name, shot_number, "1", "1"))

        self.db.commit()

        # Add shot to GUI
        self.shotList.addItem(shot_number)
        self.seqList_Clicked()

        self.Lib.message_box(self, type="info", text="Successfully created shot " + shot_number)

    def change_seq_shot(self):
        '''
        Change sequence and shot for selected references
        '''
        # Create the change seq shot dialog
        change_dialog = QtGui.QDialog()
        change_dialog.setWindowTitle("Change Sequence / Shot")
        change_dialog.setMinimumWidth(200)
        self.Lib.apply_style(self, change_dialog)

        # Create main layout
        main_layout = QtGui.QVBoxLayout(change_dialog)

        # Create seq and shot combo box
        self.change_ref_seq_combobox = QtGui.QComboBox()
        self.change_ref_seq_combobox.addItem("All")
        self.change_ref_seq_combobox.addItems([seq for seq in self.sequences])
        self.change_ref_shot_combobox = QtGui.QComboBox()
        self.change_ref_shot_combobox.addItem("None")

        # Create accept button
        apply_btn = QtGui.QPushButton("Accept")

        # Create labels
        sequence_lbl = QtGui.QLabel("Sequence Name:")
        shot_lbl = QtGui.QLabel("Shot Number:")

        # Add widgets to layout
        main_layout.addWidget(sequence_lbl)
        main_layout.addWidget(self.change_ref_seq_combobox)
        main_layout.addWidget(shot_lbl)
        main_layout.addWidget(self.change_ref_shot_combobox)
        main_layout.addWidget(apply_btn)

        # Connect the widgets to the functions
        apply_btn.clicked.connect(change_dialog.accept)
        self.change_ref_seq_combobox.currentIndexChanged.connect(self.ref_change_seq_shot_filter_shots)

        # Execute the QDialog
        change_dialog.exec_()

        # If user close dialog, return
        if change_dialog.result() == 0:
            return

        # Get selected asset and change seq shot
        selected_sequence = str(self.change_ref_seq_combobox.currentText())
        selected_shot = str(self.change_ref_shot_combobox.currentText())
        if selected_sequence == "All": selected_sequence = "xxx"
        if selected_shot == "None": selected_shot = "xxxx"

        self.selected_asset.change_sequence(selected_sequence)
        self.selected_asset.change_shot(selected_shot)

        sequence = self.sg.find_one("Sequence", [["code","is",selected_sequence]])
        if len(sequence) > 0:
            shot = self.sg.find_one("Shot", [["sg_sequence","is",sequence],["code","is",selected_shot]])
        else:
            sequence = ''
            shot = ''

        sg_asset = self.sg.find_one("Asset", [["code","is",self.selected_asset.name]])
        self.sg.update("Asset", sg_asset["id"], {'shots': [shot], 'sequences': [sequence]})

    def change_seq_shot_filter_shots(self):
        '''
        Add shots based on what sequence was clicked on the ref_change_seq_shot layout
        '''
        selected_sequence_name = str(self.change_ref_seq_combobox.currentText())

        # Add shots to shot list and shot creation list
        self.change_ref_shot_combobox.clear()
        self.change_ref_shot_combobox.addItem("None")
        if selected_sequence_name != "All":
            [self.change_ref_shot_combobox.addItem(shot) for shot in self.shots[selected_sequence_name]]

    def load_all_assets_for_first_time(self):
        '''
        Add all assets from selected project. Only run once to rebuild assets objects from Asset class.
        '''
        self.assets = {}
        assets_list = []
        self.versions = []
        self.assetList.clear()
        self.versionList.clear()

        all_assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type !=?''', (self.selected_project_name, "ref")).fetchall()
        for asset in all_assets:
            asset_id = asset[0]
            project_name = asset[1]
            sequence_name = asset[2]
            shot_number = asset[3]
            asset_name = asset[4]
            asset_path = asset[5]
            asset_extension = asset[6]
            asset_type = asset[7]
            asset_version = asset[8]
            asset_tags = asset[9]
            asset_dependency = asset[10]
            last_access = asset[11]
            last_publish = asset[12]
            creator = asset[13]
            number_of_publishes = asset[14]
            publish_from_version = asset[15]

            # Create asset object and attach it to the ListWidgetItem
            asset = self.Asset(self, asset_id, project_name, sequence_name, shot_number, asset_name, asset_path, asset_extension, asset_type, asset_version, asset_tags, asset_dependency, last_access, last_publish, creator, number_of_publishes, publish_from_version)

            # Create ListWidget Item
            if "-lowres" in asset.name:
                asset_name = asset.name.replace("-lowres", "")
            else:
                asset_name = asset.name
            asset_item = QtGui.QListWidgetItem(asset_name + " (" + asset.type + ")")
            if os.path.isfile(asset.default_media_user):
                asset_item.setIcon(QtGui.QIcon(asset.default_media_user))
            else:
                pixmap = QtGui.QPixmap(asset.default_media_manager)
                pixmap = pixmap.scaled(256, 256, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                asset_item.setIcon(QtGui.QIcon(pixmap))

            asset_item.setData(QtCore.Qt.UserRole, asset)

            # Dictionary of asset objects associated with listwidget item (Exemple Class Asset -> ListWidgetItem)
            # Useful to have access to both the asset object and its associated ListWidgetItem.
            self.assets[asset] = asset_item

            # Append each item's sequence, shot, name and type to a list to only add first version of an asset to assetList
            assets_list.append((asset.sequence, asset.shot, asset.name, asset.type))
            if asset.version != "out" and asset.type not in ["lgt", "cam"]: # If asset is not a published asset, add it to version list
                # If there's less than 2 entries for an asset, add it to the assetList.
                # If there's more than 2 entries, it means that current loop is on the version 02 or more of an asset.
                # Therefore, its first version is already in the assetList and you don't need to add the other versions too.
                if assets_list.count((asset.sequence, asset.shot, asset.name, asset.type)) < 2:
                    self.assetList.addItem(asset_item)

                # Add all versions to version List.
                version_item = QtGui.QListWidgetItem(asset.version + " (" + asset.extension + ")")
                version_item.setData(QtCore.Qt.UserRole, asset)

                # If asset is first version, set its icon to first thumbnail
                if asset.version == "01":
                    if os.path.isfile(asset.first_media):
                        version_item.setIcon(QtGui.QIcon(asset.first_media))
                    else:
                        version_item.setIcon(QtGui.QIcon(self.cur_path + "\\media\\default_asset_thumb\\version\\" + str(asset.version).zfill(2) + ".png"))
                else:
                    if os.path.isfile(asset.default_media_user):
                        version_item.setIcon(QtGui.QIcon(asset.default_media_user))
                    else:
                        version_item.setIcon(QtGui.QIcon(self.cur_path + "\\media\\default_asset_thumb\\version\\" + str(asset.version).zfill(2) + ".png"))

                self.versions.append(version_item)
                self.versionList.addItem(version_item)
                version_item.setHidden(True)

    def projectList_Clicked(self):

        if self.projectList.count() == 0:
            self.selected_project_name = "None"
            self.selected_project_path = "None"
            self.selected_project_shortname = "None"
            return

        # Query the project id based on the name of the selected project
        self.selected_project_name = str(self.projectList.currentText())
        self.selected_project_path = str(self.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''', (self.selected_project_name,)).fetchone()[0])
        self.selected_project_shortname = str(self.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.selected_project_name,)).fetchone()[0])

        # Query the sequences associated with the project
        self.sequences = self.sg.find("Sequence", [['project', 'is', {'type': 'Project', 'id': self.sg_project_id}]], ["code"])
        self.sequences = [seq["code"] for seq in self.sequences]
        self.sequences = sorted(self.sequences)


        # Query the shots associated with each sequence
        self.shots = {}
        for seq in self.sequences:
            sequence = self.sg.find_one("Sequence", [["code","is",seq]])
            shots = self.sg.find("Shot", [["sg_sequence","is",sequence]], ["code"])
            shots = [shot["code"] for shot in shots]
            self.shots[str(seq)] = [str(shot) for shot in shots]

        # Populate the sequences and shots lists
        self.seqList.clear()
        self.seqList.addItem("All")
        self.seqList.addItem("None")
        self.seqReferenceList.clear()
        self.seqReferenceList.addItem("All")
        self.seqReferenceList.addItem("None")
        self.shotList.clear()
        self.shotReferenceList.clear()
        self.shotReferenceList.addItem("None")
        [(self.seqList.addItem(sequence), self.seqReferenceList.addItem(sequence)) for sequence in self.sequences]

        # Select "All" from sequence list and "None" from shot list
        self.seqList.setCurrentIndex(0)
        self.shotList.setCurrentIndex(0)

        # Load all assets
        if self.assetList.count() == 0:
            self.load_all_assets_for_first_time()

    def projectList_DoubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_project_path))

    def seqList_Clicked(self):

        # Disable all buttons
        self.publishBtn.setDisabled(True)
        self.createVersionBtn.setDisabled(True)
        self.loadAssetBtn.setDisabled(True)
        self.importIntoSceneBtn.setDisabled(True)
        self.addRemoveAssetAsFavoriteBtn.setDisabled(True)
        self.openRealLayoutScene.setDisabled(True)
        self.deleteAssetBtn.setDisabled(True)

        self.selected_shot_number = "xxxx"

        self.selected_sequence_name = str(self.seqList.currentText())
        if self.selected_sequence_name == "None" or self.selected_sequence_name == "All":
            self.selected_sequence_name = "xxx"

        # Add shots to shot list and reference tool shot list
        if self.selected_sequence_name == "xxx":
            self.shotList.clear()
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
        else:
            shots = self.shots[self.selected_sequence_name]
            self.shotList.clear()
            self.shotList.addItem("All")
            self.shotList.addItem("None")
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
            shots = [i for i in shots if i != "xxxx"]
            shots = sorted(shots)
            [(self.shotList.addItem(shot), self.shotReferenceList.addItem(shot)) for shot in shots]

        self.shotList.setCurrentIndex(0)
        self.load_assets_from_selected_seq_shot_dept()

    def shotList_Clicked(self):

        # Disable all buttons
        self.publishBtn.setDisabled(True)
        self.createVersionBtn.setDisabled(True)
        self.loadAssetBtn.setDisabled(True)
        self.importIntoSceneBtn.setDisabled(True)
        self.addRemoveAssetAsFavoriteBtn.setDisabled(True)
        self.openRealLayoutScene.setDisabled(True)
        self.deleteAssetBtn.setDisabled(True)

        try:
            self.selected_shot_number = str(self.shotList.currentText())
        except:
            return
        if self.selected_shot_number == "None" or self.selected_shot_number == "All":
            self.selected_shot_number = "xxxx"

        # if os.path.isfile("Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/stb/" + self.selected_sequence_name + "_" + self.selected_shot_number + ".jpg"):
        #     img_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/stb/" + self.selected_sequence_name + "_" + self.selected_shot_number + ".jpg"
        # else:
        #     img_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/stb/default_stb_img.png"


        self.load_assets_from_selected_seq_shot_dept()

    def shotList_DoubleClicked(self):

        if self.selected_shot_number == "All" or self.selected_shot_number == "xxxx":
            return

        framerange = self.cursor.execute('''SELECT frame_start, frame_end FROM shots WHERE project_name=? AND sequence_name=? AND shot_number=?''', (self.selected_project_name, self.selected_sequence_name, self.selected_shot_number,)).fetchone()
        start_frame = framerange[0]
        end_frame = framerange[1]

        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Change Framerange")
        dialog.setMinimumWidth(200)
        layout = QtGui.QGridLayout(dialog)

        start_spinbox = QtGui.QSpinBox()
        end_spinbox = QtGui.QSpinBox()

        start_spinbox.setMinimum(1)
        start_spinbox.setMaximum(10000)
        end_spinbox.setMinimum(1)
        end_spinbox.setMaximum(10000)

        start_spinbox.setValue(start_frame)
        end_spinbox.setValue(end_frame)

        if self.username != "thoudon" or self.username != "lclavet":
            update_btn = QtGui.QPushButton("Update Framerange", dialog)
            update_btn.clicked.connect(dialog.accept)
            layout.addWidget(start_spinbox, 0, 0)
            layout.addWidget(end_spinbox, 0, 1)
            layout.addWidget(update_btn, 1, 0, 2, 2)
        else:
            start_spinbox.setDisabled(True)
            end_spinbox.setDisabled(True)
            layout.addWidget(start_spinbox, 0, 0)
            layout.addWidget(end_spinbox, 0, 1)



        dialog.exec_()

        if dialog.result() == 0:
            return

        new_start_frame = start_spinbox.value()
        new_end_frame = end_spinbox.value()

        self.cursor.execute('''UPDATE shots SET frame_start=?, frame_end=? WHERE project_name=? AND sequence_name=? AND shot_number=?''', (new_start_frame, new_end_frame, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number,))
        self.db.commit()

    def departmentList_Clicked(self):

        # Disable all buttons
        self.loadAssetBtn.setDisabled(True)
        self.importIntoSceneBtn.setDisabled(True)
        self.createVersionBtn.setDisabled(True)
        self.publishBtn.setDisabled(True)
        self.loadObjInGplayBtn.setDisabled(True)
        self.updateThumbBtn.setDisabled(True)
        self.addRemoveAssetAsFavoriteBtn.setDisabled(True)
        self.openRealLayoutScene.setDisabled(True)
        self.deleteAssetBtn.setDisabled(True)

        self.selected_department_name = str(self.departmentList.currentText())
        if self.selected_department_name == "All":
            self.selected_department_name = "xxx"
        else:
            self.selected_department_name = self.departments_shortname[self.selected_department_name]

        if self.username in ["thoudon", "lclavet"]:
            # Change display of create asset from scratch
            if self.selected_department_name == "mod":
                self.createAssetFromScratchBtn.show()
                self.createAssetFromScratchBtn.setText("Create Modeling Asset")
            elif self.selected_department_name == "tex":
                self.createAssetFromScratchBtn.hide()
            elif self.selected_department_name == "rig":
                self.createAssetFromScratchBtn.hide()
            elif self.selected_department_name == "anm":
                self.createAssetFromScratchBtn.show()
                self.createAssetFromScratchBtn.setText("Create Animation Scene")
            elif self.selected_department_name == "lay":
                self.createAssetFromScratchBtn.show()
                self.createAssetFromScratchBtn.setText("Create Layout Scene")
            elif self.selected_department_name == "cam":
                self.createAssetFromScratchBtn.hide()
            elif self.selected_department_name == "shd":
                self.createAssetFromScratchBtn.hide()
            elif self.selected_department_name == "lgt":
                self.createAssetFromScratchBtn.hide()
            elif self.selected_department_name == "sim":
                self.createAssetFromScratchBtn.show()
                self.createAssetFromScratchBtn.setText("Create Simulation Asset")
            elif self.selected_department_name == "dmp":
                self.createAssetFromScratchBtn.show()
                self.createAssetFromScratchBtn.setText("Create DMP Asset")
            elif self.selected_department_name == "cmp":
                self.createAssetFromScratchBtn.hide()
            elif self.selected_department_name == "xxx":
                self.createAssetFromScratchBtn.hide()

        # Hide load obj buttons
        self.importIntoSceneBtn.hide()

        # Reset last publish and last access text
        self.lastAccessLbl.setText("Last accessed by: ...")
        self.lastPublishedLbl.setText("Last published by: ...")

        self.updateThumbBtn.hide()

        self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        self.load_assets_from_selected_seq_shot_dept()

    def assetList_Clicked(self):
        # Enable buttons
        self.publishBtn.setDisabled(False)
        self.createVersionBtn.setDisabled(False)
        self.loadAssetBtn.setDisabled(False)
        self.importIntoSceneBtn.setDisabled(False)
        self.addRemoveAssetAsFavoriteBtn.setDisabled(False)
        self.updateThumbBtn.setDisabled(False)
        self.deleteAssetBtn.setDisabled(False)
        self.openRealLayoutScene.setDisabled(False)

        try:
            selected_asset = self.assetList.selectedItems()[0]
            selected_asset = selected_asset.data(QtCore.Qt.UserRole).toPyObject()
        except:
            return

        for version_item in self.versions:
            version_asset = version_item.data(QtCore.Qt.UserRole).toPyObject()
            if selected_asset.name == version_asset.name and selected_asset.type == version_asset.type and selected_asset.sequence == version_asset.sequence:
                version_item.setHidden(False)
                version_item.setSelected(True)
            else:
                version_item.setHidden(True)

        self.updateThumbBtn.show()
        self.versionList_Clicked()

    def versionList_simple_view(self):
        if self.selected_asset == None:
            return

        self.statusLbl.setText("Status: Loading Media")
        media_process = QtCore.QProcess(self)
        media_process.finished.connect(lambda: self.statusLbl.setText("Status: Idle..."))
        if self.selected_asset.type in ["mod"]:
            media_process.start("H:/DJView/bin/djv_view.exe", [self.selected_asset.full_media])
        elif self.selected_asset.type in ["shd", "tex"]:
            media_process.start("H:/DJView/bin/djv_view.exe", [self.selected_asset.first_media])

    def versionList_advanced_view(self):
        if self.selected_asset == None:
            return

        self.statusLbl.setText("Status: Loading Media")
        media_process = QtCore.QProcess(self)
        media_process.finished.connect(lambda: self.statusLbl.setText("Status: Idle..."))

        if self.selected_asset.type in ["rig", "tex", "lay"]:
            if self.selected_asset.version == "01":
                subprocess.Popen([self.cur_path_one_folder_up + "\\_soft\\ImageGlass\\ImageGlass.exe", self.selected_asset.first_media])
            else:
                subprocess.Popen([self.cur_path_one_folder_up + "\\_soft\\ImageGlass\\ImageGlass.exe", self.selected_asset.full_media])
            self.statusLbl.setText("Status: Idle...")
        elif self.selected_asset.type in ["shd"]:
            subprocess.Popen(["H:/DJView/bin/djv_view.exe", self.selected_asset.advanced_media])
            self.statusLbl.setText("Status: Idle...")
        else:
            if not os.path.isfile(self.selected_asset.advanced_media):
                if self.selected_asset.version == "01":
                    subprocess.Popen([self.cur_path_one_folder_up + "\\_soft\\ImageGlass\\ImageGlass.exe", self.selected_asset.first_media])
                else:
                    subprocess.Popen([self.cur_path_one_folder_up + "\\_soft\\ImageGlass\\ImageGlass.exe", self.selected_asset.full_media])

            media_process.start("H:/DJView/bin/djv_view.exe", [self.selected_asset.advanced_media])

    def versionList_Clicked(self):

        self.statusLbl.setText("Status: Idle...")

        # If user press arrow key in a tab other than Asset Loader, don't do anything
        current_tab_text = self.Tabs.tabText(self.Tabs.currentIndex())
        if current_tab_text != "Asset Loader":
            return

        # Reset last published label
        self.lastPublishedLbl.setText("Last published by: ...")

        try:
            selected_version = self.versionList.selectedItems()[0]
        except:
            return
        self.selected_asset = selected_version.data(QtCore.Qt.UserRole).toPyObject()

        if self.selected_asset.type == "mod":
            self.loadObjInHeadusBtn.show()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.show()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.importIntoSceneBtn.show()
            self.loadObjInGplayBtn.show()
            if "lowres" in self.selected_asset.name:
                self.createAssetFromAssetBtn.hide()
            else:
                if self.username in ["thoudon", "lclavet"]:
                    self.createAssetFromAssetBtn.show()
                    self.createAssetFromAssetBtn.setText("Create Rig, Texture, Shading or Low-Res from Modeling")
                self.hasUvSeparator.show()
            self.publishBtn.show()
            self.loadObjInGplayBtn.setDisabled(False)


        elif self.selected_asset.type == "cam":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.show()

        elif self.selected_asset.type == "lgt":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.hide()

        elif self.selected_asset.type == "tex":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()

        elif self.selected_asset.type == "rig":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.show()
            self.createAssetFromAssetBtn.hide()

        elif self.selected_asset.type == "anm":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.show()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.show()

        elif self.selected_asset.type == "sim":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.show()

        elif self.selected_asset.type == "shd":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.hide()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.show()
            self.createAssetFromAssetBtn.hide()


        elif self.selected_asset.type == "lay":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.hasUvSeparator.hide()
            if self.username in ["thoudon", "lclavet"]:
                self.createAssetFromAssetBtn.show()
                self.createAssetFromAssetBtn.setText("Create Camera or Lighting from Layout")
                self.renderLine.show()
                self.openRealLayoutScene.show()
                self.createVersionBtn.show()
                self.importIntoSceneBtn.show()
            else:
                self.importIntoSceneBtn.hide()
                self.renderLine.hide()
                self.openRealLayoutScene.hide()
                self.createVersionBtn.hide()
            if self.username in ["cgonnord", "costiguy", "mroz"]:
                self.openRealLayoutScene.show()
            self.importIntoSceneBtn.show()
            self.publishBtn.hide()
            self.loadObjInGplayBtn.hide()


        elif self.selected_asset.type == "dmp":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.show()

        elif self.selected_asset.type == "cmp":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.publishBtn.show()

        elif self.selected_asset.type == "rdr":
            self.loadObjInHeadusBtn.hide()
            self.createVersionBtn.show()
            self.changeAssetSoftwareBtn.hide()
            self.renderLine.hide()
            self.openRealLayoutScene.hide()
            self.hasUvSeparator.hide()
            self.createAssetFromAssetBtn.hide()
            self.importIntoSceneBtn.hide()
            self.loadObjInGplayBtn.hide()
            self.selected_department_name = "lay"

        else:
            pass


        # Set labels
        if len(self.selected_asset.last_access) == 0:
            self.lastAccessLbl.setText("Last accessed by: ...")
        else:
            self.lastAccessLbl.setText("Last accessed by: " + self.selected_asset.last_access)

        # Set Is In Layout label
        if "-lowres" in self.selected_asset.name:
            asset_name = self.selected_asset.name.replace("-lowres", "")
        else:
            asset_name = self.selected_asset.name
        if self.selected_asset.type == "cam":
            layout_asset = self.cursor.execute('''SELECT asset_id FROM assets WHERE asset_name=? AND asset_type="cam" AND asset_extension="hda"''', (asset_name,)).fetchone()
        else:
            layout_asset = self.cursor.execute('''SELECT asset_id FROM assets WHERE asset_name=? AND asset_type="lay" AND asset_extension="hda" AND asset_version="out"''', (asset_name,)).fetchone()

        if layout_asset != None:
            layout_asset_id = layout_asset[0]
            is_asset_in_layout = self.cursor.execute('''SELECT layout_id FROM assets_in_layout WHERE asset_id=?''', (layout_asset_id,)).fetchone()
            if is_asset_in_layout != None:
                asset_layout_id = is_asset_in_layout[0]
                layout_asset = self.Asset(self, asset_layout_id, get_infos_from_id=True)
                self.associated_layout_scene = layout_asset.full_path



        # Set favorite button state
        selected_asset_publish = self.cursor.execute('''SELECT asset_id FROM assets WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_type=? AND asset_version="out"''', (self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, self.selected_asset.type,)).fetchone()
        if not selected_asset_publish == None:
            selected_asset_publish_id = selected_asset_publish[0]
        else:
            selected_asset_publish_id = 0

        is_asset_favorited = self.cursor.execute('''SELECT * FROM favorited_assets WHERE asset_id=? AND member=?''', (selected_asset_publish_id, self.username,)).fetchone()
        if is_asset_favorited == None:
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        else:
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.favorite_icon)

        # Set publish icon to enabled
        self.publishBtn.setIcon(self.publish_icon)

        # Set create new version icon to enabled
        self.createVersionBtn.setIcon(self.new_version_icon)

        # Set load asset icon to enabled
        self.loadAssetBtn.setIcon(self.load_asset_icon)

        # Set last publish comment
        publish_comments = self.cursor.execute('''SELECT publish_time, publish_comment, publish_creator FROM publish_comments WHERE asset_id=?''', (self.selected_asset.id,)).fetchall()
        comments = ""
        for comment in reversed(publish_comments):
            publish_time = comment[0]
            publish_comment = comment[1]
            publish_creator = comment[2]
            comments += u"{0} (by {1}): {2}\n\n".format(publish_time, self.members[publish_creator], publish_comment)

        self.lastPublishComment.setText(comments)

        # Load comments
        self.CommentWidget.load_comments(self)

        # Set last publish label
        if self.selected_asset.type not in ["cmp", "lay", "shd", "hipnc", "sim", "anm"] and self.selected_asset.extension not in ["hipnc"]:
            asset_published = self.Asset(self, self.selected_asset.dependency, get_infos_from_id=True)
            self.update_last_published_time_lbl(asset_published)

        # Scroll to selected item
        self.versionList.scrollToItem(self.versionList.selectedItems()[0])

    def update_last_published_time_lbl(self, asset_published=None):

        # Set last published date label
        day_today = datetime.now()
        number_of_days_since_last_publish = day_today - asset_published.last_publish_as_date
        number_of_days_since_last_publish = number_of_days_since_last_publish.days

        self.lastPublishedLbl.setStyleSheet("color: #3c3c3c;")
        if number_of_days_since_last_publish == 0:
            number_of_days_since_last_publish = "today"
        else:
            number_of_days_since_last_publish = str(number_of_days_since_last_publish) + " days ago"

        publish_from_version_asset_id = asset_published.publish_from_version
        publish_from_version = self.cursor.execute('''SELECT asset_version FROM assets WHERE asset_id=?''', (publish_from_version_asset_id,)).fetchone()
        if publish_from_version == None or publish_from_version == "":
            publish_from_version = "01"
        else:
            publish_from_version = publish_from_version[0]
        self.lastPublishedLbl.setText("Last published by: {0} ({1}) from version {2}".format(asset_published.last_publish, number_of_days_since_last_publish, publish_from_version, ))

    def versionList_DoubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_asset.full_path))

    def load_assets_from_selected_seq_shot_dept(self):
        # Hide all versions
        [version.setHidden(True) for version in self.versions]

        # Unhide all assets
        [asset.setHidden(False) for asset in self.assets.values()]
        for asset, asset_item in self.assets.items():
            if "-lowres" in asset.name:
                asset_name = asset.name.replace("-lowres", "")
            else:
                asset_name = asset.name
            asset_item.setText(asset_name)

            if self.selected_sequence_name == "xxx" and self.selected_department_name == "xxx":
                asset_item.setText(asset_name + " (" + asset.type + ")")
                asset_item.setHidden(False)

            elif self.selected_sequence_name == "xxx" and self.selected_department_name != "xxx":
                if asset.shot != self.selected_shot_number and self.selected_shot_number != "xxxx":
                    asset_item.setHidden(True)

                if asset.type != self.selected_department_name:
                    asset_item.setHidden(True)

                # If asset is a houdini modeling, only show it when user clicks on modeling dep and not on layout
                if self.selected_department_name == "mod" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
                    asset_item.setHidden(False)
                elif self.selected_department_name == "lay" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
                    asset_item.setHidden(True)


            elif self.selected_sequence_name != "xxx" and self.selected_department_name == "xxx":
                asset_item.setText(asset_name + " (" + asset.type + ")")
                if asset.sequence != self.selected_sequence_name:
                    asset_item.setHidden(True)

                if asset.shot != self.selected_shot_number and self.selected_shot_number != "xxxx":
                    asset_item.setHidden(True)

                # If asset is a houdini modeling, only show it when user clicks on modeling dep and not on layout
                if self.selected_department_name == "mod" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
                    asset_item.setHidden(False)
                elif self.selected_department_name == "lay" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
                    asset_item.setHidden(True)

            elif self.selected_sequence_name != "xxx" and self.selected_department_name != "xxx":
                if asset.sequence != self.selected_sequence_name:
                    asset_item.setHidden(True)

                if asset.shot != self.selected_shot_number and self.selected_shot_number != "xxxx":
                    asset_item.setHidden(True)

                if asset.type != self.selected_department_name:
                    asset_item.setHidden(True)

                # If asset is a houdini modeling, only show it when user clicks on modeling dep and not on layout
                if self.selected_department_name == "mod" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
                    asset_item.setHidden(False)
                elif self.selected_department_name == "lay" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
                    asset_item.setHidden(True)

    def filterList_textChanged(self):
        asset_filter_str = str(self.assetFilter.text())
        if asset_filter_str > 0:
            for i in xrange(0, self.assetList.count()):

                asset = self.assetList.item(i).data(QtCore.Qt.UserRole).toPyObject()

                if "*" in asset_filter_str:
                    asset_filter_str = asset_filter_str.replace("*", ".*").lower()
                    r = re.compile(asset_filter_str)
                    if not r.match(asset.name.lower()):
                        self.assetList.setItemHidden(self.assetList.item(i), True)
                    else:
                        self.assetList.setItemHidden(self.assetList.item(i), False)
                else:
                    if not asset_filter_str.lower() in asset.name.lower():
                        self.assetList.setItemHidden(self.assetList.item(i), True)
                    else:
                        self.assetList.setItemHidden(self.assetList.item(i), False)

    def filter_assets_by_id(self):
        if len(str(self.filterAssetsById.text())) > 0:
            for asset, asset_item in self.assets.items():
                if str(asset.id) == str(self.filterAssetsById.text()):
                    asset_item.setHidden(False)
                    asset_item.setSelected(True)
                    self.assetList_Clicked()
                else:
                    asset_item.setHidden(True)
        else:
            self.load_assets_from_selected_seq_shot_dept()

    def create_new_version(self):

        # If selected version is "out", cancel
        if self.selected_asset.version == "out":
            self.Lib.message_box(self, text="You can't create a new version from a published asset")
            return

        # Ask if user is sure to create new version
        result = self.Lib.message_box(self, type="warning", text="Do you really want to create a new version?", no_button=True, yes_button_text="Yes", window_title="Are you sure?")
        if result == 0:
            return

        # Increment version number
        old_version_path = self.selected_asset.full_path
        new_version = str(int(self.selected_asset.version) + 1).zfill(2)
        old_version_thumbnail = self.selected_asset.default_media_user
        new_version_thumbnail = old_version_thumbnail.replace("_{0}_".format(self.selected_asset.version), "_{0}_".format(new_version))

        # Create new version asset
        asset = self.Asset(self, 0, self.selected_asset.project, self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, "", self.selected_asset.extension, self.selected_asset.type, new_version, self.selected_asset.tags, self.selected_asset.dependency, self.selected_asset.last_access, self.selected_asset.last_publish, self.selected_asset.creator, self.selected_asset.number_of_publishes)
        asset.add_asset_to_db()

        # Handle texture asset version creation
        if self.selected_asset.type == "tex":
            # Get path of selected texture asset folder
            texture_project_path = self.Lib.get_mari_project_path_from_asset_name(self, self.selected_asset.name, self.selected_asset.version)
            # Switch cache directory location to user H
            self.Lib.switch_mari_cache(self, "home")
            # Remove folder if it already exists
            if os.path.isdir("H:/mari_cache_tmp_synthese/" + texture_project_path):
                shutil.rmtree("H:/mari_cache_tmp_synthese/" + texture_project_path)
            # Copy texture asset folder from Z to H
            shutil.copytree("Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + texture_project_path, "H:/mari_cache_tmp_synthese/" + texture_project_path)

            # Start mari process
            self.mari_process = QtCore.QProcess(self)
            self.mari_process.waitForFinished()
            self.mari_process.readyRead.connect(self.mari_process_read_data)
            self.mari_process.finished.connect(partial(self.create_new_tex_version_finished, texture_project_path, asset))
            self.mari_process.start(self.mari_path, ["-t", self.cur_path + "\\lib\\software_scripts\\mari_create_new_version.py"])
            return

        if self.selected_asset.type == "sim":
            new_version_number = str(int(self.selected_asset.version) + 1).zfill(2)
            new_version_path = self.selected_asset.full_path.replace("_" + self.selected_asset.version + ".", "_" + new_version_number + ".")

            # Create HDA for sim asset
            self.houdini_hda_process = QtCore.QProcess(self)
            self.houdini_hda_process.waitForFinished()
            self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_new_sim_version.py", self.selected_asset.name, new_version_number, self.selected_asset.full_path, new_version_path])

        else:
            # Create new scene file, if it fails, remove asset from database and warn user.
            try:
                shutil.copy(old_version_path, asset.full_path)
            except:
                asset.remove_asset_from_db()
                self.Lib.message_box(self, type="error", text="Couldn't create new version, an error occured.")
                return

            # Create new version thumbnail from previous version thumbnail
            shutil.copy(old_version_thumbnail, new_version_thumbnail)

        # Add item to version list
        version_item = QtGui.QListWidgetItem(asset.version + " (" + asset.extension + ")")
        version_item.setData(QtCore.Qt.UserRole, asset)
        version_item.setIcon(QtGui.QIcon(asset.default_media_user))
        self.versions.append(version_item)
        self.versionList.addItem(version_item)
        self.versionList.setItemSelected(version_item, True)
        self.versionList_Clicked()

    def create_new_tex_version_finished(self, existing_project_path, asset):
        self.mari_process.kill()

        # Remove folder for current version of texture asset
        shutil.rmtree("H:/mari_cache_tmp_synthese/" + existing_project_path)

        # Get folder path of new texture asset version
        paths = glob("H:/mari_cache_tmp_synthese/*")
        paths = [i.replace("\\", "/") for i in paths]
        paths = [i for i in paths if not "SINGLE" in i and not "Generic" in i]

        # Copy folder of new texture asset version back to the tex folder
        shutil.move(paths[0], "Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + paths[0].split("/")[-1])

        # Add item to version list
        version_item = QtGui.QListWidgetItem(asset.version + " (" + asset.extension + ")")
        version_item.setData(QtCore.Qt.UserRole, asset)
        self.versions.append(version_item)
        self.versionList.addItem(version_item)
        self.versionList.setItemSelected(version_item, True)
        self.versionList_Clicked()

        self.Lib.message_box(self, type="info", text="New version successfully created!")

    def remove_version(self):
        # Confirm dialog
        confirm_dialog = QtGui.QMessageBox()
        reply = confirm_dialog.question(self, 'Delete selected version', "Are you sure ?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        self.Lib.apply_style(self, confirm_dialog)
        if reply != QtGui.QMessageBox.Yes:
            return

        # Set assetList item icon to current version's icon
        selected_version = self.versionList.selectedItems()[0]
        self.selected_asset = selected_version.data(QtCore.Qt.UserRole).toPyObject()
        last_version_thumb = self.selected_asset.default_media_user.replace("_{0}_".format(self.selected_asset.version), "_{0}_".format(str(int(self.selected_asset.version) - 1).zfill(2)))
        assetList_item = self.assetList.selectedItems()[0]
        assetList_item.setIcon(QtGui.QIcon(last_version_thumb))

        self.selected_asset.remove_asset_from_db()
        for item in self.versionList.selectedItems():
            self.versionList.takeItem(self.versionList.row(item))

        self.versionList_Clicked()

    def publish_asset(self):

        self.blockSignals(True)

        self.no_gui = False
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.no_gui = True
        else:
            self.no_gui = False

        self.selected_asset_type = self.selected_asset.type

        if self.no_gui == False:
            # Publish comment GUI
            dialog = QtGui.QDialog(self)
            dialog.setWindowTitle("Add a comment")
            self.Lib.apply_style(self, dialog)

            dialog_layout = QtGui.QVBoxLayout(dialog)

            publish_comment_line_edit = QtGui.QLineEdit(dialog)

            status_combobox = QtGui.QComboBox()
            status_combobox.insertItems(0, QtCore.QStringList(["N/A", "Waiting to Start", "Ready to Start", "On Hold", "Retake", "In Progress", "Pending Review", "CBB", "Final"]))


            # Fetch shotgun task status
            pipeline_steps = {"mod": "Modeling", "shd": "Shading", "tex": "Texturing", "lay": "Layout"}

            project = self.sg.find_one("Project", [["id", "is", self.sg_project_id]])
            asset = self.sg.find_one("Asset", [["code", "is", self.selected_asset.name], ["project", "is", project]])
            step = self.sg.find_one("Step", [["code", "is", pipeline_steps[self.selected_asset.type]]])
            task = self.sg.find_one("Task", [["entity", "is", asset], ["step", "is", step]], ["sg_status_list", "id"])

            if task["sg_status_list"] == "na":
                status_combobox.setCurrentIndex(0)
            elif task["sg_status_list"] == "wtg":
                status_combobox.setCurrentIndex(1)
            elif task["sg_status_list"] == "rdy":
                status_combobox.setCurrentIndex(2)
            elif task["sg_status_list"] == "hld":
                status_combobox.setCurrentIndex(3)
            elif task["sg_status_list"] == "rtk":
                status_combobox.setCurrentIndex(4)
            elif task["sg_status_list"] == "ip":
                status_combobox.setCurrentIndex(5)
            elif task["sg_status_list"] == "rev":
                status_combobox.setCurrentIndex(6)
            elif task["sg_status_list"] == "cbb":
                status_combobox.setCurrentIndex(7)
            elif task["sg_status_list"] == "fin":
                status_combobox.setCurrentIndex(8)
            else:
                status_combobox.setCurrentIndex(9)

            publish_accept_btn = QtGui.QPushButton("Publish asset!", dialog)
            publish_comment_line_edit.returnPressed.connect(dialog.accept)
            publish_accept_btn.clicked.connect(dialog.accept)

            dialog_layout.addWidget(publish_comment_line_edit)
            dialog_layout.addWidget(status_combobox)
            dialog_layout.addWidget(publish_accept_btn)
            dialog.exec_()

            if dialog.result() == 0:
                self.publish_comment = ""
                return
            self.publish_comment = unicode(self.utf8_codec.fromUnicode(publish_comment_line_edit.text()), 'utf-8')
            self.changed_status = status_combobox.currentText()

            if self.changed_status == "On Hold":
                #create note dialog

                dialog = QtGui.QDialog(self)
                dialog.setWindowTitle("Add a note")
                self.Lib.apply_style(self, dialog)

                dialog_layout = QtGui.QVBoxLayout(dialog)

                note_comment_line_edit = QtGui.QLineEdit(dialog)
                note_comment_line_edit.returnPressed.connect(dialog.accept)

                dialog_layout.addWidget(note_comment_line_edit)
                dialog.exec_()

                if dialog.result() == 0:
                    return

                asset = self.sg.find_one("Asset", [["code", "is", self.selected_asset.name]])
                sg_user = self.sg.find_one('HumanUser', [['login', 'is', self.sg_members[self.username]]])
                data = {'project': {'type': 'Project', 'id': self.sg_project_id}, 'note_links': [asset], 'user': sg_user, 'content': unicode(self.utf8_codec.fromUnicode(note_comment_line_edit.text()), 'utf-8'), 'subject': self.members[self.username] + "'s Note on " + self.selected_asset.name}
                self.sg.create("Note", data)
                self.sg.update("Task", task["id"], {'sg_status_list': "hld"})
            elif self.changed_status == "Waiting to Start":
                self.sg.update("Task", task["id"], {'sg_status_list': "wtg"})
            elif self.changed_status == "Ready to Start":
                self.sg.update("Task", task["id"], {'sg_status_list': "rdy"})
            elif self.changed_status == "Retake":
                self.sg.update("Task", task["id"], {'sg_status_list': "rtk"})
            elif self.changed_status == "In Progress":
                self.sg.update("Task", task["id"], {'sg_status_list': "ip"})
            elif self.changed_status == "Pending Review":
                self.sg.update("Task", task["id"], {'sg_status_list': "rev"})
            elif self.changed_status == "CBB":
                self.sg.update("Task", task["id"], {'sg_status_list': "cbb"})
            elif self.changed_status == "Final":
                self.sg.update("Task", task["id"], {'sg_status_list': "fin"})
            elif self.changed_status == "N/A":
                self.sg.update("Task", task["id"], {'sg_status_list': "na"})

            # Add publish comment to database
            self.cursor.execute('''INSERT INTO publish_comments(asset_id, publish_comment, publish_time, publish_creator) VALUES(?,?,?,?)''', (self.selected_asset.id, self.publish_comment, datetime.now().strftime("%d/%m/%Y at %H:%M"), self.username))
            self.db.commit()

        # Update last publish time
        self.selected_asset.change_last_publish()

        if self.selected_asset.type == "mod":
            self.publish_process = QtCore.QProcess(self)
            self.publish_process.finished.connect(self.publish_process_finished)

            if self.selected_asset.extension == "blend":
                self.publish_process.start(self.blender_path, ["-b", "-P", self.cur_path + "\\lib\\software_scripts\\blender_export_obj_from_scene.py", "--", self.selected_asset.full_path, self.selected_asset.obj_path.replace("\\", "/")])
            elif self.selected_asset.extension == "ma":
                self.publish_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_export_obj_from_scene.py", self.selected_asset.full_path, self.selected_asset.obj_path.replace("\\", "/")])
            elif self.selected_asset.extension == "scn":
                self.publish_process.start(self.softimage_batch_path, ["-processing", "-script", self.cur_path + "\\lib\\software_scripts\\softimage_export_obj_from_scene.py", "-main", "export_obj", "-args", "-file_path", self.selected_asset.full_path, "-export_path", self.selected_asset.obj_path.replace("\\", "/")])
            elif self.selected_asset.extension == "hda":
                self.publish_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_export_mod_from_mod.py", self.selected_asset.full_path])

            self.cursor.execute('''UPDATE assets SET publish_from_version=? WHERE asset_path=?''', (self.selected_asset.id, self.selected_asset.obj_path.replace("\\", "/").replace(self.selected_project_path, ""),))
            self.db.commit()

        elif self.selected_asset.type == "rig":
            shutil.copy2(self.selected_asset.full_path, self.selected_asset.rig_out_path)

            self.cursor.execute('''UPDATE assets SET publish_from_version=? WHERE asset_path=?''', (self.selected_asset.id, self.selected_asset.rig_out_path.replace(self.selected_project_path, ""),))
            self.db.commit()

            self.publish_process_finished()

        elif self.selected_asset.type == "tex":
            self.screenshot_is_ok = False
            self.cancel_screenshot = False
            while self.screenshot_is_ok == False:
                self.Lib.take_screenshot(self, path=self.selected_asset.full_media, software="mari")
                self.Lib.compress_image(self, image_path=self.selected_asset.full_media, width=700, quality=100)

                self.screenshot_dialog = QtGui.QDialog()
                self.screenshot_dialog.setWindowTitle("Preview")
                self.screenshot_dialog.setMaximumSize(700, 700)
                self.Lib.apply_style(self, self.screenshot_dialog)

                image = QtGui.QImage(self.selected_asset.full_media)
                pixmap = QtGui.QPixmap.fromImage(image)
                pixmap = pixmap.scaled(700, 700, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
                label = QtGui.QLabel()
                label.setPixmap(pixmap)
                correctLbl = QtGui.QLabel("Is this screenshot okay?")
                correctBtn = QtGui.QPushButton()
                correctBtn.setText("Yes")
                notcorrectBtn = QtGui.QPushButton()
                notcorrectBtn.setText("Nope :( Try Again!")
                closeBtn = QtGui.QPushButton()
                closeBtn.setText("Cancel publish")

                correctBtn.clicked.connect(self.set_screenshot_variable_to_true)
                notcorrectBtn.clicked.connect(self.set_screenshot_variable_to_false)
                closeBtn.clicked.connect(self.set_screenshot_variable_to_false_and_exit)

                layout = QtGui.QVBoxLayout(self.screenshot_dialog)

                layout.addWidget(label)
                layout.addWidget(correctLbl)
                layout.addWidget(correctBtn)
                layout.addWidget(notcorrectBtn)
                layout.addWidget(closeBtn)

                self.screenshot_dialog.resize(700, 700)
                self.screenshot_dialog.exec_()

            if self.cancel_screenshot == True:
                return

            # Upload thumbnail to Shotgun
            sg_asset = self.sg.find_one("Asset", [["code", "is", self.selected_asset.name]])
            self.sg.upload_thumbnail("Asset", sg_asset["id"], self.selected_asset.full_media)

            # Create new shotgun version
            sg_user = self.sg.find_one('HumanUser', [['login', 'is', self.sg_members[self.username]]])

            project = self.sg.find_one("Project", [["id", "is", self.sg_project_id]])
            sg_version = self.sg.find('Version', [["code", "contains", self.selected_asset.name + "_"], ["project", "is", project]], ["code"])
            versions = [version["code"] for version in sg_version]

            if len(versions) == 0:
                last_version_number = "0001"
            else:
                last_version = sorted(versions)[-1]
                last_version_number = str(int(last_version.split("_")[-1]) + 1).zfill(4)

            data = {
                'project': {'type': 'Project', 'id': self.sg_project_id},
                'code': self.selected_asset.name + "_" + last_version_number,
                'entity': sg_asset,
                'description': self.publish_comment,
                'user': sg_user,
                'sg_path_to_movie': self.selected_asset.full_media,
                'image': self.selected_asset.full_media}

            version = self.sg.create("Version", data)
            self.sg.upload("Version", version["id"], self.selected_asset.full_media.replace("\\", "/"), "sg_uploaded_movie")

            self.load_all_assets_for_first_time()
            self.load_assets_from_selected_seq_shot_dept()
            self.Lib.message_box(self, type="info", text="Successfully published texture asset!")

        elif self.selected_asset.type == "shd":

            selected_asset = self.selected_asset.name

            self.publish_process = QtCore.QProcess(self)
            self.publish_process.readyRead.connect(self.shading_render_progress)
            self.publish_process.finished.connect(partial(self.publish_process_finished, selected_asset))

            self.statusLbl.setText("Status: Rendering shading thumbnail with Mantra. Please wait...")
            self.publish_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_render_from_asset.py", self.selected_asset.full_path])

            self.cursor.execute('''UPDATE assets SET publish_from_version=? WHERE asset_path=?''', (self.selected_asset.id, self.selected_asset.rig_out_path.replace(self.selected_project_path, ""),))
            self.db.commit()

        elif self.selected_asset.type == "anm":
            # Get frame range from selected shot
            sequence = self.sg.find_one("Sequence", [["code","is",self.selected_asset.sequence]])
            shot_id = self.sg.find_one("Shot", [["sg_sequence","is",sequence],["code","is",self.selected_asset.shot]], ["id"])
            sg_cut_in = self.sg.find_one("Shot", [["id", "is", shot_id["id"]]], ["sg_cut_in"])
            sg_cut_out = self.sg.find_one("Shot", [["id", "is", shot_id["id"]]], ["sg_cut_out"])
            start_frame = sg_cut_in["sg_cut_in"]
            end_frame = sg_cut_out["sg_cut_out"]


            self.publish_process = QtCore.QProcess(self)
            self.publish_process.finished.connect(self.publish_process_finished)
            self.publish_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_export_anm_as_alembic.py", self.selected_asset.full_path.replace("\\", "/"), self.selected_asset.anim_out_path.replace("\\", "/"), str(start_frame), str(end_frame)])

            self.cursor.execute('''UPDATE assets SET publish_from_version=? WHERE asset_path=?''', (self.selected_asset.id, self.selected_asset.anim_out_path.replace(self.selected_project_path, ""),))
            self.db.commit()

        elif self.selected_asset.type == "cam":
            # Get frame range from selected shot
            sequence = self.sg.find_one("Sequence", [["code", "is", self.selected_asset.sequence]])
            shot_id = self.sg.find_one("Shot", [["sg_sequence", "is", sequence], ["code", "is", self.selected_asset.shot]], ["id"])
            sg_cut_in = self.sg.find_one("Shot", [["id", "is", shot_id["id"]]], ["sg_cut_in"])
            sg_cut_out = self.sg.find_one("Shot", [["id", "is", shot_id["id"]]], ["sg_cut_out"])
            start_frame = sg_cut_in["sg_cut_in"]
            end_frame = sg_cut_out["sg_cut_out"]

            export_path = str(self.selected_asset.full_path.replace("_" + self.selected_asset.version + ".", "_out.").replace(".hda", ".abc").replace("\\", "/"))
            hda_path = str(self.selected_asset.full_path.replace("\\", "/"))
            camera_name = str(self.selected_asset.name)

            layout_asset = self.Asset(self, self.selected_asset.dependency, get_infos_from_id=True)

            self.publish_process = QtCore.QProcess(self)
            self.publish_process.finished.connect(self.publish_process_finished)
            self.publish_process.waitForFinished()
            self.publish_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_export_cam_from_lay.py", export_path, layout_asset.full_path, camera_name, start_frame, end_frame])

    def publish_process_finished(self, selected_asset=""):

        # Check if current asset has been favorited by someone.
        favorited_by = self.cursor.execute('''SELECT member FROM favorited_assets WHERE asset_id=?''', (self.selected_asset.id,)).fetchall()
        if favorited_by != None:
            favorited_by = [i[0] for i in favorited_by]
        else:
            favorited_by = []


        # Add log entry saying that the asset has been published.
        log_entry = self.LogEntry(self, 0, self.selected_asset.id, [], favorited_by, self.username, "", "publish", "{0} has published a new version of asset {1} ({2}).".format(self.members[self.username], self.selected_asset.name, self.departments_longname[self.selected_asset.type]), datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()

        if self.selected_asset_type == "mod" and not "lowres" in self.selected_asset.name:
            # Normalize modeling scale
            self.normalize_mod_scale_process = QtCore.QProcess(self)
            self.normalize_mod_scale_process.waitForFinished()
            self.normalize_mod_scale_process.finished.connect(self.normalize_modeling_finished)
            self.normalize_mod_scale_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_normalize_scale.py", self.selected_asset.obj_path.replace("\\", "/")])
        elif self.selected_asset_type == "shd":
            img_filename = "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/shd/.thumb/" + selected_asset + "_01_full.jpg"
            thumb_filename = "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/shd/.thumb/" + selected_asset + "_01_full-thumb.jpg"

            # Create thumbnail
            shutil.copy(img_filename, thumb_filename)
            self.compress_image(thumb_filename, 240, 70)

            # Upload thumbnail to Shotgun
            sg_asset = self.sg.find_one("Asset", [["code", "is", selected_asset]])
            self.sg.upload_thumbnail("Asset", sg_asset["id"], img_filename)

            # Create new shotgun version
            sg_user = self.sg.find_one('HumanUser', [['login', 'is', self.sg_members[self.username]]])

            project = self.sg.find_one("Project", [["id", "is", self.sg_project_id]])
            sg_version = self.sg.find('Version', [["code", "contains", selected_asset + "_"], ["project", "is", project]], ["code"])
            versions = [version["code"] for version in sg_version]

            if len(versions) == 0:
                last_version_number = "0001"
            else:
                try:
                    last_version = sorted(versions)[-1]
                    last_version_number = str(int(last_version.split("_")[-1]) + 1).zfill(4)
                except:
                    last_version_number = "xxxx"

            data = {
                'project': {'type': 'Project', 'id': self.sg_project_id},
                'code': selected_asset + "_" + last_version_number,
                'entity': sg_asset,
                'description': self.publish_comment,
                'user': sg_user,
                'sg_path_to_movie': img_filename,
                'image': img_filename}

            version = self.sg.create("Version", data)
            self.sg.upload("Version", version["id"], img_filename.replace("\\", "/"), "sg_uploaded_movie")
            self.Lib.message_box(self, type="info", text="Successfully published shading asset!")

        else:
            self.statusLbl.setText("Status: Publish finished, now updating thumbnails.")
            if self.no_gui == False:
                if self.selected_asset_type != "rig":
                    self.update_thumbnail(False)

        self.statusLbl.setText("Status: Idle...")
        self.blockSignals(False)

    def set_screenshot_variable_to_true(self):
        self.screenshot_is_ok = True
        self.screenshot_dialog.close()

    def set_screenshot_variable_to_false(self):
        self.screenshot_is_ok = False
        self.screenshot_dialog.close()

    def set_screenshot_variable_to_false_and_exit(self):
        self.screenshot_is_ok = True
        self.cancel_screenshot = True
        self.screenshot_dialog.close()

    def shading_render_progress(self):
        while self.publish_process.canReadLine():
            print(self.publish_process.readLine())

    def normalize_modeling_finished(self):
        self.versionList_Clicked()
        self.update_thumbnail(False)

    def update_thumbnail(self, ask_window=True, batch_update=False):
        if self.no_gui == True:
            self.Lib.message_box(self, type="info", text="Successfully published asset!")
            return

        if self.selected_asset.type == "mod":
            if ask_window:
                dialog = QtGui.QDialog(self)
                dialog.setWindowTitle("Select options")
                dialog_main_layout = QtGui.QVBoxLayout(dialog)

                checkbox_full = QtGui.QCheckBox("Single image (Full Resolution Render)", dialog)
                if not os.path.isfile(self.selected_asset.full_media):  # If full don't exist, set checkbox to true
                    checkbox_full.setCheckState(2)
                checkbox_turn = QtGui.QCheckBox("Turntable (video)", dialog)
                if not os.path.isfile(self.selected_asset.advanced_media):  # If turn don't exist, set checkbox to true
                    checkbox_turn.setCheckState(2)

                create_btn = QtGui.QPushButton("Start!", dialog)
                create_btn.clicked.connect(dialog.accept)

                dialog_main_layout.addWidget(checkbox_full)
                dialog_main_layout.addWidget(checkbox_turn)
                dialog_main_layout.addWidget(create_btn)

                dialog.exec_()

                if dialog.result() == 0:
                    return

                thumbs_to_create = ""
                if checkbox_full.isChecked():
                    thumbs_to_create += "full"
                if checkbox_turn.isChecked():
                    thumbs_to_create += "turn"
            else:
                thumbs_to_create = "full"

            self.create_thumbnails(self.selected_asset.obj_path, thumbs_to_create, self.selected_asset.version)

        elif self.selected_asset.type == "anm":

            anim_has_camera = self.cursor.execute('''SELECT has_camera FROM camera_in_anim WHERE asset_id=?''', (self.selected_asset.id,)).fetchone()
            if anim_has_camera == None:
                return

            shots = (self.cursor.execute('''SELECT frame_start, frame_end FROM shots WHERE project_name=? AND sequence_name=? AND shot_number=?''', (self.selected_project_name, self.selected_asset.sequence, self.selected_asset.shot,))).fetchall()
            start_frame = str(shots[0][0])
            end_frame = str(shots[0][1])
            self.i = 0
            self.thumbnailProgressBar.show()
            self.thumbnailProgressBar.setMaximum(int(end_frame) - int(start_frame))
            self.thumbnailProgressBar.setValue(0)
            asset = self.selected_asset

            self.update_thumb_process = QtCore.QProcess(self)
            self.update_thumb_process.finished.connect(partial(self.create_mov_from_playblast, start_frame, end_frame, asset))
            self.update_thumb_process.readyRead.connect(self.update_thumb_ready_read)
            self.update_thumb_process.waitForFinished()
            self.update_thumb_process.start("C:/Program Files/Autodesk/Maya2015/bin/Render.exe", ["-r", "hw2", "-s", start_frame, "-e", end_frame, self.selected_asset.full_path])

        elif self.selected_asset.type == "cam":
            associated_hip_scene = self.cursor.execute('''SELECT asset_path FROM assets WHERE asset_id=?''', (self.selected_asset.dependency,)).fetchone()[0]
            associated_hip_scene = self.selected_project_path + associated_hip_scene

            shots = (self.cursor.execute('''SELECT frame_start, frame_end FROM shots WHERE project_name=? AND sequence_name=? AND shot_number=?''', (self.selected_project_name, self.selected_asset.sequence, self.selected_asset.shot,))).fetchall()
            start_frame = str(shots[0][0])
            end_frame = str(shots[0][1])
            self.i = 0
            self.thumbnailProgressBar.show()
            self.thumbnailProgressBar.setMaximum(20)
            self.thumbnailProgressBar.setValue(0)
            asset = self.selected_asset

            self.update_thumb_process = QtCore.QProcess(self)
            self.update_thumb_process.finished.connect(partial(self.create_mov_from_flipbook, start_frame, end_frame, asset))
            self.update_thumb_process.readyRead.connect(self.update_thumb_ready_read)
            self.update_thumb_process.waitForFinished()
            self.update_thumb_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_flipbook.py", associated_hip_scene, self.selected_asset.name, start_frame, end_frame])

        elif self.selected_asset.type == "shd":
            self.i = 0
            self.thumbnailProgressBar.show()
            self.thumbnailProgressBar.setMaximum(250)
            self.thumbnailProgressBar.setValue(0)
            asset = self.Asset(self, self.selected_asset.dependency, get_infos_from_id=True)

            self.update_thumb_process = QtCore.QProcess(self)
            self.update_thumb_process.finished.connect(partial(self.create_mov_from_turn, self.selected_asset))
            self.update_thumb_process.readyRead.connect(self.update_thumb_ready_read)
            self.update_thumb_process.waitForFinished()
            if self.batch_thumbnail == True:
                process = subprocess.Popen([self.houdini_batch_path, self.cur_path + "\\lib\\software_scripts\\houdini_create_render_from_asset.py", self.cur_path + "/lib/software_scripts/houdini_turn_render/turn_render.hipnc", asset.full_path, asset.name])
                process.wait()
                self.create_mov_from_turn(self.selected_asset)
            else:
                self.update_thumb_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_render_from_asset.py", self.cur_path + "/lib/software_scripts/houdini_turn_render/turn_render.hipnc", asset.full_path, asset.name])

        elif self.selected_asset.type == "rig":
            self.Lib.take_screenshot(self, path=self.selected_asset.first_media)
            self.Lib.compress_image(self, image_path=self.selected_asset.first_media, width=700, quality=100)

        elif self.selected_asset.type == "tex":
            self.Lib.take_screenshot(self, path=self.selected_asset.full_media, software="mari")
            self.Lib.compress_image(self, image_path=self.selected_asset.full_media, width=700, quality=100)

        elif self.selected_asset.type == "lay":
            self.Lib.take_screenshot(self, path=self.selected_asset.first_media)
            self.Lib.compress_image(self, image_path=self.selected_asset.first_media, width=700, quality=100)

    def create_mov_from_playblast(self, start_frame, end_frame, asset):
        file_sequence = "H:/" + asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + ".%04d.jpg"
        movie_path = "H:/" + asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "_full.mp4"

        subprocess.call([self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-r", "24", "-start_number", start_frame, "-i", file_sequence, "-vcodec", "libx264", "-y", "-r", "24", movie_path])

        thumb_filename = os.path.split(asset.full_path)[0] + "\\.thumb\\" + asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "_advanced.mp4"
        shutil.copy(movie_path, thumb_filename)

        os.remove(movie_path)
        for i in range(int(start_frame), int(end_frame) + 1):
            if i == int(start_frame):
                thumbnail_first_frame = os.path.split(asset.full_path)[0] + "\\.thumb\\" + asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "_full.jpg"
                shutil.copy("H:/" + asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "." + str(i).zfill(4) + ".jpg", thumbnail_first_frame)
                self.Lib.squarify_image(self, image_path=thumbnail_first_frame)
            os.remove("H:/" + asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "." + str(i).zfill(4) + ".jpg")

        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())
        self.thumbnailProgressBar.hide()
        self.blockSignals(True)
        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()
        self.blockSignals(False)
        self.Lib.message_box(self, type="info", text="Successfully created playblast!")

    def create_mov_from_flipbook(self, start_frame, end_frame, asset):
        file_sequence = "H:/tmp/playblast.%04d.jpg"
        movie_path = "H:/tmp/" + asset.path.replace("\\assets\\cam\\", "").replace(".hda", "") + "_full.mp4"

        subprocess.call([self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-start_number", start_frame, "-i", file_sequence, "-vcodec", "libx264", "-y", "-r", "24", movie_path])

        movie_output_path = os.path.split(asset.full_path)[0] + "\\.thumb\\" + asset.path.replace("\\assets\\cam\\", "").replace(".hda", "") + "_advanced.mp4"
        shutil.copy(movie_path, movie_output_path)

        os.remove(movie_path)
        for i in range(int(start_frame), int(end_frame) + 1):
            if i == int(start_frame):
                thumb_first_frame = os.path.split(asset.full_path)[0] + "\\.thumb\\" + asset.path.replace("\\assets\\cam\\", "").replace(".hda", "") + "_full.jpg"
                shutil.copy("H:/tmp/playblast." + str(i).zfill(4) + ".jpg", thumb_first_frame)
                self.Lib.squarify_image(self, image_path=thumb_first_frame)
            os.remove("H:/tmp/playblast." + str(i).zfill(4) + ".jpg")

        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())
        self.thumbnailProgressBar.hide()

        self.blockSignals(True)
        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()
        self.blockSignals(False)

        self.Lib.message_box(self, type="info", text="Successfully created playblast!")

    def create_mov_from_turn(self, asset):
        all_files = glob("H:/tmp/*")
        all_files = [i.replace("\\", "/") for i in all_files if "turn_" in i]

        if len(all_files) > 24:
            turn_folder = os.path.split(asset.full_path)[0].replace("\\", "/") + "/.thumb/"  # Ex: H:\01-NAD\_pipeline\test_project_files\assets\shd\.turn
            filename_path = asset.path.replace("\\assets\\shd\\", "").replace(".hda", ".mp4")  # Ex: nat_xxx_xxxx_shd_flippy_01.mp4
            filename_path_geo = filename_path.replace(asset.name + "_" + asset.version, asset.name + "_" + asset.version + "_full")
            filename_path_hdr = filename_path.replace(asset.name + "_" + asset.version, asset.name + "_" + asset.version + "_advanced")
            movie_path_geo = (turn_folder + filename_path_geo).replace("\\", "/")
            movie_path_hdr = (turn_folder + filename_path_hdr).replace("\\", "/")

            subprocess.call([self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-i", "H:/tmp/turn_geo.%04d.jpg", "-vcodec", "libx264", "-y", "-r", "24", movie_path_geo])
            subprocess.call([self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-i", "H:/tmp/turn_hdr.%04d.jpg", "-vcodec", "libx264", "-y", "-r", "24", movie_path_hdr])

            for i, each_file in enumerate(all_files):
                if i == 3:
                    shutil.move(each_file, movie_path_geo.replace("_full.mp4", "_full.jpg"))
                else:
                    os.remove(each_file)


            self.blockSignals(True)
            self.load_all_assets_for_first_time()
            self.load_assets_from_selected_seq_shot_dept()
            self.blockSignals(False)



            if self.batch_thumbnail == True:
                pass
            else:
                self.Lib.message_box(self, type="info", text="Successfully created turntable!")
        else:
            if self.batch_thumbnail == True:
                pass
            else:
                self.Lib.message_box(self, type="info", text="Couldn't create turntable, there must be no shader...")


        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())
        self.thumbnailProgressBar.hide()

    def create_img_from_tex(self, asset):
        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())
        self.thumbnailProgressBar.hide()

        selected_version_item.setIcon(QtGui.QIcon(asset.default_media_user))
        selected_asset_item.setIcon(QtGui.QIcon(asset.default_media_user))

        self.Lib.message_box(self, type="info", text="Successfully created playblast!")

    def create_thumbnails(self, obj_path="", thumbs_to_create="", version=""):

        self.updateThumbBtn.setEnabled(False)
        self.full_obj_path = obj_path
        self.obj_name = obj_path.split("\\")[-1].split("_")[0]
        self.obj_tmp_path = "H:\\tmp\\" + obj_path.split("\\")[-1]
        self.type = type
        self.version = version
        self.i = 0

        self.thumbnailProgressBar.show()
        self.thumbnailProgressBar.setValue(0)

        self.thumbs_to_create = thumbs_to_create


        if "full" in self.thumbs_to_create:
            self.type = "full"
            if self.batch_thumbnail == True:
                self.sampling = 500
                self.resolution = 250
            else:
                self.sampling = 250
                self.resolution = 150
            self.thumbs_to_create = thumbs_to_create.replace("full", "")
        elif "turn" in self.thumbs_to_create:
            self.type = "turn"
            if self.batch_thumbnail == True:
                self.sampling = 150
                self.resolution = 150
            else:
                self.sampling = 50
                self.resolution = 100
            self.thumbs_to_create = thumbs_to_create.replace("turn", "")

        if self.type == "full":
            self.thumbnailProgressBar.setMaximum(67 + int(self.sampling))
        elif self.type == "turn":
            self.thumbnailProgressBar.setMaximum(1171 + (int(self.sampling) * 20))

        if os.path.getsize(self.full_obj_path) < 100:
            self.thumbnailProgressBar.hide()
            return

        if self.no_gui == True:
            self.thumbnailProgressBar.hide()
            self.updateThumbBtn.setEnabled(True)
            self.Lib.message_box(self, type="info", text="Successfully created thumbnails")
            return

        if self.batch_thumbnail == True:
            process = subprocess.Popen(["C:/Program Files/Blender Foundation/Blender/blender.exe", "-b", self.cur_path + "\\lib\\thumbnailer\\Thumbnailer.blend", "--python-text",
                                        "ThumbScript", self.full_obj_path, self.type, str(self.sampling),
                                        str(self.resolution), self.version
                                        ])
            process.wait()
            self.create_thumbnail_finished(version)
        else:
            self.create_thumbnail_process = QtCore.QProcess(self)
            self.create_thumbnail_process.readyReadStandardOutput.connect(self.create_thumbnail_new_data)
            self.create_thumbnail_process.setProcessChannelMode(QtCore.QProcess.SeparateChannels)
            self.create_thumbnail_process.finished.connect(partial(self.create_thumbnail_finished, version))
            self.create_thumbnail_process.start("C:/Program Files/Blender Foundation/Blender/blender.exe", ["-b", self.cur_path + "\\lib\\thumbnailer\\Thumbnailer.blend", "--python-text",
                                                                                                            "ThumbScript", self.full_obj_path, self.type, str(self.sampling),
                                                                                                            str(self.resolution), self.version
                                                                                                            ])

    def create_thumbnail_new_data(self):
        while self.create_thumbnail_process.canReadLine():
            self.i += 1
            out = self.create_thumbnail_process.readLine()
            self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.value() + 1)
            hue = self.fit_range(self.i, 0, self.thumbnailProgressBar.maximum(), 0, 76)
            self.thumbnailProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);}")

    def create_thumbnail_finished(self, version):
        img_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_full.jpg")
        thumb_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_full-thumb.jpg")
        if self.type == "full":
            filename = self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg")
            self.compress_image(filename, int(1920 * float(self.resolution) / 100), 100)

            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg"), img_filename)
            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg"), thumb_filename)
            os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg"))

            self.compress_image(thumb_filename, int(240 * float(self.resolution) / 100), 70)

        elif self.type == "turn":
            file_sequence = self.obj_tmp_path.replace("out.obj", self.version + "_%02d.jpg")
            movie_path = self.obj_tmp_path.replace("out.obj", self.version + "_advanced.mp4")
            subprocess.call([self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-i", file_sequence, "-vcodec", "libx264", "-b", "800k", "-crf", "0", "-y", "-r", "24", movie_path])

            turn_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_advanced.mp4")
            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_advanced.mp4"), turn_filename)
            os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_advanced.mp4"))
            for i in range(24):
                os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_" + str(i).zfill(2) + ".jpg"))

        try:
            self.create_thumbnail_process.kill()
        except:
            pass

        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())

        # Upload thumbnail to Shotgun
        sg_asset = self.sg.find_one("Asset", [["code", "is", self.obj_name]])
        self.sg.upload_thumbnail("Asset", sg_asset["id"], img_filename)

        # Create new shotgun version
        sg_user = self.sg.find_one('HumanUser', [['login', 'is', self.sg_members[self.username]]])

        project = self.sg.find_one("Project", [["id", "is", self.sg_project_id]])
        sg_version = self.sg.find('Version', [["code", "contains", self.obj_name + "_"], ["project","is",project]], ["code"])
        versions = [version["code"] for version in sg_version]

        if len(versions) == 0:
            last_version_number = "0001"
        else:
            try:
                last_version = sorted(versions)[-1]
                last_version_number = str(int(last_version.split("_")[-1]) + 1).zfill(4)
            except:
                last_version_number = ""

        data = {
            'project': {'type': 'Project', 'id': self.sg_project_id},
            'code': self.obj_name + "_" + last_version_number,
            'entity': sg_asset,
            'description': self.publish_comment,
            'user': sg_user,
            'sg_path_to_movie':img_filename,
            'image': img_filename}

        version = self.sg.create("Version", data)
        self.sg.upload("Version", version["id"], img_filename.replace("\\", "/"), "sg_uploaded_movie")

        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()
        self.versionList_Clicked()

        if len(self.thumbs_to_create) > 0:
            self.create_thumbnails(self.full_obj_path, self.thumbs_to_create, self.version)
        else:

            self.blockSignals(True)
            self.AssetLoader.load_all_assets_for_first_time(self)
            self.AssetLoader.load_assets_from_selected_seq_shot_dept(self)
            self.blockSignals(False)

            self.thumbnailProgressBar.hide()
            self.updateThumbBtn.setEnabled(True)
            if self.batch_thumbnail == True:
                pass
            else:
                self.message_box(type="info", text="Successfully created thumbnails")

    def update_thumb_ready_read(self):
        while self.update_thumb_process.canReadLine():
            self.i += 1
            self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.value() + 1)
            hue = self.fit_range(self.i, 0, self.thumbnailProgressBar.maximum(), 0, 76)
            self.thumbnailProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);}")
            out = self.update_thumb_process.readLine()
            print(out)

    def show_playblast(self):
        if self.selected_asset == None:
            return

        if self.selected_asset.type == "anm":
            subprocess.Popen(["H:/DJView/bin/djv_view.exe", self.selected_asset.anim_playblast_path])

        elif self.selected_asset.type == "cam":
            subprocess.Popen(["H:/DJView/bin/djv_view.exe", self.selected_asset.cam_playblast_path])

    def show_shd_turn(self, type):
        if self.selected_asset == None:
            return

        if type == "geo":
            subprocess.Popen(["H:/DJView/bin/djv_view.exe", self.selected_asset.turngeo_path])
        elif type == "hdr":
            subprocess.Popen(["H:/DJView/bin/djv_view.exe", self.selected_asset.turnhdr_path])

    def switch_thumbnail_display(self, type=""):
        if not self.selected_asset:
            return

        if type == "full":
            result = self.check_thumbnails_conditions(type="full")
            if result == True:
                qpixmap = QtGui.QPixmap(self.selected_asset.full_img_path)
                qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
                self.assetImg.setData(self.selected_asset.full_img_path)
                self.assetImg.setPixmap(qpixmap)

        elif type == "turn":
            result = self.check_thumbnails_conditions(type="turn")
            if result == True:
                subprocess.Popen(["H:/DJView/bin/djv_view.exe", self.selected_asset.turn_vid_path])

    def check_thumbnails_conditions(self, type=""):
        '''
        When user clicks on full, quad or turn to show given view, this function check if the asset has already been published at least once, if
        there is already a thumbnail or not, and if there's a new published version from which user can make a new thumbnail.
        '''
        if type == "full":
            path = self.selected_asset.full_img_path
            type_full_text = "full resolution image"
        elif type == "turn":
            path = self.selected_asset.turn_vid_path
            type_full_text = "turntable"


        # Asset has never been published, ask for first publish.
        publish_asset = self.Asset(self, self.selected_asset.dependency, get_infos_from_id=True)
        if publish_asset.number_of_publishes == 0:
            result = self.Lib.message_box(self, type="warning", text="This asset has never been published. Do you want to publish it?", no_button=True)
            if result == 0:
                return False
            else:
                self.publish_asset()
                return False

        # There's a new published version, ask if user wants to create a new thumbnail
        if os.path.isfile(path):
            publish_asset_id = self.selected_asset.dependency
            publish_asset = self.Asset(self, publish_asset_id, get_infos_from_id=True)
            last_publish_time = publish_asset.last_publish_as_date
            last_modified_img_time = self.Lib.modification_date(self, path)
            if last_publish_time > last_modified_img_time:
                result = self.Lib.thumbnail_creation_box(self, text="There's a new publish available. Do you want to create a thumbnail for it?")
                if result == 1:
                    os.remove(path)
                    self.update_thumbnail()
                    return False

        # Thumbnail has never been created for asset, ask if user wants to create a thumbnail
        if not os.path.isfile(path):
            result = self.Lib.message_box(self, type="warning", text="There is no {0} for this asset. Do you want to create one?".format(type_full_text), no_button=True)
            if result == 0:
                return False
            else:
                self.update_thumbnail()
                return False

        return True

    def load_obj_in_gplay(self):
        subprocess.Popen(["Z:\\RFRENC~1\\Outils\\SPCIFI~1\\Houdini\\HOUDIN~1.13\\bin\\gplay.exe", self.selected_asset.obj_path], shell=True)

    def load_asset(self):

        self.statusLbl.setText("Status: Loading asset {0}".format(self.selected_asset.name))

        self.selected_asset.change_last_access()
        self.lastAccessLbl.setText("Last accessed by: " + self.selected_asset.last_access)

        if self.selected_asset.type == "mod":
            if self.selected_asset.extension == "blend":
                t = Thread(target=lambda: subprocess.Popen([self.blender_path, self.selected_asset.full_path]))
                t.start()
            elif self.selected_asset.extension == "ma":
                t = Thread(target=lambda: subprocess.Popen([self.maya_path, self.selected_asset.full_path]))
                t.start()
            elif self.selected_asset.extension == "scn":
                t = Thread(target=lambda: subprocess.Popen([self.softimage_path, self.selected_asset.full_path]))
                t.start()
            elif self.selected_asset.extension == "hda":
                process = QtCore.QProcess(self)
                process.start(self.houdini_path, [self.selected_asset.full_path])

        elif self.selected_asset.type == "shd":
            process = QtCore.QProcess(self)
            process.start(self.houdini_path, [self.selected_asset.full_path.replace("\\", "/")])

        elif self.selected_asset.type == "sim":
            process = QtCore.QProcess(self)
            scene_path = os.path.split(self.selected_asset.full_path.replace("\\", "/"))[0] + "/" + os.path.split(self.selected_asset.full_path.replace("\\", "/"))[1].split("_")[0] + "_01.hipnc"
            print(scene_path)
            process.start(self.houdini_path, [scene_path])

        elif self.selected_asset.type == "lay":
            shutil.copy2(self.selected_asset.full_path, self.selected_asset.full_path.replace(".hipnc", "_" + self.username + "_laytmp.hipnc"))
            process = QtCore.QProcess(self)
            process.finished.connect(partial(self.load_asset_finished, self.selected_asset.full_path.replace(".hipnc", "_" + self.username + "_laytmp.hipnc")))
            process.start(self.houdini_path, [self.selected_asset.full_path.replace("\\", "/").replace(".hipnc", "_" + self.username + "_laytmp.hipnc")])

        elif self.selected_asset.type == "rig" or self.selected_asset.type == "anm":
            process = QtCore.QProcess(self)
            process.start(self.maya_path, [self.selected_asset.full_path.replace("\\", "/")])

        elif self.selected_asset.type == "cam":
            associated_hip_scene = self.cursor.execute('''SELECT asset_path FROM assets WHERE asset_id=?''', (self.selected_asset.dependency, )).fetchone()[0]
            associated_hip_scene = self.selected_project_path + associated_hip_scene
            shutil.copy2(associated_hip_scene, associated_hip_scene.replace(".hipnc", "_" + self.username + "_camtmp.hipnc"))
            process = QtCore.QProcess(self)
            process.finished.connect(partial(self.load_asset_finished, associated_hip_scene.replace(".hipnc", "_" + self.username + "_camtmp.hipnc")))
            process.start(self.houdini_path, [associated_hip_scene.replace("\\", "/").replace(".hipnc", "_" + self.username + "_camtmp.hipnc")])

        elif self.selected_asset.type == "lgt":
            associated_hip_scene = self.cursor.execute('''SELECT asset_path FROM assets WHERE asset_id=?''', (self.selected_asset.dependency, )).fetchone()[0]
            associated_hip_scene = self.selected_project_path + associated_hip_scene
            shutil.copy2(associated_hip_scene, associated_hip_scene.replace(".hipnc", "_" + self.username + "_lgttmp.hipnc"))
            process = QtCore.QProcess(self)
            process.finished.connect(partial(self.load_asset_finished, associated_hip_scene.replace(".hipnc", "_" + self.username + "_lgttmp.hipnc")))
            process.start(self.houdini_path, [associated_hip_scene.replace("\\", "/").replace(".hipnc", "_" + self.username + "_lgttmp.hipnc")])

        elif self.selected_asset.type == "cmp":
            selected_nuke_shot = self.selected_asset.full_path.split("\\")[-1]
            all_nuke_scripts = glob("Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/cmp/{0}/02_comp/*".format(selected_nuke_shot))
            all_nuke_scripts = [i for i in all_nuke_scripts if not "~" in i]
            all_nuke_scripts = [i for i in all_nuke_scripts if not "autosave" in i]
            all_nuke_scripts_versions = [i.split("\\")[-1].split("_")[-1].replace(".nk", "") for i in all_nuke_scripts if not "autosave" in i]

            self.select_version_dialog = QtGui.QDialog(self)
            self.select_version_dialog.setMinimumWidth(150)
            self.Lib.apply_style(self, self.select_version_dialog)

            self.select_version_dialog.setWindowTitle("Select a version to load:")
            self.select_version_dialog_layout = QtGui.QHBoxLayout(self.select_version_dialog)

            version_combobox = QtGui.QComboBox(self.select_version_dialog)
            version_combobox.addItems(all_nuke_scripts_versions)
            self.select_version_dialog_layout.addWidget(version_combobox)

            loadBtn = QtGui.QPushButton("Load Nuke Script", self.select_version_dialog)
            loadBtn.clicked.connect(self.select_version_dialog.close)

            self.select_version_dialog_layout.addWidget(loadBtn)

            self.select_version_dialog.exec_()

            process = QtCore.QProcess(self)
            process.start(self.nuke_path, ["Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/cmp/{0}/02_comp/{0}_{1}.nk".format(selected_nuke_shot, version_combobox.currentText())])

        elif self.selected_asset.type == "tex":
            #texture_project_path = self.Lib.get_mari_project_path_from_asset_name(self, self.selected_asset.name, self.selected_asset.version)
            self.Lib.switch_mari_cache(self, "server")
            self.mari_open_asset_process = QtCore.QProcess(self)
            self.mari_open_asset_process.finished.connect(partial(self.mari_finished))
            self.mari_open_asset_process.start(self.mari_path, [self.cur_path + "\\lib\\software_scripts\\mari_start_project.py", self.selected_asset.name + "_" + self.selected_asset.version])

        self.statusLbl.setText("Status: Idle...")

    def load_asset_finished(self, file_to_remove=None):
        if file_to_remove != None:
            if os.path.isfile(file_to_remove):
                os.remove(file_to_remove)

    def load_obj_in_headus(self):
        try:
            self.load_uv_process = QtCore.QProcess(self)
            self.load_uv_process.start("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/headus/howin32.exe", [self.selected_asset.obj_path])
        except:
            pass

    def mari_finished(self):
        self.mari_open_asset_process.kill()

        self.Lib.switch_mari_cache(self, "perso")

        self.statusLbl.setText("Status: Idle...")

    def open_real_layout_scene(self):
        if self.selected_asset.type == "mod":
            hda_path = self.cursor.execute('''SELECT asset_path FROM assets WHERE asset_dependency=? AND asset_extension="hda" AND asset_type="lay"''', (self.selected_asset.id, )).fetchone()
            process = QtCore.QProcess(self)
            process.start(self.houdini_path, [self.selected_project_path + hda_path[0].replace("\\", "/")])
        else:
            lock_files = glob("Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/lay/*")
            lock_files = [i for i in lock_files if ".lock" in i]
            lock_scenes = [(os.path.split(i)[-1].split("_")[0].replace(".lock", ""), os.path.split(i)[-1].split("_")[-1].replace(".lock", "")) for i in lock_files]

            if len(lock_scenes) > 0:
                for scene_and_user in lock_scenes:
                    scene = scene_and_user[0]
                    user = scene_and_user[1]
                    if self.selected_asset.name == scene and user != self.username:
                        self.Lib.message_box(self, type="error", text="The scene is already in use by " + self.members[user])
                        return

            open("Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/lay/" + self.selected_asset.name + "_" + self.username + ".lock", "a+")

            process = QtCore.QProcess(self)
            process.finished.connect(partial(self.delete_layout_lock, self.selected_asset.name))
            process.start(self.houdini_path, [self.selected_asset.full_path])

    def delete_layout_lock(self, layout_scene_name):
        lock_files = glob("Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/lay/*")
        lock_files = [i for i in lock_files if ".lock" in i]

        for each_file in lock_files:
            if layout_scene_name in each_file:
                os.remove(each_file)

    def open_associated_layout_scene(self):
        shutil.copy2(self.associated_layout_scene, self.associated_layout_scene.replace(".hipnc", "_" + self.username + "_layplacementtmp.hipnc"))
        process = QtCore.QProcess(self)
        process.finished.connect(partial(self.load_asset_finished, self.associated_layout_scene.replace(".hipnc", "_" + self.username + "_layplacementtmp.hipnc")))
        process.start(self.houdini_path, [self.associated_layout_scene.replace("\\", "/").replace(".hipnc", "_" + self.username + "_layplacementtmp.hipnc")])

    def delete_asset(self):

        result = self.Lib.message_box(self, type="warning", text="You're about to delete an asset. This action is not undoable. Are you sure you want to continue?", window_title="Delete asset?")
        if result == 1024:
            return

        asset_name = self.selected_asset.name
        asset_name_lowres = asset_name + "-lowres"

        # Delete asset on shotgun
        sg_asset = self.sg.find_one("Asset", [["code","is",asset_name]])
        try:
            self.sg.delete("Asset", sg_asset["id"])
        except:
            pass

        assets = self.cursor.execute('''SELECT asset_id FROM assets WHERE asset_name=?''', (asset_name,)).fetchall()
        assets_lowres = self.cursor.execute('''SELECT asset_id FROM assets WHERE asset_name=?''', (asset_name_lowres,)).fetchall()

        assets_to_delete = assets + assets_lowres
        assets_to_delete = [self.Asset(self, asset_id[0], get_infos_from_id=True) for asset_id in assets_to_delete]

        for asset in assets_to_delete:
            asset.remove_asset_from_db()

        self.Lib.remove_log_entry_from_asset_id(self, asset.id)

        tex_path = self.Lib.get_mari_project_path_from_asset_name(self, self.selected_asset.name, self.selected_asset.version)
        if tex_path != None:
            shutil.rmtree("Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + tex_path)

        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()
        # Hide all versions
        [version.setHidden(True) for version in self.versions]

    def import_into_scene(self):
        if self.selected_asset == None:
            return

        if self.selected_asset.type == "mod":
            self.import_obj_into_scene()

        elif self.selected_asset.type == "anm":

            self.create_from_asset_dialog = QtGui.QDialog(self)
            self.Lib.apply_style(self, self.create_from_asset_dialog)

            self.create_from_asset_dialog.setWindowTitle("Choose which type of asset to import")
            self.create_from_asset_dialog_main_layout = QtGui.QHBoxLayout(self.create_from_asset_dialog)

            camBtn = QtGui.QPushButton("Camera", self.create_from_asset_dialog)
            layBtn = QtGui.QPushButton("Layout", self.create_from_asset_dialog)
            rigBtn = QtGui.QPushButton("Rigs", self.create_from_asset_dialog)

            camBtn.clicked.connect(self.import_cam_into_anm)
            layBtn.clicked.connect(self.add_assets_into_anim)
            rigBtn.clicked.connect(self.add_rigs_to_anim)

            self.create_from_asset_dialog_main_layout.addWidget(camBtn)
            self.create_from_asset_dialog_main_layout.addWidget(layBtn)
            self.create_from_asset_dialog_main_layout.addWidget(rigBtn)

            self.create_from_asset_dialog.exec_()

        elif self.selected_asset.type == "lay":
            AddAssetsToLayoutWindow(self)

    def import_cam_into_anm(self):
        self.create_from_asset_dialog.close()
        all_cameras = []
        for asset in self.assets:
            if asset.type == "cam" and asset.extension == "abc":
                all_cameras.append(asset)

        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Please choose a camera")
        layout = QtGui.QVBoxLayout(dialog)

        listwidget = QtGui.QListWidget(dialog)

        for asset in all_cameras:
            item = QtGui.QListWidgetItem("Sequence: {0} | Shot: {1}".format(asset.sequence, asset.shot, asset.name))
            item.setData(QtCore.Qt.UserRole, asset)
            listwidget.addItem(item)

        acceptBtn = QtGui.QPushButton("Import selected camera", dialog)
        acceptBtn.clicked.connect(dialog.accept)

        layout.addWidget(listwidget)
        layout.addWidget(acceptBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        selected_camera = listwidget.selectedItems()[0]
        self.selected_camera_asset = selected_camera.data(QtCore.Qt.UserRole).toPyObject()

        self.import_cam_process = QtCore.QProcess(self)
        self.import_cam_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported Camera into scene!"))
        self.import_cam_process.waitForFinished()
        self.import_cam_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_cam_into_anm.py", self.selected_asset.full_path, self.selected_camera_asset.full_path])

        self.cursor.execute('''INSERT INTO camera_in_anim(asset_id, has_camera) VALUES(?,?)''', (self.selected_asset.id, 1,))
        self.db.commit()

    def add_assets_into_anim(self):
        self.create_from_asset_dialog.close()
        all_layout_scene = []
        for asset in self.assets:
            if asset.type == "lay" and asset.extension == "hipnc":
                all_layout_scene.append(asset)

        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Please choose a layout scene")
        layout = QtGui.QVBoxLayout(dialog)

        listwidget = QtGui.QListWidget(dialog)

        for asset in all_layout_scene:
            item = QtGui.QListWidgetItem("Sequence: {0} | Shot: {1} | Name: {2}".format(asset.sequence, asset.shot, asset.name))
            item.setData(QtCore.Qt.UserRole, asset)
            listwidget.addItem(item)

        acceptBtn = QtGui.QPushButton("Select layout scene", dialog)
        acceptBtn.clicked.connect(dialog.accept)

        layout.addWidget(listwidget)
        layout.addWidget(acceptBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        selected_scene = listwidget.selectedItems()[0]
        self.selected_layout_asset = selected_scene.data(QtCore.Qt.UserRole).toPyObject()

        AddAssetsToAnimWindow(self)

    def add_rigs_to_anim(self):
        self.create_from_asset_dialog.close()
        AddRigsToAnimWindow(self)

    def import_obj_into_scene(self):
        if "lowres" in self.selected_asset.name:
            obj_file = self.selected_asset.obj_path.replace("-lowres", "")
        else:
            # Ask for user to select files
            obj_file = QtGui.QFileDialog.getOpenFileName(self, 'Select OBJ', 'H:/', "3D Model (*.obj)")

            if len(obj_file) < 1:
                return

        if self.selected_asset.extension == "blend":
            self.import_obj_process = QtCore.QProcess(self)
            self.import_obj_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported OBJ file!"))
            self.import_obj_process.waitForFinished()
            self.import_obj_process.start(self.blender_path, ["-b", "-P", self.cur_path + "\\lib\\software_scripts\\blender_import_obj_into_scene.py", "--", self.selected_asset.full_path, obj_file])
        elif self.selected_asset.extension == "ma":
            self.import_obj_process = QtCore.QProcess(self)
            self.import_obj_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported OBJ file!"))
            self.import_obj_process.waitForFinished()
            self.import_obj_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_obj_into_scene.py", self.selected_asset.full_path, obj_file])
        elif self.selected_asset.extension == "scn":
            self.import_obj_process = QtCore.QProcess(self)
            self.import_obj_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported OBJ file!"))
            self.import_obj_process.start(self.softimage_batch_path, ["-processing", "-script", self.cur_path + "\\lib\\software_scripts\\softimage_import_obj_into_scene.py", "-main", "import_obj", "-args", "-file_path", self.selected_asset.full_path, "-obj_path", obj_file])

    def create_asset_from_scratch(self):

        if self.selected_department_name == "lay":
            if self.selected_sequence_name == "xxx":
                self.Lib.message_box(self, type="error", text="You must select a sequence to create a layout")
                return

        # Create soft selection and asset name dialog
        dialog = QtGui.QDialog(self)
        self.Lib.apply_style(self, dialog)

        dialog.setWindowTitle("Enter a name")
        dialog_main_layout = QtGui.QVBoxLayout(dialog)


        if self.selected_department_name == "mod":
            software_combobox = QtGui.QComboBox(dialog)
            software_combobox.addItems(["Blender", "Maya", "Softimage", "Houdini"])
            dialog_main_layout.addWidget(software_combobox)

            type_combobox = QtGui.QComboBox(dialog)
            type_combobox.addItems(['Prop', 'Vehicle', 'Character', 'Environment', 'Matte Painting'])
            dialog_main_layout.addWidget(type_combobox)

        name_line_edit = QtGui.QLineEdit()
        name_line_edit.setPlaceholderText("Please enter a name...")
        name_line_edit.returnPressed.connect(dialog.accept)

        if self.selected_department_name == "mod":
            description_line_edit = QtGui.QLineEdit()
            description_line_edit.setPlaceholderText('Please enter a description for the asset')
            description_line_edit.returnPressed.connect(dialog.accept)

        dialog_main_layout.addWidget(name_line_edit)
        if self.selected_department_name == "mod":
            dialog_main_layout.addWidget(description_line_edit)

        dialog.exec_()
        if dialog.result() == 0:
            return

        if self.selected_department_name == "mod":
            # Get selected software and associated extension
            selected_software = str(software_combobox.currentText()).lower().replace(" ", "")
            if selected_software == "blender":
                extension = "blend"
            elif selected_software == "maya":
                extension = "ma"
            elif selected_software == "softimage":
                extension = "scn"
            elif selected_software == "houdini":
                extension = "hda"

        # Get asset name
        asset_name = unicode(name_line_edit.text())
        asset_name = self.Lib.normalize_str(self, asset_name)
        asset_name = asset_name_tmp = self.Lib.convert_to_camel_case(self, asset_name, asset_type=self.selected_department_name)

        if self.selected_department_name == "mod":
            asset_description = unicode(self.utf8_codec.fromUnicode(description_line_edit.text()), 'utf-8')
            selected_type = str(type_combobox.currentText())

        # If an asset with given name already exists, change asset name to "assetname-version" (ex: colonne-01) until no asset with given name exists
        version = 1
        all_assets_name = self.cursor.execute('''SELECT asset_name FROM assets WHERE asset_type != "ref"''').fetchall()
        all_assets_name = [str(i[0]) for i in all_assets_name]
        while asset_name_tmp in all_assets_name:
            all_assets_name = self.cursor.execute('''SELECT asset_name FROM assets''').fetchall()
            all_assets_name = [str(i[0]) for i in all_assets_name]
            asset_name_tmp = asset_name + str(version).zfill(2)
            version += 1

        asset_name = asset_name_tmp

        if self.selected_department_name == "mod":
            self.create_mod_asset_from_scratch(asset_name, extension, selected_software, asset_description, selected_type)
        elif self.selected_department_name == "lay":
            self.create_lay_asset_from_scratch(asset_name)
        elif self.selected_department_name == "sim":
            self.create_sim_asset_from_scratch(asset_name)
        elif self.selected_department_name == "anm":
            self.create_anm_asset_from_scratch(asset_name)

    def create_asset_from_asset(self):
        if self.selected_asset.type == "mod" or (self.selected_asset.type == "lay" and self.selected_asset.extension == "hda" and self.selected_asset.version != "out"):
            if self.selected_asset == None: return
            if "lowres" in self.selected_asset.name:
                self.Lib.message_box(self, type="error", text="You can't create an asset from a low-res asset. Please select the corresponding high-res asset.")
                return
            self.create_from_asset_dialog = QtGui.QDialog(self)
            self.Lib.apply_style(self, self.create_from_asset_dialog)

            self.create_from_asset_dialog.setWindowTitle("Choose which asset to create")
            self.create_from_asset_dialog_main_layout = QtGui.QHBoxLayout(self.create_from_asset_dialog)

            rigBtn = QtGui.QPushButton("Rig", self.create_from_asset_dialog)
            texBtn = QtGui.QPushButton("Tex", self.create_from_asset_dialog)
            shdBtn = QtGui.QPushButton("Shading", self.create_from_asset_dialog)
            lowBtn = QtGui.QPushButton("LowRes", self.create_from_asset_dialog)

            rigBtn.clicked.connect(self.create_rig_asset_from_mod)
            texBtn.clicked.connect(self.create_tex_asset_from_mod)
            shdBtn.clicked.connect(self.create_shd_asset_from_mod)
            lowBtn.clicked.connect(self.create_lowres_from_mod)

            self.create_from_asset_dialog_main_layout.addWidget(rigBtn)
            self.create_from_asset_dialog_main_layout.addWidget(texBtn)
            self.create_from_asset_dialog_main_layout.addWidget(shdBtn)
            self.create_from_asset_dialog_main_layout.addWidget(lowBtn)

            self.create_from_asset_dialog.exec_()

        elif self.selected_asset.type == "rig":
            AnimSceneChooser(self)

        elif self.selected_asset.type == "lay":
            if self.selected_asset == None: return
            self.create_from_asset_dialog = QtGui.QDialog(self)
            self.Lib.apply_style(self, self.create_from_asset_dialog)

            self.create_from_asset_dialog.setWindowTitle("Enter a name")
            self.create_from_asset_dialog_main_layout = QtGui.QHBoxLayout(self.create_from_asset_dialog)

            cameraBtn = QtGui.QPushButton("Camera", self.create_from_asset_dialog)
            lightingBtn = QtGui.QPushButton("Lighting", self.create_from_asset_dialog)

            cameraBtn.clicked.connect(self.create_cam_asset_from_lay)
            lightingBtn.clicked.connect(self.create_lgt_asset_from_lay)

            self.create_from_asset_dialog_main_layout.addWidget(cameraBtn)
            self.create_from_asset_dialog_main_layout.addWidget(lightingBtn)

            self.create_from_asset_dialog.exec_()

    def create_rig_asset_from_mod(self):

        is_asset_rig_already_existing = self.cursor.execute('''SELECT * FROM assets WHERE asset_type="rig" AND asset_name=?''', (self.selected_asset.name,)).fetchone()
        if is_asset_rig_already_existing != None:
            self.Lib.message_box(self, type="error", text="A rig already exists for this asset.")
            return

        self.create_from_asset_dialog.close()

        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name, "", "ma", "rig", "01", [], self.selected_asset.id, "", "", self.username)
        asset.add_asset_to_db()

        obj_path = str(self.selected_asset.obj_path).replace("\\", "/")
        file_export = os.path.splitext(obj_path)[0].replace("mod", "rig").replace("out", "01") + ".ma"
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(partial(self.asset_creation_finished, asset))
        self.process.waitForFinished()
        self.process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_obj_as_reference.py", obj_path, file_export])

    def create_tex_asset_from_mod(self):
        is_asset_tex_already_existing = self.cursor.execute('''SELECT * FROM assets WHERE asset_type="tex" AND asset_name=?''', (self.selected_asset.name,)).fetchone()
        if is_asset_tex_already_existing != None:
            self.Lib.message_box(self, type="error", text="A texture scene already exists for this asset.")
            return

        self.create_from_asset_dialog.close()

        obj_publish_path = self.Asset(self, self.selected_asset.dependency, get_infos_from_id=True)

        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name, "", "mari", "tex", "01", [], obj_publish_path.id, "", "", self.username)
        asset.add_asset_to_db()

        self.Lib.switch_mari_cache(self, "server")
        self.mari_process = QtCore.QProcess(self)
        self.mari_process.readyRead.connect(self.mari_process_read_data)
        self.mari_process.finished.connect(partial(self.asset_creation_finished, asset))
        self.mari_process.waitForFinished()
        self.mari_process.start(self.mari_path, [self.cur_path + "\\lib\\software_scripts\\mari_create_project.py", self.selected_asset.name, "01", obj_publish_path.full_path.replace("\\\\", "/")])

    def mari_process_read_data(self):
        while self.mari_process.canReadLine():
            out = self.mari_process.readLine()
            if "Welcome to Mari 2.6v2!  Type help() to get started." in out:
                self.mari_process.kill()
            print(out)

    def create_cam_asset_from_lay(self):

        self.create_from_asset_dialog.close()

        # if selected sequence has no shots, abort
        shots = self.shots[self.selected_asset.sequence]
        if len(shots) == 0:
            self.Lib.message_box(self, type="error", text="You can't create a camera for a sequence without any shot")
            return

        # Create shot list selection dialog
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Choose a shot")
        self.Lib.apply_style(self, dialog)

        layout = QtGui.QVBoxLayout(dialog)

        shotLbl = QtGui.QLabel("Shot list:", self)
        shotListWidget = QtGui.QListWidget(self)
        createCamBtn = QtGui.QPushButton("Create asset", self)
        createCamBtn.clicked.connect(dialog.accept)

        existing_cam_shots = self.cursor.execute('''SELECT shot_number FROM assets WHERE asset_type="cam" AND sequence_name=?''', (self.selected_asset.sequence,)).fetchall()
        if len(existing_cam_shots) > 0:
            existing_cam_shots = [str(i[0]) for i in existing_cam_shots]

        shots = self.shots[self.selected_asset.sequence]
        shots_with_no_cam = sorted(list(set(shots) - set(existing_cam_shots)))

        if len(shots_with_no_cam) == 0:
            self.Lib.message_box(self, type="warning", text="There's already a camera for every shot in this sequence")
            return

        shotListWidget.addItems(QtCore.QStringList(shots_with_no_cam))
        shotListWidget.setCurrentRow(0)
        selected_shot = shots[0]

        layout.addWidget(shotLbl)
        layout.addWidget(shotListWidget)
        layout.addWidget(createCamBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        # Get selected item
        selected_shot = shotListWidget.selectedItems()[0]
        selected_shot = str(selected_shot.text())

        camera_asset = self.Asset(self, 0, self.selected_project_name, self.selected_asset.sequence, selected_shot, "cam-" + selected_shot, "", "hda", "cam", "01", [], self.selected_asset.id, "", "", self.username)
        camera_asset.add_asset_to_db()

        camera_asset_publish = self.Asset(self, 0, self.selected_project_name, self.selected_asset.sequence, selected_shot, "cam-" + selected_shot, "", "abc", "cam", "out", [], camera_asset.id, "", "", self.username)
        camera_asset_publish.add_asset_to_db()

        shutil.copy(self.NEF_folder + "\\camera.abc", camera_asset_publish.full_path)

        # Create HDA associated to modeling scene
        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, camera_asset))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_import_cam_into_lay.py", self.selected_asset.full_path.replace("\\", "/"), camera_asset.full_path.replace("\\", "/"), selected_shot])

        # Add entry to assets in layout database
        self.cursor.execute('''INSERT INTO assets_in_layout(asset_id, layout_id) VALUES(?,?)''', (camera_asset.id, self.selected_asset.id,))
        self.db.commit()

    def create_lgt_asset_from_lay(self):

        self.create_from_asset_dialog.close()

        # if selected sequence has no shots, abort
        shots = self.shots[self.selected_asset.sequence]
        if len(shots) == 0:
            self.Lib.message_box(self, type="error", text="You can't create a light for a sequence without any shot")
            return

        # Create shot list selection dialog
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Choose a shot")
        self.Lib.apply_style(self, dialog)

        layout = QtGui.QVBoxLayout(dialog)

        shotLbl = QtGui.QLabel("Shot list:", self)
        shotListWidget = QtGui.QListWidget(self)
        createLgtBtn = QtGui.QPushButton("Create asset", self)
        createLgtBtn.clicked.connect(dialog.accept)

        existing_lights_shots = self.cursor.execute('''SELECT shot_number FROM assets WHERE asset_type="lgt" AND sequence_name=?''', (self.selected_asset.sequence, )).fetchall()
        if len(existing_lights_shots) > 0:
            existing_lights_shots = [str(i[0]) for i in existing_lights_shots]

        shots = self.shots[self.selected_asset.sequence]
        shots_with_no_lights = sorted(list(set(shots) - set(existing_lights_shots)))

        if len(shots_with_no_lights) == 0:
            self.Lib.message_box(self, type="warning", text="There's already a light for every shot in this sequence")
            return

        shotListWidget.addItems(QtCore.QStringList(shots_with_no_lights))
        shotListWidget.setCurrentRow(0)
        selected_shot = shots[0]

        layout.addWidget(shotLbl)
        layout.addWidget(shotListWidget)
        layout.addWidget(createLgtBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        # Get selected item
        selected_shot = shotListWidget.selectedItems()[0]
        selected_shot = str(selected_shot.text())

        light_asset = self.Asset(self, 0, self.selected_project_name, self.selected_asset.sequence, selected_shot, self.selected_asset.sequence + "_lighting-" + selected_shot, "", "hda", "lgt", "01", [], self.selected_asset.id, "", "", self.username)
        light_asset.add_asset_to_db()

        # Create HDA associated to modeling scene
        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, light_asset))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_import_lgt_into_lay.py", self.selected_asset.full_path.replace("\\", "/"), light_asset.full_path.replace("\\", "/"), selected_shot])

        # Add entry to assets in layout database
        self.cursor.execute('''INSERT INTO assets_in_layout(asset_id, layout_id) VALUES(?,?)''', (light_asset.id, self.selected_asset.id,))
        self.db.commit()

    def create_mod_asset_from_scratch(self, asset_name="", extension=None, selected_software=None, asset_description='', selected_type=''):

        if selected_software == "houdini":
            # Create modeling scene asset
            asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "mod", "01", [], "", "", "", self.username)
            asset.add_asset_to_db()

            # Create main HDA database entry
            main_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "ass", "out", [], asset.id, "", "", self.username)
            main_hda_asset.add_asset_to_db()

            # Create default publish cube (obj)
            obj_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "obj", "mod", "out", [], asset.id, "", "", self.username)
            obj_asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_asset.full_path)

            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_asset.full_path.replace("_" + obj_asset.name + "_", "_" + obj_asset.name + "-lowres_"))

            # Add publish obj as dependency to main asset
            asset.change_dependency(obj_asset.id)

            # Create modeling HDA
            self.houdini_hda_process = QtCore.QProcess(self)
            self.houdini_hda_process.waitForFinished()
            self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_modeling_hda_for_houdini.py", asset.name, asset.obj_path, asset.full_path])

        else:
            # Create modeling scene asset
            asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", extension, "mod", "01", [], "", "", "", self.username)
            asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\" + selected_software + "." + extension, asset.full_path)

            # Create default publish cube (obj)
            obj_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "obj", "mod", "out", [], asset.id, "", "", self.username)
            obj_asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_asset.full_path)
            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_asset.full_path.replace("_" + obj_asset.name + "_", "_" + obj_asset.name + "-lowres_"))

            # Add publish obj as dependency to main asset
            asset.change_dependency(obj_asset.id)

            # Create main HDA database entry
            main_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "ass", "out", [], asset.id, "", "", self.username)
            main_hda_asset.add_asset_to_db()

        # Create HDA associated to modeling scene
        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, asset))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_modeling_hda.py", self.cur_path_one_folder_up, main_hda_asset.full_path, main_hda_asset.obj_path, asset_name, main_hda_asset.obj_path.replace(".obj", ".hdanc")])


        # SHOTGUN
        #Retrieve sequence and shot in Shotgun
        sequence = self.sg.find("Sequence", [["code","is",self.selected_sequence_name]])

        # Check if sequence exists
        if len(sequence) > 0:
            shot = self.sg.find("Shot", [["code","is",self.selected_shot_number],["sg_sequence","is",sequence]])
        else:
            sequence = []
            shot = []

        data = {
            'project': {'type': 'Project', 'id': self.sg_project_id},
            'code': asset_name,
            'shots':shot,
            'sequences':sequence,
            'description':asset_description,
            'sg_asset_type':selected_type
        }

        # Create main asset in shotgun
        sg_asset = self.sg.create("Asset", data)

        # Create associated shotgun tasks
        sg_asset = self.sg.find_one("Asset", [["code", "is", asset_name]])
        mod_step = self.sg.find_one('Step', [['code', 'is', 'Modeling']])
        cpt_step = self.sg.find_one('Step', [['code', 'is', 'Concept']])
        tex_step = self.sg.find_one('Step', [['code', 'is', 'Texturing']])
        shd_step = self.sg.find_one('Step', [['code', 'is', 'Shading']])

        data = {'project': {'type': 'Project', 'id': self.sg_project_id}, 'content': 'references', 'entity': sg_asset, 'step': cpt_step}
        self.sg.create('Task', data)
        data = {'project': {'type': 'Project', 'id': self.sg_project_id}, 'content': 'concepts', 'entity': sg_asset, 'step': cpt_step}
        self.sg.create('Task', data)
        data = {'project': {'type': 'Project', 'id': self.sg_project_id}, 'content': 'modeling', 'entity': sg_asset, 'step': mod_step}
        self.sg.create('Task', data)
        data = {'project': {'type': 'Project', 'id': self.sg_project_id}, 'content': 'UV', 'entity': sg_asset, 'step': mod_step}
        self.sg.create('Task', data)
        data = {'project': {'type': 'Project', 'id': self.sg_project_id}, 'content': 'texturing', 'entity': sg_asset, 'step': tex_step}
        self.sg.create('Task', data)
        data = {'project': {'type': 'Project', 'id': self.sg_project_id}, 'content': 'shading', 'entity': sg_asset, 'step': shd_step}
        self.sg.create('Task', data)

        # Create PureRef Document
        shutil.copy(self.NEF_folder + "\\default.pur", "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/ref/pureref/" + asset_name + ".pur")

        # Create texture folder
        os.makedirs("Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/tex/" + asset_name)

    def create_lay_asset_from_scratch(self, asset_name):

        # Create modeling scene asset
        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hipnc", "lay", "01", [], "", "", "", self.username)
        asset.add_asset_to_db()
        shutil.copy(self.NEF_folder + "\\houdini.hipnc", asset.full_path)

        self.asset_creation_finished(asset)

        #self.houdini_hda_process = QtCore.QProcess(self)
        #self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, asset))
        #self.houdini_hda_process.waitForFinished()
        #self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_import_glob_lgt_into_lay.py", asset.full_path.replace("_01.", "_global_lighting.").replace(".hipnc", ".hda"), asset.full_path])

    def create_sim_asset_from_scratch(self, asset_name):
        sim_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "sim", "01", [], "", "", "", self.username)
        sim_asset.add_asset_to_db()

        # Create HDA for sim asset
        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, sim_asset))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_sim_from_scratch.py", sim_asset.full_path, asset_name])

    def create_anm_asset_from_scratch(self, asset_name):
        if self.selected_shot_number != "xxxx":
            try:
                os.mkdir("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\assets\\anm\\{0}".format(self.selected_shot_number))
            except:
                pass


        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "ma", "anm", "01", [], "", "", "", self.username)
        asset.add_asset_to_db()

        shutil.copy(self.cur_path_one_folder_up + "\\_NEF\\maya.ma", asset.full_path)
        self.asset_creation_finished(asset)

    def create_lowres_from_mod(self):

        self.create_from_asset_dialog.close()

        does_low_res_exists = self.cursor.execute('''SELECT asset_id FROM assets WHERE asset_name=?''', (self.selected_asset.name + "-lowres", )).fetchone()
        if does_low_res_exists != None:
            self.Lib.message_box(self, type="error", text="There's already a LowRes asset for this modeling")
            return

        # Create low res modeling scene asset
        asset_low_res = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name + "-lowres", "", self.selected_asset.extension, "mod", "01", [], "", "", "", self.username)
        asset_low_res.add_asset_to_db()
        if self.selected_asset.extension == "blend":
            selected_software = "blender"
        elif self.selected_asset.extension == "ma":
            selected_software = "maya"
        elif self.selected_asset.extension == "scn":
            selected_software = "softimage"
        elif self.selected_asset.extension == "c4d":
            selected_software = "cinema4d"
        elif self.selected_asset.extension == "hda":
            selected_software = "houdini"
        shutil.copy(self.NEF_folder + "\\" + selected_software + "." + self.selected_asset.extension, asset_low_res.full_path)

        # Create default lowres publish cube (obj)
        obj_lowres_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name + "-lowres", "", "obj", "mod", "out", [], asset_low_res.id, "", "", self.username)
        obj_lowres_asset.add_asset_to_db()
        asset_low_res.change_dependency(obj_lowres_asset.id)

        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()

        self.Lib.message_box(self, type="info", text="Successfully created LowRes modeling asset")

    def create_shd_asset_from_mod(self):
        self.create_from_asset_dialog.close()

        already_existing = self.cursor.execute('''SELECT * FROM assets WHERE asset_name=? AND asset_type="shd"''', (self.selected_asset.name, )).fetchone()
        if already_existing != None:
            self.Lib.message_box(self, type="error", text="There's already a shading scene for this asset!")
            return

        # Create shading HDA database entry
        shading_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, "", "hipnc", "shd", "01", [], "", "", "", self.username)
        shading_hda_asset.add_asset_to_db()
        main_hda_path = shading_hda_asset.full_path.replace("\\shd\\", "\\ass\\").replace("_shd_", "_ass_").replace("_01.", "_out.").replace(".hipnc", ".hda")

        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.readyRead.connect(self.blblbl)
        self.houdini_hda_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully created shading scene!"))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_shd_from_mod.py", main_hda_path, shading_hda_asset.full_path, shading_hda_asset.name])

    def blblbl(self):
        while self.houdini_hda_process.canReadLine():
            print(self.houdini_hda_process.readLine())

    def asset_creation_finished(self, asset):

        # Reload assets
        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()

        if self.selected_asset != None:
            if self.selected_asset.type == "mod" and asset.type == "rig":
                # Create default publish scene for rig asset
                out_rig_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name, "", "ma", "rig", "out", [], asset.id, "", "", self.username)
                out_rig_asset.add_asset_to_db()

                asset.change_dependency(out_rig_asset.id)

                shutil.copy(asset.full_path, out_rig_asset.full_path)

        # Update last access
        asset.change_last_access()
        self.lastAccessLbl.setText("Last accessed by: " + asset.last_access)

        # Add Log Entry
        log_entry = self.LogEntry(self, 0, asset.id, [], [], self.username, "", "asset", "{0} has created a new {1} asset ({2}).".format(self.members[self.username], self.departments_longname[asset.type], asset.name), datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()

        # Show info message
        self.Lib.message_box(self, type="info", text="Asset has been succesfully created!")

    def add_assets_to_layout(self):
        AddAssetsToLayoutWindow(self)

    def create_default_asset_thumbnail(self, asset):
        self.thumb_process = QtCore.QProcess(self)
        self.thumb_process.waitForFinished()
        asset_filename = asset.path.replace("\\assets\\" + asset.type + "\\", "")
        export_path = os.path.split(asset.full_path)[0] + "\\.thumb\\" + asset_filename.replace("_" + asset.version + ".", "_out.").replace("." + asset.extension, ".png")
        export_path = asset.default_thumb
        self.thumb_process.start("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/WinPython/python-2.7.9.amd64/python.exe", [self.cur_path + "\\lib\\thumb_creator.py", asset.name, self.cur_path + "\\media\\default_asset_thumb\\" + asset.type + ".png", export_path, self.cur_path + "\\media\\ProximaNova-Regular.otf"])

    def batch_update_thumbnails(self):

        self.batch_thumbnail = True

        # # Shading

        shading_asset_list = []
        for asset, asset_item in self.assets.items():
            if asset.type in ["shd"]:
                max_asset_id = self.cursor.execute('''SELECT MAX(asset_version), asset_id FROM assets WHERE asset_name=? AND asset_version != "out" AND asset_type="shd"''', (asset.name,)).fetchone()
                if max_asset_id[0] != None:
                    selected_asset = self.Asset(self, max_asset_id[1], get_infos_from_id=True)
                    shading_asset_list.append((selected_asset, selected_asset.last_publish_as_date))

        shading_asset_list.sort(key=lambda x: x[1], reverse=True)

        for asset in shading_asset_list:
            time_difference = asset[1] - datetime.now()
            if abs(time_difference.days) > 2:
                self.selected_asset = asset[0]
                self.update_thumbnail(ask_window=False)


        # Modeling

        modeling_asset_list = []
        for asset, asset_item in self.assets.items():
            if asset.type in ["mod"]:
                max_asset_id = self.cursor.execute('''SELECT MAX(asset_version), asset_id FROM assets WHERE asset_name=? AND asset_version != "out" AND asset_type="mod"''', (asset.name,)).fetchone()
                if max_asset_id[0] != None:
                    selected_asset = self.Asset(self, max_asset_id[1], get_infos_from_id=True)
                    modeling_asset_list.append((selected_asset, selected_asset.last_publish_as_date))

        modeling_asset_list.sort(key=lambda x: x[1], reverse=True)


        for asset in modeling_asset_list:
            time_difference = asset[1] - datetime.now()
            if abs(time_difference.days) > 2:
                self.selected_asset = asset[0]
                self.update_thumbnail(ask_window=False)

        self.batch_thumbnail = False

    def change_asset_software_01(self):
        self.statusLbl.setText("Status: Switching asset's software. This can take up to 5 minutes for high resolution meshes. Please wait...")
        self.blockSignals(True)
        self.current_extension = os.path.splitext(self.selected_asset.full_path)[-1]
        self.old_path = self.selected_asset.full_path

        dialog = QtGui.QDialog(self)
        self.Lib.apply_style(self, dialog)

        dialog.setWindowTitle("Select a software")
        dialog.setMinimumWidth(200)
        dialog_main_layout = QtGui.QVBoxLayout(dialog)

        if self.selected_asset.type == "mod":
            software_combobox = QtGui.QComboBox(dialog)
            if self.current_extension == '.blend':
                software_combobox.addItems(["Maya", "Softimage"])
            elif self.current_extension == '.ma':
                software_combobox.addItems(["Blender", "Softimage"])
            elif self.current_extension == '.scn':
                software_combobox.addItems(["Blender", "Maya"])

            dialog_main_layout.addWidget(software_combobox)
        else:
            return

        acceptBtn = QtGui.QPushButton('Accept', dialog)
        acceptBtn.clicked.connect(dialog.accept)
        dialog_main_layout.addWidget(acceptBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        self.selected_software = str(software_combobox.currentText()).lower()

        # Publish asset first
        self.publish_process = QtCore.QProcess(self)
        self.publish_process.finished.connect(self.normalize_modeling_scale)

        if self.current_extension == ".blend":
            self.publish_process.start(self.blender_path, ["-b", "-P", self.cur_path + "\\lib\\software_scripts\\blender_export_obj_from_scene.py", "--", self.selected_asset.full_path, self.selected_asset.obj_path.replace("\\", "/")])
        elif self.current_extension == ".ma":
            self.publish_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_export_obj_from_scene.py", self.selected_asset.full_path, self.selected_asset.obj_path.replace("\\", "/")])
        elif self.current_extension == ".scn":
            self.publish_process.start(self.softimage_batch_path,
                                       ["-processing", "-script", self.cur_path + "\\lib\\software_scripts\\softimage_export_obj_from_scene.py", "-main", "export_obj", "-args", "-file_path", self.selected_asset.full_path, "-export_path",
                                        self.selected_asset.obj_path.replace("\\", "/")])

    def normalize_modeling_scale(self):
        # Normalize modeling scale
        self.normalize_mod_scale_process = QtCore.QProcess(self)
        self.normalize_mod_scale_process.waitForFinished()
        self.normalize_mod_scale_process.finished.connect(self.change_asset_software_02)
        self.normalize_mod_scale_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_normalize_scale.py", self.selected_asset.obj_path.replace("\\", "/")])

    def change_asset_software_02(self):
        self.import_obj_process = QtCore.QProcess(self)

        if self.selected_software == "blender":
            new_path = self.selected_asset.full_path.replace(self.current_extension, '.blend')
            shutil.copy(self.NEF_folder + "\\blender.blend", new_path)
            self.import_obj_process.finished.connect(self.change_asset_software_03)
            self.import_obj_process.waitForFinished()
            self.import_obj_process.start(self.blender_path, ["-b", "-P", self.cur_path + "\\lib\\software_scripts\\blender_import_obj_into_scene.py", "--", new_path, self.selected_asset.obj_path])
            self.selected_asset.change_extension(new_extension='blend')

        elif self.selected_software == "maya":
            new_path = self.selected_asset.full_path.replace(self.current_extension, '.ma')
            shutil.copy(self.NEF_folder + "\\maya.ma", new_path)
            self.import_obj_process.finished.connect(self.change_asset_software_03)
            self.import_obj_process.waitForFinished()
            self.import_obj_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_obj_into_scene_from_output.py", new_path, self.selected_asset.obj_path])
            self.selected_asset.change_extension(new_extension='ma')

        elif self.selected_software == "softimage":
            new_path = self.selected_asset.full_path.replace(self.current_extension, '.scn')
            shutil.copy(self.NEF_folder + "\\softimage.scn", new_path)
            self.import_obj_process.finished.connect(self.change_asset_software_03)
            self.import_obj_process.start(self.softimage_batch_path,
                                          ["-processing", "-script", self.cur_path + "\\lib\\software_scripts\\softimage_import_obj_into_scene.py", "-main", "import_obj", "-args", "-file_path", new_path, "-obj_path", self.selected_asset.obj_path])
            self.selected_asset.change_extension(new_extension='scn')

    def change_asset_software_03(self):
        os.remove(self.old_path)
        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()
        self.Lib.message_box(self, type="info", text="Successfully switched software!")

        self.blockSignals(False)
        self.statusLbl.setText("Status: Idle...")

class AnimSceneChooser(QtGui.QDialog):
    def __init__(self, main):
        super(AnimSceneChooser, self).__init__()
        self.main = main

        self.setWindowTitle("Choose a sequence and a shot")
        self.main.Lib.apply_style(self.main, self)

        layout = QtGui.QGridLayout(self)

        seqLbl = QtGui.QLabel("Sequence:", self)
        shotLbl = QtGui.QLabel("Shot:", self)

        self.seqListWidget = QtGui.QListWidget(self)
        self.shotListWidget = QtGui.QListWidget(self)

        self.seqListWidget.itemClicked.connect(self.filter_shots_based_on_sequence)
        self.shotListWidget.itemClicked.connect(self.shot_list_clicked)

        seqList = QtCore.QStringList()
        [seqList.append(i) for i in self.main.shots.keys()]
        self.seqListWidget.addItems(seqList)

        for seq, shots in self.main.shots.items():
            item = QtGui.QListWidgetItem("None")
            item.setData(QtCore.Qt.UserRole, seq)
            self.shotListWidget.addItem(item)
            for shot in shots:
                item = QtGui.QListWidgetItem(shot)
                item.setData(QtCore.Qt.UserRole, seq)
                self.shotListWidget.addItem(item)

        createAnimSceneBtn = QtGui.QPushButton("Create animation asset", self)
        createAnimSceneBtn.clicked.connect(self.create_anm_from_rig)


        layout.addWidget(seqLbl, 0, 0)
        layout.addWidget(shotLbl, 0, 1)
        layout.addWidget(self.seqListWidget, 1, 0)
        layout.addWidget(self.shotListWidget, 1, 1)
        layout.addWidget(createAnimSceneBtn, 2, 0, 2, 2)

        self.seqListWidget.setCurrentRow(0)
        self.filter_shots_based_on_sequence()

        self.exec_()

    def filter_shots_based_on_sequence(self):
        self.selected_sequence = self.seqListWidget.selectedItems()[0]
        self.selected_sequence = str(self.selected_sequence.text())

        for i in xrange(0, self.shotListWidget.count()):
            seq_from_shot = self.shotListWidget.item(i).data(QtCore.Qt.UserRole).toPyObject()
            if seq_from_shot == self.selected_sequence:
                self.shotListWidget.item(i).setHidden(False)
            else:
                self.shotListWidget.item(i).setHidden(True)

    def shot_list_clicked(self):
        self.selected_shot = self.shotListWidget.selectedItems()[0]
        self.selected_shot = str(self.selected_shot.text())
        if self.selected_shot == "None":
            self.selected_shot = "xxxx"

    def create_anm_from_rig(self):

        asset = self.main.Asset(self.main, 0, self.main.selected_project_name, self.selected_sequence, self.selected_shot, self.main.selected_asset.name, "", "ma", "anm", "01", [], "", "", "", self.main.username)
        asset.add_asset_to_db()

        alembic_publish_asset = self.main.Asset(self.main, 0, self.main.selected_project_name, self.selected_sequence, self.selected_shot, self.main.selected_asset.name, "", "abc", "anm", "out", [], asset.id, "", "", self.main.username)
        alembic_publish_asset.add_asset_to_db()

        asset.change_dependency(alembic_publish_asset.id)

        process = QtCore.QProcess(self)
        process.waitForFinished()
        process.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_import_rig_as_reference.py", self.main.selected_asset.rig_out_path, asset.full_path])

        hda_layout_asset = self.main.cursor.execute('''SELECT asset_path FROM assets WHERE asset_name=? AND asset_extension="hda" AND asset_type="lay"''', (asset.name,)).fetchone()

        hda_process = QtCore.QProcess(self)
        hda_process.finished.connect(partial(self.create_abc, asset))
        hda_process.waitForFinished()
        hda_process.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_update_hda_from_abc.py", alembic_publish_asset.full_path.replace("\\", "/"), alembic_publish_asset.name, (self.main.selected_project_path + hda_layout_asset[0]).replace("\\", "/")])

    def create_abc(self, asset):
        self.publish_process = QtCore.QProcess(self)
        self.publish_process.finished.connect(partial(self.main.asset_creation_finished, asset))
        self.publish_process.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_export_anm_as_alembic.py", asset.full_path.replace("\\", "/"), asset.anim_out_path.replace("\\", "/"), "1", "2"])

class AddAssetsToLayoutWindow(QtGui.QDialog, Ui_addAssetsToLayoutWidget):
    def __init__(self, main):
        super(AddAssetsToLayoutWindow, self).__init__()

        self.main = main

        # Initialize the guis
        self.add_assets_layout = self.setupUi(self)
        self.main.Lib.apply_style(self.main, self)

        # Connections
        self.availableAssetsListWidget.doubleClicked.connect(self.add_asset_to_list)
        self.assetsToAddListWidget.doubleClicked.connect(self.remove_asset_from_list)
        self.availableAssetsListWidget.setDragEnabled(False)
        self.assetsToAddListWidget.setDragEnabled(False)

        self.addAssetBtn.clicked.connect(self.add_asset_to_list)
        self.removeAssetBtn.clicked.connect(self.remove_asset_from_list)
        self.addAssetsToLayoutBtn.clicked.connect(self.add_assets_to_layout)

        # GET ALL LAYOUT ASSETS
        self.all_layout_assets_id = self.main.cursor.execute('''SELECT asset_id FROM assets WHERE asset_type="lay" AND asset_extension="hda"''').fetchall() # Get IDs of all layout assets

        # GET ALL LAYOUT ASSETS WHICH ARE IN LAYOUT
        self.assets_in_layout_id = self.main.cursor.execute('''SELECT asset_id FROM assets_in_layout WHERE layout_id=?''', (int(self.main.selected_asset.id),)).fetchall() # Get IDs of layout assets in layout

        # Convert [(1,), (2,), (3)] to [1, 2, 3]
        if len(self.all_layout_assets_id) > 0:
            self.all_layout_assets_id = [i[0] for i in self.all_layout_assets_id]

        # Convert [(1,), (2,), (3)] to [1, 2, 3]
        if len(self.assets_in_layout_id) > 0:
            self.assets_in_layout_id = [i[0] for i in self.assets_in_layout_id]

        # Get assets not in layout by substracting assets in layout from all layout assets
        self.assets_not_in_layout_id = list(set(self.all_layout_assets_id) - set(self.assets_in_layout_id))

        # Get assets from IDs
        self.assets_in_layout = [self.main.Asset(self.main, i, get_infos_from_id=True) for i in self.assets_in_layout_id]
        self.assets_not_in_layout = [self.main.Asset(self.main, i, get_infos_from_id=True) for i in self.assets_not_in_layout_id]

        for asset in self.assets_not_in_layout:
            last_modeling_version_id = self.main.cursor.execute('''SELECT MAX(asset_id) FROM assets WHERE asset_name=? AND asset_type="mod" AND asset_version!="out"''', (asset.name,)).fetchone()
            last_modeling_asset = self.main.Asset(self.main, last_modeling_version_id[0], get_infos_from_id=True)
            img = last_modeling_asset.default_media_user

            item = QtGui.QListWidgetItem(asset.name)
            if os.path.isfile(img):
                item.setIcon(QtGui.QIcon(img))
            else:
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
                img = self.main.no_img_found

            item.setData(QtCore.Qt.UserRole, (asset, img))

            self.availableAssetsListWidget.addItem(item)

        for asset in self.assets_in_layout:
            if asset.type != "lay":
                continue
            last_modeling_version_id = self.main.cursor.execute('''SELECT MAX(asset_id) FROM assets WHERE asset_name=? AND asset_type="mod" AND asset_version!="out"''', (asset.name,)).fetchone()
            last_modeling_asset = self.main.Asset(self.main, last_modeling_version_id[0], get_infos_from_id=True)
            img = last_modeling_asset.default_media_user

            item = QtGui.QListWidgetItem(asset.name)
            if os.path.isfile(img):
                item.setIcon(QtGui.QIcon(img))
            else:
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
                img = self.main.no_img_found

            item.setData(QtCore.Qt.UserRole, (asset, img))

            self.assetsToAddListWidget.addItem(item)

        self.exec_()

    def add_asset_to_list(self):
        for asset in self.availableAssetsListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.assetsToAddListWidget.addItem(item)

            # Remove item from left list
            self.availableAssetsListWidget.takeItem(self.availableAssetsListWidget.row(asset))

    def remove_asset_from_list(self):
        for asset in self.assetsToAddListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.availableAssetsListWidget.addItem(item)

            # Remove item from left list
            self.assetsToAddListWidget.takeItem(self.assetsToAddListWidget.row(asset))

    def add_assets_to_layout(self):
        self.main.statusLbl.setText("Status: Adding/Removing asset to/from layout")

        assets_to_add = []
        for i in xrange(self.assetsToAddListWidget.count()):
            list_item = self.assetsToAddListWidget.item(i)
            asset = list_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            is_asset_in_layout = self.main.cursor.execute('''SELECT * FROM assets_in_layout WHERE asset_id=? AND layout_id=?''', (asset.id, int(self.main.selected_asset.id),)).fetchone()
            if is_asset_in_layout == None:
                assets_to_add.append(asset.full_path.replace("\\", "/"))
                self.main.cursor.execute('''INSERT INTO assets_in_layout(asset_id, layout_id) VALUES(?,?)''', (asset.id, self.main.selected_asset.id,))
                self.main.db.commit()

        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.readyRead.connect(self.readpro)
        self.houdini_hda_process.finished.connect(self.remove_assets_from_layout)
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_import_multiple_hdas_into_layout.py", self.main.selected_asset.full_path.replace("\\", "/"), "|".join(assets_to_add)])

    def remove_assets_from_layout(self):
        assets_to_remove = []
        for i in xrange(self.availableAssetsListWidget.count()):
            list_item = self.availableAssetsListWidget.item(i)
            asset = list_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            is_asset_in_layout = self.main.cursor.execute('''SELECT * FROM assets_in_layout WHERE asset_id=?''', (asset.id,)).fetchone()
            if is_asset_in_layout != None:
                assets_to_remove.append(asset.full_path)

        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.readyRead.connect(self.readpro)
        self.houdini_hda_process.finished.connect(self.process_finished)
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_delete_multiple_hda_from_lay.py", self.main.selected_asset.full_path.replace("\\", "/"), "|".join(assets_to_remove)])

    def process_finished(self):
        self.main.Lib.message_box(self.main, type="info", text="Assets have been succesfully imported/removed into/from layout scene!")
        self.houdini_hda_process.kill()
        self.main.statusLbl.setText("Status: Idle...")

    def readpro(self):
        while self.houdini_hda_process.canReadLine():
            out = self.houdini_hda_process.readLine()
            print(out)

class AddAssetsToAnimWindow(QtGui.QDialog, Ui_addAssetsToLayoutWidget):
    def __init__(self, main):
        super(AddAssetsToAnimWindow, self).__init__()

        self.main = main

        # Initialize the guis
        self.add_assets_layout = self.setupUi(self)
        self.main.Lib.apply_style(self.main, self)

        self.setWindowTitle("Add/remove assets to/from animation scene")
        self.addAssetsToLayoutBtn.setText("Add/remove assets to/from animation scene")

        # Connections
        self.availableAssetsListWidget.setDragEnabled(False)
        self.assetsToAddListWidget.setDragEnabled(False)
        self.availableAssetsListWidget.doubleClicked.connect(self.add_asset_to_list)
        self.assetsToAddListWidget.doubleClicked.connect(self.remove_asset_from_list)

        self.addAssetBtn.clicked.connect(self.add_asset_to_list)
        self.removeAssetBtn.clicked.connect(self.remove_asset_from_list)
        self.addAssetsToLayoutBtn.clicked.connect(self.add_remove_assets_to_anim)

        self.assets_in_anim = []
        self.assets_not_in_layout_db = []
        self.assets_in_layout_db = []

        self.get_assets_from_anim = QtCore.QProcess(self)
        self.get_assets_from_anim.readyRead.connect(self.get_assets_from_process_output)
        self.get_assets_from_anim.finished.connect(self.finished)
        self.get_assets_from_anim.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_get_assets_from_anm.py", self.main.selected_asset.full_path])

    def get_assets_from_process_output(self):
        while self.get_assets_from_anim.canReadLine():
            out = str(self.get_assets_from_anim.readLine())
            self.assets_in_anim.append(out)

    def finished(self):

        # Remove line breaks ("\n") from list
        self.assets_in_anim = [i.replace("\n", "").replace("HighRes", "") for i in self.assets_in_anim]

        # Get all layout assets from selected layout scene
        assets_id_from_db = self.main.cursor.execute('''SELECT asset_id FROM assets_in_layout WHERE layout_id=?''', (self.main.selected_layout_asset.id,)).fetchall()
        assets_id_from_db = [i[0] for i in assets_id_from_db]

        layout_assets = []
        for id in assets_id_from_db:
            try:
                asset = self.main.Asset(self.main, id, get_infos_from_id=True)
                layout_assets.append(asset)
            except:
                pass

        # Go through each asset and check if it is already in anim scene
        for asset in layout_assets:
            asset_filename = asset.path.split("\\")[-1].replace(".hda", "") # Get asset_filename (Ex: nat_xxx_xxxx_lay_pipe_out from \assets\lay\nat_xxx_xxxx_lay_pipe_out.hda)
            if not asset_filename in self.assets_in_anim:
                # Asset is not in anim scene, add it to assets_not_in_layout_db list
                self.assets_not_in_layout_db.append(asset)
            else:
                self.assets_in_layout_db.append(asset)


        # Add assets to list widget
        for asset in self.assets_not_in_layout_db:
            if asset.type != "lay":
                continue

            # Get version from which the modeling asset was published
            obj_asset_path = asset.full_path.replace("lay", "mod").replace("hda", "obj") # Get path of obj from modeling (Ex: \assets\mod\nat_xxx_xxxx_mod_pipe_out.obj)
            obj_asset_id = self.main.cursor.execute('''SELECT asset_id FROM assets WHERE asset_path=?''', (obj_asset_path.replace(self.main.selected_project_path, ""), )).fetchone()
            obj_asset = self.main.Asset(self.main, obj_asset_id[0], get_infos_from_id=True)

            # If asset has never been published, skip
            if obj_asset.number_of_publishes == 0:
                continue

            published_from_version = obj_asset.publish_from_version # Published_from_version = id of asset from which the modeling was published
            last_published_asset = self.main.Asset(self.main, published_from_version, get_infos_from_id=True)

            item = QtGui.QListWidgetItem(asset.name)
            # Get thumbnail from last published scene (Full thumbnail of version 05 (which is the version from which the last publish was made for example))
            if not os.path.isfile(last_published_asset.default_media_user):
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
            else:
                item.setIcon(QtGui.QIcon(last_published_asset.default_media_user))
            item.setData(QtCore.Qt.UserRole, (asset, last_published_asset.default_media_user))
            self.availableAssetsListWidget.addItem(item)


        for asset in self.assets_in_layout_db:
            # Get version from which the modeling asset was published
            obj_asset_path = asset.full_path.replace("lay", "mod").replace("hda", "obj")  # Get path of obj from modeling (Ex: \assets\mod\nat_xxx_xxxx_mod_pipe_out.obj)
            obj_asset_id = self.main.cursor.execute('''SELECT asset_id FROM assets WHERE asset_path=?''', (obj_asset_path.replace(self.main.selected_project_path, ""),)).fetchone()
            obj_asset = self.main.Asset(self.main, obj_asset_id[0], get_infos_from_id=True)

            # If asset has never been published, skip
            if obj_asset.number_of_publishes == 0:
                continue

            published_from_version = obj_asset.publish_from_version  # Published_from_version = id of asset from which the modeling was published
            last_published_asset = self.main.Asset(self.main, published_from_version, get_infos_from_id=True)

            item = QtGui.QListWidgetItem(asset.name)
            # Get thumbnail from last published scene (Full thumbnail of version 05 (which is the version from which the last publish was made for example))
            if not os.path.isfile(last_published_asset.default_media_user):
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
                item.setData(QtCore.Qt.UserRole, (asset, self.main.no_img_found))
            else:
                item.setIcon(QtGui.QIcon(last_published_asset.default_media_user))
                item.setData(QtCore.Qt.UserRole, (asset, last_published_asset.default_media_user))
            self.assetsToAddListWidget.addItem(item)

        self.exec_()

    def add_asset_to_list(self):
        for asset in self.availableAssetsListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.assetsToAddListWidget.addItem(item)

            # Remove item from left list
            self.availableAssetsListWidget.takeItem(self.availableAssetsListWidget.row(asset))

    def remove_asset_from_list(self):
        for asset in self.assetsToAddListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.availableAssetsListWidget.addItem(item)

            # Remove item from left list
            self.assetsToAddListWidget.takeItem(self.assetsToAddListWidget.row(asset))

    def add_remove_assets_to_anim(self):
        self.assets_to_add = []
        for i in xrange(self.assetsToAddListWidget.count()):
            item_to_add = self.assetsToAddListWidget.item(i)
            asset = item_to_add.data(QtCore.Qt.UserRole).toPyObject()[0]
            self.assets_to_add.append(asset.full_path.replace("\\", "/"))

        self.assets_to_remove = []
        for i in xrange(self.availableAssetsListWidget.count()):
            item_to_add = self.availableAssetsListWidget.item(i)
            asset = item_to_add.data(QtCore.Qt.UserRole).toPyObject()[0]
            self.assets_to_remove.append(asset.full_path.replace("\\", "/"))

        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(self.houdini_process_finished)
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_export_mod_in_place_from_lay.py", self.main.selected_layout_asset.full_path, "|".join(self.assets_to_add)])

    def houdini_process_finished(self):
        self.maya_ref_process = QtCore.QProcess(self)
        self.maya_ref_process.finished.connect(self.maya_process_finished)
        self.maya_ref_process.readyRead.connect(self.readydata)
        self.maya_ref_process.waitForFinished()
        self.maya_ref_process.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_import_obj_from_lay_as_ref.py", self.main.selected_asset.full_path, "|".join(self.assets_to_remove), "|".join(self.assets_to_add)])

    def maya_process_finished(self):
        self.main.Lib.message_box(self.main, type="info", text="Assets have been succesfully imported/removed into/from layout scene!")
        #self.houdini_hda_process.kill()
        #self.maya_ref_process.kill()

    def readydata(self):
        while self.maya_ref_process.canReadLine():
            out = self.maya_ref_process.readLine()
            print(out)

class AddRigsToAnimWindow(QtGui.QDialog, Ui_addAssetsToLayoutWidget):
    def __init__(self, main):
        super(AddRigsToAnimWindow, self).__init__()

        self.main = main

        # Initialize the guis
        self.add_assets_layout = self.setupUi(self)
        self.main.Lib.apply_style(self.main, self)

        self.setWindowTitle("Add/remove rigs to/from animation scene")
        self.addAssetsToLayoutBtn.setText("Add/remove rigs to/from animation scene")

        # Connections
        self.availableAssetsListWidget.setDragEnabled(False)
        self.assetsToAddListWidget.setDragEnabled(False)
        self.availableAssetsListWidget.doubleClicked.connect(self.add_asset_to_list)
        self.assetsToAddListWidget.doubleClicked.connect(self.remove_asset_from_list)

        self.addAssetBtn.clicked.connect(self.add_asset_to_list)
        self.removeAssetBtn.clicked.connect(self.remove_asset_from_list)
        self.addAssetsToLayoutBtn.clicked.connect(self.add_remove_assets_to_anim)

        self.assets_in_anim = []
        self.assets_not_in_layout_db = []
        self.assets_in_layout_db = []

        # GET ALL RIG ASSETS
        self.all_rig_assets_id = self.main.cursor.execute('''SELECT asset_id FROM assets WHERE asset_type="rig" AND asset_version="out"''').fetchall()  # Get IDs of all rig assets

        # GET ALL RIG ASSETS WHICH ARE IN ANIM SCENE
        self.assets_in_anim_id = self.main.cursor.execute('''SELECT asset_id FROM rigs_in_anim WHERE anim_asset_id=?''', (int(self.main.selected_asset.id),)).fetchall()  # Get IDs of rig assets in anim

        # Convert [(1,), (2,), (3)] to [1, 2, 3]
        if len(self.all_rig_assets_id) > 0:
            self.all_rig_assets_id = [i[0] for i in self.all_rig_assets_id]

        # Convert [(1,), (2,), (3)] to [1, 2, 3]
        if len(self.assets_in_anim_id) > 0:
            self.assets_in_anim_id = [i[0] for i in self.assets_in_anim_id]

        # Get assets not in layout by substracting assets in layout from all layout assets
        self.assets_not_in_layout_id = list(set(self.all_rig_assets_id) - set(self.assets_in_anim_id))

        # Get assets from IDs
        self.assets_in_layout = [self.main.Asset(self.main, i, get_infos_from_id=True) for i in self.assets_in_anim_id]
        self.assets_not_in_layout = [self.main.Asset(self.main, i, get_infos_from_id=True) for i in self.assets_not_in_layout_id]

        for asset in self.assets_not_in_layout:
            last_rig_version_id = self.main.cursor.execute('''SELECT MAX(asset_id) FROM assets WHERE asset_name=? AND asset_type="rig" AND asset_version!="out"''', (asset.name,)).fetchone()
            last_rig_asset = self.main.Asset(self.main, last_rig_version_id[0], get_infos_from_id=True)
            img = last_rig_asset.default_media_user

            item = QtGui.QListWidgetItem(asset.name)
            if os.path.isfile(img):
                item.setIcon(QtGui.QIcon(img))
            else:
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
                img = self.main.no_img_found

            item.setData(QtCore.Qt.UserRole, (asset, img))

            self.availableAssetsListWidget.addItem(item)

        for asset in self.assets_in_layout:
            if asset.type != "rig":
                continue
            last_rig_version_id = self.main.cursor.execute('''SELECT MAX(asset_id) FROM assets WHERE asset_name=? AND asset_type="rig" AND asset_version!="out"''', (asset.name,)).fetchone()
            last_rig_asset = self.main.Asset(self.main, last_rig_version_id[0], get_infos_from_id=True)
            img = last_rig_asset.default_media_user

            item = QtGui.QListWidgetItem(asset.name)
            if os.path.isfile(img):
                item.setIcon(QtGui.QIcon(img))
            else:
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
                img = self.main.no_img_found

            item.setData(QtCore.Qt.UserRole, (asset, img))

            self.assetsToAddListWidget.addItem(item)


        self.exec_()

    def add_asset_to_list(self):
        for asset in self.availableAssetsListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.assetsToAddListWidget.addItem(item)

            # Remove item from left list
            self.availableAssetsListWidget.takeItem(self.availableAssetsListWidget.row(asset))

    def remove_asset_from_list(self):
        for asset in self.assetsToAddListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.availableAssetsListWidget.addItem(item)

            # Remove item from left list
            self.assetsToAddListWidget.takeItem(self.assetsToAddListWidget.row(asset))

    def add_remove_assets_to_anim(self):
        self.rigs_to_add = []
        for i in xrange(self.assetsToAddListWidget.count()):
            item_to_add = self.assetsToAddListWidget.item(i)
            asset = item_to_add.data(QtCore.Qt.UserRole).toPyObject()[0]
            self.rigs_to_add.append(asset.full_path.replace("\\", "/"))
            # Add entry to assets in layout database
            self.main.cursor.execute('''INSERT INTO rigs_in_anim(asset_id, anim_asset_id) VALUES(?,?)''', (asset.id, self.main.selected_asset.id,))
            self.main.db.commit()

        self.rigs_to_remove = []
        for i in xrange(self.availableAssetsListWidget.count()):
            item_to_add = self.availableAssetsListWidget.item(i)
            asset = item_to_add.data(QtCore.Qt.UserRole).toPyObject()[0]
            self.rigs_to_remove.append(asset.full_path.replace("\\", "/"))

        self.maya_rig_process = QtCore.QProcess(self)
        self.maya_rig_process.readyRead.connect(self.raraaa)
        self.maya_rig_process.finished.connect(self.maya_process_finished)
        self.maya_rig_process.waitForFinished()
        self.maya_rig_process.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_add_remove_rig_from_anm.py", self.main.selected_asset.full_path, "|".join(self.rigs_to_add), "|".join(self.rigs_to_remove)])

    def raraaa(self):
        while self.maya_rig_process.canReadLine():
            print(self.maya_rig_process.readLine())

    def maya_process_finished(self, asset_id):
        self.main.Lib.message_box(self.main, type="info", text="Rigs have been succesfully imported/removed into/from layout scene!")
        # self.houdini_hda_process.kill()
        # self.maya_ref_process.kill()

    def readydata(self):
        while self.maya_ref_process.canReadLine():
            out = self.maya_ref_process.readLine()
            print(out)


