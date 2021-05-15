import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QAction,
    qApp,
    QApplication,
    QGridLayout,
    QLabel,
    QDial,
    QComboBox,
    QPushButton,
    QCheckBox,
    QLineEdit
)

# from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QPainter, QPen, QIntValidator
from PyQt5.QtCore import Qt
import cfg
import synthesizer


class Home(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)

        grid = QGridLayout()
        grid.addWidget(Mixer(), 0, 0)
        grid.addWidget(Preview(), 1, 0)
        wid.setLayout(grid)
        exitAct = QAction(QIcon("exit.png"), "&Exit", self)
        exitAct.setShortcut("Ctrl+Q")
        exitAct.setStatusTip("Exit application")
        exitAct.triggered.connect(qApp.quit)

        self.statusbar = self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAct)

        self.resize(600, 500)
        self.setWindowTitle("Title")
        # self. setWindowIcon(QIcon('x.png'))
        self.show()

    def get_patch(self):
        cfg.operators = []
        dials = ["amplitude", "attack", "decay", "sustain", "release"]
        for id in range(cfg.operator_count):
            operator = {}
            operator["enabled"] = self.findChild(QCheckBox, f"enabled{id}").isChecked()
            operator["waveform"] = str(
                self.findChild(QComboBox, f"waveform{id}").currentText()
            )
            try:
                operator["transpose"] = int(self.findChild(QLineEdit, f"transpose{id}").text())
            except ValueError:
                operator["transpose"] = 0
            for dial in dials:
                operator[dial] = self.findChild(QDial, f"{dial}{id}").value()
                if dial in ["amplitude", "sustain"]:
                    operator[dial] /= 100
            cfg.operators.append(operator)

        return cfg.operators


class Mixer(QWidget):
    def __init__(self, operators=6):
        super().__init__()
        self.initUI()

    def initUI(self):

        grid = QGridLayout()
        max_columns = 3
        column = 0
        row = 0
        for id in range(cfg.operator_count):
            operator = Operator(id)
            grid.addWidget(operator, row, column)
            if column == max_columns - 1:
                column = 0
                row += 1
            else:
                column += 1

        self.setLayout(grid)


class Preview(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        image_preview = QLabel("Image")
        audio_preview = QLabel("Audio")
        grid.addWidget(Oscilloscope(), 0, 0)
        grid.addWidget(Audio(), 1, 0)
        self.setLayout(grid)


class Operator(QWidget):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.initUI()

    def initUI(self):
        grid = QGridLayout()

        enabled = QCheckBox('Enabled')
        enabled.setObjectName(f"enabled{self.id}")
        enabled.toggle()
        enabled.stateChanged.connect(self.checkbox_update)
        grid.addWidget(enabled, 0, 0)

        amplitude = QDial()
        amplitude.setObjectName(f"amplitude{self.id}")
        amplitude.setMinimum(0)
        amplitude.setMaximum(100)
        amplitude.setValue(100)
        amplitude.setNotchesVisible(True)
        amplitude.setMaximumSize(80, 80)
        amplitude.valueChanged.connect(self.dial_update)
        # amplitude.setEnabled(False)
        grid.addWidget(amplitude, 1, 0)
        #grid.addWidget(amplitude, 0, 0, 2, 1)

        waveform = QComboBox(self)
        waveform.setObjectName(f"waveform{self.id}")
        waveform.addItem("Sine")
        waveform.addItem("Square")
        waveform.addItem("Sawtooth")
        waveform.addItem("Triangle")
        waveform.addItem("Random")
        waveform.currentTextChanged.connect(self.combobox_update)
        
        transpose = QLineEdit(self)
        transpose.setObjectName(f"transpose{self.id}")
        transpose.setValidator(QIntValidator())
        transpose.setMaxLength(3)
        transpose.setText("0")
        transpose.textChanged.connect(self.lineedit_update)
        
        grid.addWidget(waveform, 0, 1)
        grid.addWidget(transpose, 0, 2)
        grid.addWidget(Envelope(self.id), 1, 1)
        self.setLayout(grid)

    def return_operator(self):
        operator = {}
        
    def combobox_update(self, value):
    	update_statusbar(str(value))
    	draw_oscilloscope()
    	
    def checkbox_update(self):
    	draw_oscilloscope()
    	
    def lineedit_update(self):
    	draw_oscilloscope()
    	
    def dial_update(self, value):
    	update_statusbar(str(value))
    	draw_oscilloscope()


class Envelope(QWidget):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.initUI()

    def initUI(self):
        grid = QGridLayout()

        envelope = {}
        label = {}
        stages = ["attack", "decay", "sustain", "release"]

        for stage in stages:
            envelope[stage] = QDial()
            envelope[stage].setObjectName(f"{stage}{self.id}")
            envelope[stage].setMinimum(0)
            envelope[stage].setMaximum(100)
            envelope[stage].setValue(0)
            envelope[stage].setNotchesVisible(True)
            envelope[stage].setMaximumSize(40, 40)
            envelope[stage].valueChanged.connect(self.dial_update)

            label[stage] = QLabel(stage[0].upper())
            label[stage].setAlignment(Qt.AlignCenter)

        envelope["sustain"].setValue(100)

        for column, stage in enumerate(stages):
            grid.addWidget(envelope[stage], 0, column)
            grid.addWidget(label[stage], 1, column)

        self.setLayout(grid)

    def dial_update(self, value):
        update_statusbar(str(value))
        draw_oscilloscope()

class Oscilloscope(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 900
        self.height = 100
        self.initUI()

    def initUI(self):
        self.resize(self.width, self.height)

    def paintEvent(self, event, waveform=[]):
        qp = QPainter()
        qp.begin(self)
        self.draw_waveform(qp, waveform)
        qp.end()

    def draw_waveform(self, qp, waveform=[]):
        if cfg.stream == []:
            pen = QPen(Qt.black, 2, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(
                0, int(self.height / 2), int(self.width), int(self.height / 2)
            )
        else:
            samples = cfg.oscilloscope_samples
            for s in range(samples):
                if s == 0:
                    continue
                pen = QPen(Qt.black, 2, Qt.SolidLine)
                qp.setPen(pen)
                x1 = int(
                    synthesizer.interpolate(0, self.width, 0, s - 1, samples)
                )
                y1 = int(
                    synthesizer.interpolate(
                        self.height, 0, -32767, cfg.stream[s - 1], 32768
                    )
                )
                x2 = int(synthesizer.interpolate(0, self.width, 0, s, samples))
                y2 = int(
                    synthesizer.interpolate(
                        self.height, 0, -32767, cfg.stream[s], 32768
                    )
                )
                qp.drawLine(x1, y1, x2, y2)


class Audio(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()

        preview_button = QPushButton()
        preview_button.setText("Preview")
        preview_button.clicked.connect(self.listen)
        grid.addWidget(preview_button, 0, 0)

        record_button = QPushButton()
        record_button.setText("Record")
        record_button.clicked.connect(self.record)
        grid.addWidget(record_button, 1, 0)

        self.setLayout(grid)

    def listen(self, pressed):
        update()

    def record(self, pressed):
        update()
        record()


w = None
active = False

def main():
    global w, active
    app = QApplication(sys.argv)
    w = Home()
    active = True
    draw_oscilloscope()
    sys.exit(app.exec_())


def update_statusbar(message):
    if active:
        w.statusbar.showMessage(message, 5000)


def draw_oscilloscope():
    if active:
        w.get_patch()
        synthesizer.process(cfg.oscilloscope_samples)
        w.update()


def update():
    w.get_patch()
    synthesizer.process()
    w.update()


def record():
    w.get_patch()
    synthesizer.record()


if __name__ == "__main__":
    main()
