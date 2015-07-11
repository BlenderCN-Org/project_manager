#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import unicodedata
import PIL
from PIL import Image
import subprocess
import winsound
import os
import collections
import ctypes
import sys

class Lib(object):

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
        self.msgBox.setWindowIcon(self.app_icon)

        # Apply custom CSS to msgBox
        css = QtCore.QFile(self.cur_path + "\\media\\style.css")
        css.open(QtCore.QIODevice.ReadOnly)
        if css.isOpen():
            self.msgBox.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
        css.close()

        self.msgBox.setWindowTitle("Warning!")
        self.msgBox.setText(text)

        self.msgBox_okBtn = self.msgBox.addButton(QtGui.QMessageBox.Ok)
        self.msgBox_okBtn.setStyleSheet("width: 64px;")
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

    def apply_style(self, form):


        # Apply custom CSS to msgBox
        css = QtCore.QFile(self.cur_path + "\\media\\style.css")
        css.open(QtCore.QIODevice.ReadOnly)
        if css.isOpen():
            form.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
        css.close()

        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile(self.cur_path + "\\media\\favicon.png", QtCore.QSize(16, 16))
        form.setWindowIcon(app_icon)

    def normalize_str(self, data):
        try:
            data = unicode(data, "utf-8")
        except:
            pass
        return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')

    def convert_to_camel_case(self, str):
        str = str
        liste = str.split(" ")
        liste_finale = []
        for i, item in enumerate(liste):
            if i != 0:
                uppercase_str = item[0].upper() + item[1:len(item)]
                liste_finale.append(uppercase_str)
            else:
                liste_finale.append(item)

        str = "".join(liste_finale)
        str = str.replace("'", "")
        str = str.replace("_", "")
        str = str.replace("-", "")
        return str

    def compress_image(self, image_path, width, quality):
        basewidth = width
        img = Image.open(image_path)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        img.save(image_path, 'JPEG', quality=quality)

    def take_screenshot(self, path="H:\\01-NAD\\Session-06\\_pipeline\\_utilities\\_database\\screenshots", name="tmp"):

        # constants
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        SCREEN_GRABBER = cur_dir + "\\screenshot_grabber\\MiniCap.exe"

        # filename
        extension = ".jpg"
        file_name = path + "\\" + name + extension

        # run the screen grabber
        subprocess.call([SCREEN_GRABBER, '-captureregselect', '-exit', '-save', file_name])
        winsound.PlaySound(cur_dir + "\\screenshot_grabber\\camera.wav", winsound.SND_FILENAME)

    def fit_range(self, base_value=2.5, base_min=0, base_max=5, limit_min=0, limit_max=1):
        return ((limit_max - limit_min) * (base_value - base_min) / (base_max - base_min)) + limit_min

    def disk_usage(self, path):
        _ntuple_diskusage = collections.namedtuple('usage', 'total used free')
        _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), \
                           ctypes.c_ulonglong()
        if sys.version_info >= (3,) or isinstance(path, unicode):
            fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
        else:
            fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA
        ret = fun(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
        if ret == 0:
            raise ctypes.WinError()
        used = total.value - free.value
        return _ntuple_diskusage(total.value, used, free.value)

    def bytes2human(self, n):
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i+1)*10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f' % (value)
        return "%sB" % n

    def get_folder_space(self, path="Z:\\Groupes-cours\\NAND999-A15-N01\\Nature"):
        usage = self.disk_usage(path)
        return self.bytes2human(usage.total)

    def get_files_from_folder(self, path):
        files_list = []
        folder_path = path

        for (dir, _, files) in os.walk(folder_path):
            for f in files:
                path = os.path.join(dir, f)
                if os.path.exists(path):
                    files_list.append(path)

        return files_list

class DesktopWidget(QtGui.QWidget):

    def __init__(self, task_name):
        super(DesktopWidget, self).__init__()


        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\favicon.png", QtCore.QSize(16, 16))
        self.setWindowIcon(app_icon)

        self.top = True
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("My Tasks - Desktop Widget")

        self.setStyleSheet("background: rgb(30, 30, 30);")

        self.layout = QtGui.QHBoxLayout(self)

        self.taskNameLbl = QtGui.QLabel(task_name)
        self.taskNameLbl.setStyleSheet("color: #fff;")
        self.layout.addWidget(self.taskNameLbl)

        self.add_separator()

        self.taskDepartmentLbl = QtGui.QLabel("Modeling")
        self.taskDepartmentLbl.setStyleSheet("color: #fff;")
        self.layout.addWidget(self.taskDepartmentLbl)

        self.layout.setContentsMargins(12, 12, 12, 12)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)


    def showMenu(self, pos):

        self.widget_menu=QtGui.QMenu(self)
        self.action_top = QtGui.QAction("Always on top", self.widget_menu)
        self.action_close = QtGui.QAction("Close", self.widget_menu)
        self.action_top.triggered.connect(self.always_on_top)
        self.action_close.triggered.connect(self.close_widget)
        self.widget_menu.addAction(self.action_top)
        self.widget_menu.addAction(self.action_close)
        self.widget_menu.popup(self.mapToGlobal(pos))
        self.widget_menu.setStyleSheet("QMenu::item {color: black;}")
        self.widget_menu.setStyleSheet("QMenu {color: white;}")

    def close_widget(self):
        self.close()

    def always_on_top(self):
        if self.top == False:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.show()
            self.top = True
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
            self.show()
            self.top = False

    def add_separator(self):
        line_01 = QtGui.QFrame()
        line_01.setFrameShape(QtGui.QFrame.VLine)
        line_01.setLineWidth(1)
        line_01.setStyleSheet("color: #fff;")
        self.layout.addWidget(line_01)

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        x=event.globalX()
        y=event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)
