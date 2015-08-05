#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import unicodedata
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import subprocess
import os
import collections
import ctypes
import sys
from threading import Thread
import time
import distutils.core
import shutil
from datetime import datetime
import smtplib
from dateutil import relativedelta


class Lib(object):

    def create_thumbnails(self, obj_path="", thumbs_to_create="", version=""):

        self.updateThumbBtn.setEnabled(False)

        self.full_obj_path = obj_path
        self.obj_tmp_path = "C:\\Temp\\" + obj_path.split("\\")[-1]
        self.type = type
        self.version = version
        self.i = 0

        self.thumbnailProgressBar.show()
        self.thumbnailProgressBar.setValue(0)

        self.thumbs_to_create = thumbs_to_create

        if "full" in self.thumbs_to_create:
            self.type = "full"
            self.sampling = 100
            self.resolution = 50
            self.thumbs_to_create = thumbs_to_create.replace("full", "")
        elif "quad" in self.thumbs_to_create:
            self.type = "quad"
            self.sampling = 25
            self.resolution = 50
            self.thumbs_to_create = thumbs_to_create.replace("quad", "")
        elif "turn" in self.thumbs_to_create:
            self.type = "turn"
            self.sampling = 10
            self.resolution = 50
            self.thumbs_to_create = thumbs_to_create.replace("turn", "")

        if self.type == "full":
            self.thumbnailProgressBar.setMaximum(67 + int(self.sampling))
        elif self.type == "quad":
            self.thumbnailProgressBar.setMaximum(211 + (int(self.sampling) * 4))
        elif self.type == "turn":
            self.thumbnailProgressBar.setMaximum(1171 + (int(self.sampling) * 20))

        if self.type == "quad":
            self.resolution = str(int(self.resolution) / 2)

        if os.path.getsize(self.full_obj_path) < 100:
            self.message_box(type="warning", text="It looks like the published modeling is nothing. Make sure you model something before trying to make a thumbnail out of it!")
            return

        self.create_thumbnail_process = QtCore.QProcess(self)
        self.create_thumbnail_process.readyReadStandardOutput.connect(self.create_thumbnail_new_data)
        self.create_thumbnail_process.setProcessChannelMode(QtCore.QProcess.SeparateChannels)
        self.create_thumbnail_process.finished.connect(self.create_thumbnail_finished)
        self.create_thumbnail_process.start("C:/Program Files/Blender Foundation/Blender/blender.exe", ["-b",self.cur_path + "\\lib\\thumbnailer\\Thumbnailer.blend", "--python-text",
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

    def create_thumbnail_finished(self):

        if self.type == "full":
            filename = self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg")
            self.compress_image(filename, int(1920 * float(self.resolution) / 100), 90)
            thumb_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_full.jpg")
            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg"), thumb_filename)
            os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg"))

        elif self.type == "quad":
            full_scale_width = int(1920 * float(self.resolution) * 2 / 100)
            full_scale_height = int(1152 * float(self.resolution) * 2 / 100)

            quad_scale_width = int(1920 * float(self.resolution) / 100)
            quad_scale_height = int(1152 * float(self.resolution) / 100)

            im = Image.new("RGB", (full_scale_width, full_scale_height), "black")

            view01 = Image.open(self.obj_tmp_path.replace("out.obj", self.version + "_000.jpg"))
            view02 = Image.open(self.obj_tmp_path.replace("out.obj", self.version + "_090.jpg"))
            view03 = Image.open(self.obj_tmp_path.replace("out.obj", self.version + "_180.jpg"))
            view04 = Image.open(self.obj_tmp_path.replace("out.obj", self.version + "_270.jpg"))

            # get the correct size

            im.paste(view01, (0, 0))
            im.paste(view02, (quad_scale_width, 0))
            im.paste(view03, (0, quad_scale_height))
            im.paste(view04, (quad_scale_width, quad_scale_height))

            im.save(self.obj_tmp_path.replace("out.obj", self.version + "_quad.jpg"), "JPEG", quality=100, optimize=True, progressive=True)
            thumb_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_quad.jpg")
            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_quad.jpg"), thumb_filename)
            os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_quad.jpg"))

            for i in range(0, 360, 90):
                os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_" + str(i).zfill(3) + ".jpg"))


        elif self.type == "turn":
            file_sequence = self.obj_tmp_path.replace("out.obj", self.version + "_%02d.jpg")
            movie_path = self.obj_tmp_path.replace("out.obj", self.version + "_turn.mp4")
            subprocess.call(
                [self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-i", file_sequence, "-vcodec", "libx264", "-y", "-r", "24",
                 movie_path])

            thumb_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_turn.mp4")
            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_turn.mp4"), thumb_filename)
            os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_turn.mp4"))
            for i in range(24):
                os.remove(self.obj_tmp_path.replace("out.obj", "_" + str(i).zfill(2) + ".jpg"))

        self.create_thumbnail_process.kill()
        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())

        if len(self.thumbs_to_create) > 0:
            self.create_thumbnails(self.full_obj_path, self.thumbs_to_create)
        else:
            thumb_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_full.jpg")
            qpixmap = QtGui.QPixmap(thumb_filename)
            qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(thumb_filename)
            self.assetImg.setPixmap(qpixmap)
            self.thumbnailProgressBar.hide()
            self.updateThumbBtn.setEnabled(True)

    def setup_user_session(self):
        if os.path.exists("H:\\plugins"):
            shutil.rmtree("H:\\plugins")
        distutils.dir_util.copy_tree(self.cur_path_one_folder_up + "\\_setup\\plugins", "H:\\plugins")

    def message_box(self, type="Warning", text="warning", no_button=False, exec_now=True):

        self.msgBox = QtGui.QMessageBox()
        self.msgBox.setWindowIcon(self.app_icon)

        self.Lib.apply_style(self, self.msgBox)

        self.msgBox.setWindowTitle("Manager")
        self.msgBox.setText(text)

        self.msgBox_okBtn = self.msgBox.addButton(QtGui.QMessageBox.Ok)
        self.msgBox_okBtn.setStyleSheet("width: 64px;")
        self.msgBox.setDefaultButton(self.msgBox_okBtn)
        self.msgBox_okBtn.clicked.connect(self.msgBox.accept)

        if no_button == True:
            self.msgBox_noBtn = self.msgBox.addButton(QtGui.QMessageBox.No)
            self.msgBox_noBtn.setStyleSheet("width: 64px;")
            self.msgBox_noBtn.clicked.connect(self.msgBox.reject)

        if type == "warning":
            self.msgBox.setIcon(QtGui.QMessageBox.Warning)
        elif type == "error":
            self.msgBox.setIcon(QtGui.QMessageBox.Critical)
        elif type == "info":
            self.msgBox.setIcon(QtGui.QMessageBox.Information)

        if exec_now == True:
            return self.msgBox.exec_()
        else:
            return self.msgBox

    def thumbnail_creation_box(self, text=""):
        self.thumbnail_creation_box = QtGui.QMessageBox()
        self.thumbnail_creation_box.setWindowIcon(self.app_icon)
        self.Lib.apply_style(self, self.thumbnail_creation_box)

        self.thumbnail_creation_box.setWindowTitle("Manager")
        self.thumbnail_creation_box.setText(text)

        self.thumbnail_creation_box_okBtn = self.thumbnail_creation_box.addButton(QtGui.QMessageBox.Ok)
        self.thumbnail_creation_box_noBtn = self.thumbnail_creation_box.addButton(QtGui.QMessageBox.No)
        self.thumbnail_creation_box_okBtn.setStyleSheet("width: 64px;")
        self.thumbnail_creation_box_noBtn.setStyleSheet("width: 64px;")
        self.thumbnail_creation_box_okBtn.clicked.connect(self.thumbnail_creation_box.accept)
        self.thumbnail_creation_box.setDefaultButton(self.thumbnail_creation_box_okBtn)

        return self.thumbnail_creation_box.exec_()

    def center_window(self):
        """
        Move the window to the center of the screen

        """
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2) + 400, (resolution.height() / 2) - (self.frameSize().height() / 2) + 50)
        self.setFixedSize(0, 0)

    def open_in_explorer(self):
        """
        Open selected assets in explorer
        """
        subprocess.Popen(r'explorer /select,' + str(self.assetPathLbl.text()))

    def apply_style(self, form):

        form.setWindowFlags(form.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)

        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile(self.cur_path + "\\media\\favicon_cube.png", QtCore.QSize(16, 16))
        form.setWindowIcon(app_icon)

        if int(self.theme) == 0:
            # Apply custom CSS to msgBox
            css = QtCore.QFile(self.cur_path + "\\media\\style.css")
            css.open(QtCore.QIODevice.ReadOnly)
            if css.isOpen():
                form.setStyleSheet(QtCore.QVariant(css.readAll()).toString().replace("checkbox|placeholder", self.cur_path.replace("\\", "/") + "/media/checkbox.png"))
            css.close()

        elif int(self.theme) == 2:
            form.setStyle(QtGui.QStyleFactory.create("plastique"))

        elif int(self.theme) == 0:
            form.setStyle(QtGui.QStyleFactory.create("cleanlooks"))

    def normalize_str(self, data):
        try:
            data = unicode(data, "utf-8")
        except:
            pass
        return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')

    def convert_to_camel_case(self, str):
        str = str.lower()
        str = str.replace("(", "")
        str = str.replace(")", "")
        str = str.replace("'", "")
        str = str.replace("_", " ")
        str = str.replace("-", " ")
        str = str.replace(":", "")
        str = str.replace(";", "")
        str = str.replace("|", "")
        str = str.replace("#", "")
        str = str.replace("!", "")
        str = str.replace("?", "")
        str = str.replace("0", "")
        str = str.replace("1", "")
        str = str.replace("2", "")
        str = str.replace("3", "")
        str = str.replace("4", "")
        str = str.replace("5", "")
        str = str.replace("6", "")
        str = str.replace("7", "")
        str = str.replace("8", "")
        str = str.replace("9", "")
        liste = str.split(" ")
        liste = filter(None, liste)
        liste_finale = []
        for i, item in enumerate(liste):
            if i != 0:
                uppercase_str = item[0].upper() + item[1:len(item)]
                liste_finale.append(uppercase_str)
            else:
                liste_finale.append(item)

        str = "".join(liste_finale)
        return str

    def compress_image(self, image_path, width, quality):
        basewidth = width
        img = Image.open(image_path)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        img.save(image_path, 'JPEG', quality=quality)

    def take_screenshot(self, path):

        self.hide()

        # constants
        SCREEN_GRABBER = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\screenshot_grabber\\MiniCap.exe"

        # filename
        file_name = path

        # run the screen grabber
        subprocess.call([SCREEN_GRABBER, '-captureregselect', '-exit', '-save', file_name])
        #winsound.PlaySound("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\screenshot_grabber\\camera.wav", winsound.SND_FILENAME)

        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()

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
                return '%.3f' % (value)
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

    def add_watermark(self, in_file, text, out_file='watermark.jpg', angle=0, opacity=0.75):
        font = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\arial.ttf"
        img = Image.open(in_file).convert('RGB')
        watermark = Image.new('RGBA', img.size, (0,0,0,0))
        size = 2
        n_font = ImageFont.truetype(font, size)
        n_width, n_height = n_font.getsize(text)
        while n_width+n_height < watermark.size[0]:
            size += 2
            n_font = ImageFont.truetype(font, size)
            n_width, n_height = n_font.getsize(text)
        draw = ImageDraw.Draw(watermark, 'RGBA')
        draw.text(((watermark.size[0] - n_width) / 2,
                   (watermark.size[1] - n_height) / 2),
                  text, font=n_font)
        watermark = watermark.rotate(angle,Image.BICUBIC)
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
        Image.composite(watermark, img, watermark).save(out_file, 'JPEG')

    def reference_check_if_projSeqShot_is_selected(self):


        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.message_box(text="Please select a project first")
            return None, None

        # Check if a sequence is selected
        if len(self.seqReferenceList.selectedItems()) == 0:
            selected_sequence = "xxx"
        else:
            selected_sequence = str(self.seqReferenceList.selectedItems()[0].text())
            if selected_sequence == "All" or selected_sequence == "None": selected_sequence = "xxx"

        # Check if a shot is selected
        if len(self.shotReferenceList.selectedItems()) == 0:
            selected_shot = "xxxx"
        else:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
            if selected_shot == "All" or selected_shot == "None": selected_shot = "xxxx"


        return selected_sequence, selected_shot

    def get_diff_between_lists(self, list1, list2):
        c = set(list1).union(set(list2))
        d = set(list1).intersection(set(list2))
        return list(c - d)

    def modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.fromtimestamp(t)

    def add_entry_to_log(self, members_list="", members_concerned="", asset_id=0, type="", description=""):
        if members_list == "All":
            members_list = self.members.keys()

        members_list = ["|{0}|".format(member) for member in members_list]
        members_list = "".join(members_list)

        if members_concerned == "All":
            members_concerned = self.members.keys()

        members_concerned = ["|{0}|".format(member) for member in members_concerned]
        members_concerned = "".join(members_concerned)

        self.cursor.execute('''INSERT INTO log(log_dependancy, viewed_by, members_concerned, log_type, log_description) VALUES(?,?,?,?,?)''', (asset_id, members_list, members_concerned, type, description))
        self.db.commit()

    def remove_log_entry_from_asset_id(self, asset_id, type=None):
        if type != None:
            self.cursor.execute('''DELETE FROM log WHERE log_dependancy=? AND log_type=?''', (asset_id, type))
        else:
            self.cursor.execute('''DELETE FROM log WHERE log_dependancy=?''', (asset_id,))
        self.db.commit()

    def read_process_data(self, process):
        while process.canReadLine():
            out = process.readLine()
            print(out)

    def send_email(self, from_addr="nad.update@gmail.com", addr_list=[], subject="", message="", login="nad.update@gmail.com", password="python123", username=""):

        subject = unicode(self.utf8_codec.fromUnicode(subject), 'utf-8').encode('utf-8')
        message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8').encode('utf-8')

        smtpserver = 'smtp.gmail.com:25'
        header = 'From: {0}\n'.format(from_addr)
        header += 'To: %s\n' % ','.join(addr_list)
        header += 'Subject: {0} par {1}\n\n'.format(subject, username)
        message = header + message + "\nEnvoyé par " + username + " depuis Manager 2.0"

        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(login, password)
        problems = server.sendmail(from_addr, addr_list, message)
        server.quit()

        self.message_box(type="info", text="Mail successfully sent!")

    def check_last_active(self):
        for member in self.members.keys():
            last_active = self.cursor.execute('''SELECT last_active FROM preferences WHERE username=?''', (member,)).fetchone()
            self.last_active = last_active[0]
            now = datetime.now()
            date = self.last_active.split(" ")[0]
            time = self.last_active.split(" ")[-1]
            day = date.split("/")[0]
            month = date.split("/")[1]
            year = date.split("/")[2]
            hour = time.split(":")[0]
            minutes = time.split(":")[1]
            self.last_active_as_date = datetime(int(year), int(month), int(day), int(hour), int(minutes))

            last_active_period = relativedelta.relativedelta(now, self.last_active_as_date)
            if last_active_period.minutes >= 1:
                self.cursor.execute('''UPDATE preferences SET is_online=0 WHERE username=?''', (member,))
            else:
                self.cursor.execute('''UPDATE preferences SET is_online=1 WHERE username=?''', (member,))

class DesktopWidget(QtGui.QWidget):

    def __init__(self, task_name, task_department, task_status, task_start, task_end, task_bid):
        super(DesktopWidget, self).__init__()

        self.DesktopWidget_status = {"Ready to Start": 0, "In Progress": 1, "On Hold": 2, "Waiting for Approval": 3, "Retake": 4,
                       "Done": 5}

        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\favicon.png", QtCore.QSize(16, 16))
        self.setWindowIcon(app_icon)

        self.top = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("My Tasks - Desktop Widget")

        self.setStyleSheet("background: rgb(222, 222, 222);")

        self.layout = QtGui.QHBoxLayout(self)

        self.taskNameLbl = QtGui.QLabel(task_name)
        self.taskNameLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskNameLbl)

        self.add_separator()

        self.taskDepartmentLbl = QtGui.QLabel(task_department)
        self.taskDepartmentLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskDepartmentLbl)

        self.add_separator()

        self.statusComboBox = QtGui.QComboBox()
        self.statusComboBox.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake", "Done"])
        self.statusComboBox.setCurrentIndex(self.DesktopWidget_status[task_status])
        self.change_cell_status_color(self.statusComboBox, task_status)
        self.layout.addWidget(self.statusComboBox)

        self.add_separator()

        self.taskStartLbl = QtGui.QLabel("Start: " + task_start)
        self.taskStartLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskStartLbl)

        self.add_separator()

        self.taskEndLbl = QtGui.QLabel("End: " + task_end)
        self.taskEndLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskEndLbl)

        self.add_separator()

        self.taskBidtLbl = QtGui.QLabel(task_bid + " days left")
        self.taskBidtLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskBidtLbl)

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
        line_01.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(line_01)

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        try:
            x=event.globalX()
            y=event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x-x_w, y-y_w)
        except:
            pass

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

class CheckNews(QtCore.QThread):
    def __init__(self, main):
        QtCore.QThread.__init__(self)

    def run(self):
        while True:
            self.emit(QtCore.SIGNAL("refresh_all"))
            time.sleep(10)



if __name__ == "__main__":
    test = Lib()
    test.send_email()


    # app = QtGui.QApplication(sys.argv)
    # test = Lib()
    # test.create_thumbnails(obj_path="Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\lib\\thumbnailer\\statue.obj", type="quad", sampling="100", resolution="10")
    # app.exit()