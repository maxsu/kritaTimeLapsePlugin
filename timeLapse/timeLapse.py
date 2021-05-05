
from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import subprocess
import os

class timeLapseDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.recState = "notRecording"
        self.fieldPath = QLineEdit()
        self.fieldFFMPath = QLineEdit()
        self.fieldName = QLineEdit()

        self.setWindowTitle("Time Lapse")
        self.mainWidget = QWidget(self)
        RGBWidget = QWidget(self)
        self.setWidget(self.mainWidget)
        hLayout = QHBoxLayout()
        gLayout = QGridLayout()
        self.mainWidget.setLayout(gLayout)
        RGBWidget.setLayout(hLayout)

        self.saveCounter = 1
        self.timer = QTimer()
        self.timer.timeout.connect(self.saveImage)

        self.buttonStartRecording = QPushButton("Start")
        self.buttonStartRecording.clicked.connect(self.startRec)
        self.buttonStartRecording.setEnabled(True)
        self.buttonStopRecording = QPushButton("Stop")
        self.buttonStopRecording.clicked.connect(self.stopRec)
        self.buttonStopRecording.setEnabled(False)

        self.checkBoxAlpha = QCheckBox("Alpha")
        self.checkBoxForceSRGB = QCheckBox("Force SRGB")
        self.checkBoxInterlaced = QCheckBox("Interlaced")
        self.checkBoxSaveSRGBProfile = QCheckBox("Save SRGB Profile")

        self.fieldCompression = QSpinBox()
        self.fieldCompression.setRange(1,9)
        self.fieldCompression.setPrefix("Compression -  ")
        self.fieldFPS = QSpinBox()
        self.fieldFPS.setRange(24,60)
        self.fieldFPS.setPrefix("Frames per second -  ")
        self.fieldImageInterval = QSpinBox()
        self.fieldImageInterval.setRange(10,7200)
        self.fieldImageInterval.setPrefix("Take an image every  ")
        self.fieldImageInterval.setSuffix("  seconds")

        rx = QRegExp("(C|D):\\\\([a-zA-Z-\d._ ]+\\\\*)*")
        validator = QRegExpValidator(rx, self)

        self.PathLabel = QLabel("Path:  ")
        self.FFMPathLabel = QLabel("FFmpeg Path:")
        self.fieldPath.setValidator(validator)
        self.fieldFFMPath.setValidator(validator)
        self.nameLabel = QLabel("Name: ")


        self.RGBLabel = QLabel("Transparency Fillcolor: ")
        self.RField = QSpinBox()
        self.RField .setRange(0,255)
        self.RField.setPrefix("R  ")

        self.GField = QSpinBox()
        self.GField.setRange(0,255)
        self.GField.setPrefix("G  ")

        self.BField = QSpinBox()
        self.BField.setRange(0,255)
        self.BField.setPrefix("B  ")

        RGBWidget.layout().addWidget(self.RGBLabel)
        RGBWidget.layout().addWidget(self.RField)
        RGBWidget.layout().addWidget(self.GField)
        RGBWidget.layout().addWidget(self.BField)

        self.mainWidget.layout().addWidget(self.fieldCompression,0,0)
        self.mainWidget.layout().addWidget(self.fieldFPS,0,1)
        self.mainWidget.layout().addWidget(self.fieldImageInterval,1,0,1,2)
        self.mainWidget.layout().addWidget(RGBWidget,2,0,1,2)

        self.mainWidget.layout().addWidget(self.checkBoxAlpha,3,0)
        self.mainWidget.layout().addWidget(self.checkBoxForceSRGB,4,0)
        self.mainWidget.layout().addWidget(self.checkBoxInterlaced,3,1)
        self.mainWidget.layout().addWidget(self.checkBoxSaveSRGBProfile,4,1)

        self.mainWidget.layout().addWidget(self.buttonStartRecording,5,0,)
        self.mainWidget.layout().addWidget(self.buttonStopRecording,5,1)

        self.mainWidget.layout().addWidget(self.PathLabel,6,0)
        self.mainWidget.layout().addWidget(self.fieldPath,6,1)
        self.mainWidget.layout().addWidget(self.nameLabel,7,0)
        self.mainWidget.layout().addWidget(self.fieldName,7,1)
        self.mainWidget.layout().addWidget(self.FFMPathLabel,8,0)
        self.mainWidget.layout().addWidget(self.fieldFFMPath,8,1)

    def startRec(self):

        if (self.recState == "notRecording"):
            self.recState = "recording"
            self.buttonStopRecording.setEnabled(True)
            self.setUiEnabled(False)
            self.buttonStartRecording.setText("Pause")
            if not(os.path.isdir(self.fieldPath.text()+"\\"+self.fieldName.text())):
                os.mkdir(self.fieldPath.text()+"\\"+self.fieldName.text())
            self.iO = krita.InfoObject()
            self.iO.setProperties({
                "alpha":self.checkBoxAlpha.isChecked(),
                "compression":self.fieldCompression.value(),
                "forceSRGB":self.checkBoxForceSRGB.isChecked(),
                "indexed":True,"interlaced":self.checkBoxInterlaced.isChecked(),
                "saveSRGBProfile":self.checkBoxSaveSRGBProfile.isChecked(),
                "transparencyFillcolor":[self.RField.value(),self.GField.value(),self.BField.value()]
            })
            self.doc = Krita.instance().activeDocument()
            self.doc.setBatchmode(True)
            self.timer.start(self.fieldImageInterval.value()*1000)

        elif (self.recState == "pause"):
            self.timer.start(self.fieldImageInterval.value()*1000)
            self.buttonStartRecording.setText("Pause")
            self.buttonStopRecording.setEnabled(True)
            self.recState = "recording"
        elif (self.recState == "recording"):
            self.timer.stop()
            self.buttonStartRecording.setText("Resume")
            self.buttonStopRecording.setEnabled(False)
            self.recState = "pause"



    def stopRec(self):
        self.recState = "notRecording"
        self.timer.stop()
        self.saveImage()
        self.saveCounter = 0
        self.buttonStartRecording.setEnabled(True)
        self.buttonStartRecording.setText("Start")
        self.buttonStopRecording.setEnabled(False)
        self.setUiEnabled(True)
        ffmpegpath = self.fieldFFMPath.text()
        framerate = str(self.fieldFPS.value())
        width = str(self.doc.width())
        height = str(self.doc.height())
        path = self.fieldPath.text()
        name = self.fieldName.text()
        subprocess.run(f"{ffmpegpath}\\ffmpeg.exe -r {framerate} -f image2 -s {width}x{height} -i {path}\\{name}\%d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p {path}\\{name}\\_TimeLapse.mp4")

    def setUiEnabled(self, x: bool ):
        self.fieldFPS.setEnabled(x)
        self.fieldPath.setEnabled(x)
        self.fieldFFMPath.setEnabled(x)
        self.fieldCompression.setEnabled(x)
        self.fieldImageInterval.setEnabled(x)
        self.BField.setEnabled(x)
        self.GField.setEnabled(x)
        self.RField.setEnabled(x)
        self.checkBoxAlpha.setEnabled(x)
        self.checkBoxForceSRGB.setEnabled(x)
        self.checkBoxInterlaced.setEnabled(x)
        self.checkBoxSaveSRGBProfile.setEnabled(x)
        self.fieldName.setEnabled(x)

    def saveImage(self):
        counter = self.saveCounter
        if (self.doc.exportImage(self.fieldPath.text()+"\\"+self.fieldName.text()+f"\\{counter}.png",self.iO)):
            self.saveCounter += 1

    def canvasChanged(self, canvas):
        pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("timeLapse", DockWidgetFactoryBase.DockRight, timeLapseDocker))
