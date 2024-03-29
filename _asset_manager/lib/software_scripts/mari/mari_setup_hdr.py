import glob
import os
import mari
import PythonQt.QtGui as gui
import PythonQt.QtCore as core

class Hdr_Manager(gui.QDialog):
    def __init__(self):
        super(Hdr_Manager, self).__init__()
        self.hdr = mari.lights.list()[4]
        self.hdr_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\_prefs\\houdini\\houdini14.0\\ressources\\HDR"
        self.thumb_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\_prefs\\houdini\\houdini14.0\\ressources\\HDR\\thumb"
        self.hdr_list = []


        self.UI()
        self.show()

    def UI(self):

        self.setWindowTitle("HDR Choice")
        main_layout = gui.QHBoxLayout(self)

        #Left Layout
        self.left_group = gui.QGroupBox(self)
        self.left_group_layout = gui.QGridLayout(self)
        self.left_group.setLayout(self.left_group_layout)

        #HDR Combobox
        self.hdr_combobox = gui.QComboBox()

        os.chdir(self.hdr_path)
        for file in glob.glob("*.HDR"):     #Get HDR in folder
            split_file = file.split(".")[0]
            self.hdr_list.append(split_file)

        num = 0
        for maps in self.hdr_list:          #Add Maps in combobox
            self.hdr_combobox.insertItem(num, maps)
            num = num + 1
        self.left_group_layout.addWidget(self.hdr_combobox)

        # #Thumbnail viewer
        self.thumb_view = gui.QLabel()
        self.selection = self.hdr_combobox.currentText
        self.pixmap = gui.QPixmap(self.thumb_path + "\\" + self.selection + "_thumb.jpg")
        self.thumb_view.setPixmap(self.pixmap)
        self.left_group_layout.addWidget(self.thumb_view)

        self.hdr_combobox.connect("currentIndexChanged(int)", self.change_hdr_pixmap)

        #Apply HDR
        apply_hdr = gui.QPushButton("Apply HDR")
        self.left_group_layout.addWidget(apply_hdr)
        apply_hdr.connect( "clicked()", self.applyHDR)

        # Add Layout to main
        main_layout.addWidget(self.left_group)


    def applyHDR(self):
        self.selection = self.hdr_combobox.currentText
        self.hdr.setCubeImage(self.hdr_path + "\\" + self.selection + ".hdr", 2)

    def change_hdr_pixmap(self):
        selected_hdr = self.hdr_combobox.currentText
        self.pixmap = gui.QPixmap(self.thumb_path + "\\" + selected_hdr + "_thumb.jpg")
        self.thumb_view.setPixmap(self.pixmap)


MainWindow = Hdr_Manager()
MainWindow.show()