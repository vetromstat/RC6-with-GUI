
from rcdes import Ui_MainWindow
from PyQt6 import QtGui
from PyQt6.QtCore import QThread,pyqtSignal,QObject
from PyQt6 import QtWidgets
import os,sys
from PyQt6.QtWidgets import QFileDialog, QMessageBox,QInputDialog,QApplication,QLineEdit
from rc import * 
filename = ""
Key = ""
S=[]
choose = ""
mode = "EBC"
iv = "qwert"
w = 32
r = 20 
Threading = False 

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()
    isRunning = True
    path = filename 
    def stop(self):
        self.isRunning = False
    def run(self):
        global Key,ok,iv,kk,choose,isFinished,Threading,S
        isFinished = False
        Threading = True
        Done = False 
        if ok and Key:
            if choose == "enc":	
                chunksize = 8192
                with open (filename,mode='rb') as file: 
                    pointer = 0
                    fileContent = file.read(chunksize)
                    message = bytesToBin(fileContent)  
                    isFirst = True 
                    while fileContent and self.isRunning:
                        if isFirst:
                            encription_bin_message = Encription(message,S,mode,iv,w,r)
                            encription_message = binToBytes(encription_bin_message)
                            pointer += len(encription_message)
                            isFirst = False
                            self.progress.emit()
                        else:
                            file.seek(pointer)
                            fileContent = file.read(chunksize)
                            if len(fileContent) <= chunksize and len(fileContent)!=0:
                                message = bytesToBin(fileContent)
                                encription_bin_message = Encription(message, S,mode,iv,w,r)
                                encription_message = binToBytes(encription_bin_message)
                                pointer += len(encription_message)
                                self.progress.emit()
                            elif len(fileContent) == 0:
                                Done = True 
                                break
                        with open("T8jif11mmfdjk0NNn.txt",mode = 'a+b') as f:
                            f.write(encription_message) 
                            newname = os.path.realpath(f.name)

                if Done:
                    os.remove(filename)
                    os.rename(newname,filename)
                else:
                    os.remove("T8jif11mmfdjk0NNn.txt")    

            elif choose == "dec":
                chunksize = 8192
                with open (filename,mode='r+b') as file: 
                    pointer = 0
                    fileContent = file.read(chunksize)
                    message = bytesToBin(fileContent)
                    isFirst = True
                    while fileContent and self.isRunning:
                        if isFirst:
                            decription_bin_message = Decription(message,S,mode,iv,w,r)
                            decription_message = binToBytes(decription_bin_message)
                            pointer += len(decription_message)
                            if os.path.splitext(filename)[1]!='.mp4':
                                decription_message = decription_message.lstrip(b'\x00')
                            isFirst = False
                            self.progress.emit()
                        else: 
                            file.seek(pointer)
                            fileContent = file.read(chunksize)
                            if len(fileContent) <= chunksize and len(fileContent)!=0:
                                message = bytesToBin(fileContent)
                                decription_bin_message = Decription(message,S,mode,iv,w,r)
                                decription_message = binToBytes(decription_bin_message)
                                pointer += len(decription_message)
                                if os.path.splitext(filename)[1]!='.mp4':
                                    decription_message = decription_message.lstrip(b'\x00')
                                self.progress.emit()
                            elif len(fileContent) == 0:
                                Done = True 
                                break
                        with open("T8jif11mmfdjk0NNn.txt",mode = 'a+b') as f:
                            f.write(decription_message) 
                            newname = os.path.realpath(f.name)

                if Done:
                    os.remove(filename)
                    os.rename(newname,filename)
                else:
                    os.remove("T8jif11mmfdjk0NNn.txt")    
        
            Key = ""
            S=[]
            iv = ""
            ok = False
            Threading = False
            self.finished.emit()
        else:
            self.finished.emit()
            return


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("free-icon-data-encryption-4291599 (1).png"))
        self.ui.centralwidget.setAcceptDrops(True)
        self.ui.radioEBC.setChecked(True)
        self.ui.radioEBC.toggled.connect(self.Mode)
        self.ui.radioCBC.toggled.connect(self.Mode)
        self.ui.radioCFB.toggled.connect(self.Mode)
        self.ui.radioOFB.toggled.connect(self.Mode)
        self.ui.pathbtn.clicked.connect(self.ChoosePath)
        self.ui.cross.clicked.connect(self.Cross)
        self.ui.encbtn.clicked.connect(self.Work)
        self.ui.decbtn.clicked.connect(self.Work)
        self.ui.blocksizeSlider.valueChanged.connect(self.BlockSize)
        self.ui.spinBox.valueChanged.connect(self.Rounds)

    def Disable(self):
        self.ui.radioEBC.setEnabled(False)
        self.ui.radioCBC.setEnabled(False)
        self.ui.radioCFB.setEnabled(False)
        self.ui.radioOFB.setEnabled(False)
        self.ui.pathbtn.setEnabled(False)
        self.ui.encbtn.setEnabled(False)
        self.ui.decbtn.setEnabled(False)
        self.ui.blocksizeSlider.setEnabled(False)
        self.ui.spinBox.setEnabled(False)
        self.setAcceptDrops(False)

    def Enable(self):
        self.ui.radioEBC.setEnabled(True)
        self.ui.radioCBC.setEnabled(True)
        self.ui.radioCFB.setEnabled(True)
        self.ui.radioOFB.setEnabled(True)
        self.ui.pathbtn.setEnabled(True)
        self.ui.encbtn.setEnabled(True)
        self.ui.decbtn.setEnabled(True)
        self.ui.blocksizeSlider.setEnabled(True)
        self.ui.spinBox.setEnabled(True)
        self.setAcceptDrops(True)

    def Work(self):
        self.Disable()
        global Key,ok,iv,kk,choose,mode,S
        self.ui.label_2.setStyleSheet("border-image:3767084.png;")
        if str(self.sender().objectName()) == "encbtn":
            choose = "enc"
        else:
            choose = "dec"

        Key,ok = QInputDialog.getText(self,'Input Dialog',
                                        'Enter Key:',echo = QLineEdit.EchoMode.Password)
        Key = bytes(Key, 'utf-8') 
        Key = bytesToBin(Key) 
        S = generateKey(Key,w,r)
        if mode != "EBC":
            iv,kk = QInputDialog.getText(self,'Input Dialog',
                                        'Enter IV:')

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.Finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.UpdateProgress)
        self.thread.start() 

    def Finished(self):
        self.Enable()
        self.ui.progressBar.setValue(0)
        self.ui.label_2.setStyleSheet("border-image: approved.png);")

    def UpdateProgress(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value()+1)

    def Cross(self): 
        global filename,Threading
        if Threading:
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.Enable()
        self.ui.label_2.setStyleSheet("border-image: none; border:dotted;")
        self.ui.pathlbl.setText("")
        filename = ""

    def Mode(self):
        global mode
        mode = ""
        radio = self.sender()
        if radio.isChecked() == True:
            mode = radio.text()

    def ChoosePath(self):
        global filename
        fname,ok = QFileDialog.getOpenFileName(
            self,
            "Open File",
            ".",
            "All Files (*)",
        )
        if ok:
            try: 
                 os.rename(fname, "T8jif11mmfdjk0NNn.txt")
                 os.rename("T8jif11mmfdjk0NNn.txt", fname)
                 filename = fname
                 self.ui.progressBar.setMaximum(int(os.stat(filename).st_size / 8192)+1)
                 self.ui.pathlbl.setText(filename)
                 self.ui.label_2.setStyleSheet("border-image:url(3767084.png);")
                 self.ui.label_2.setText("")
            except OSError:
                QMessageBox().warning(self,"Opened file","Close the file first",QMessageBox.StandardButton.Ok)

    def BlockSize(self):
        global w
        if   self.sender().value() == 1: w = 16
        elif self.sender().value() == 2: w = 32
        elif self.sender().value() == 3: w = 64

    def Rounds(self):
        global r 
        r = self.ui.spinBox.value()

    def dragEnterEvent(self, event):
        file = [u.toLocalFile() for u in event.mimeData().urls()]
        if event.mimeData().hasUrls() and os.path.isfile(file[0]):
            event.accept()
        else:
            event.ignore()
                       
    def dragMoveEvent(self, event):
            event.accept()
           
    def dropEvent(self, event):
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            global filename
            try: 
                 os.rename(files[0], "T8jif11mmfdjk0NNn.txt")
                 os.rename("T8jif11mmfdjk0NNn.txt", files[0])
                 filename = files[0]
                 self.ui.progressBar.setMaximum(int(os.stat(filename).st_size / 8192)+1)
                 self.ui.pathlbl.setText(filename)
                 self.ui.label_2.setStyleSheet("border-image:3767084.png);")
                 self.ui.label_2.setText("")
            except OSError:
                QMessageBox().warning(self,"Opened file","Close the file first",QMessageBox.StandardButton.Ok)


    def closeEvent(self, event):
        close = QMessageBox.question(self,
                                         "QUIT",
                                         "Are you sure want to quit ?",
                                         QMessageBox.StandardButton.Yes  | QMessageBox.StandardButton.No)

        if close == QMessageBox.StandardButton.Yes:
            if self.thread.isRunning():
                os.remove("T8jif11mmfdjk0NNn.txt")
                event.accept()
            else:
                event.accept()
        else:
                event.ignore()
def main():
    app = QApplication(sys.argv)
    window = MyWin()
    window.show()  
    sys.exit(app.exec())

if __name__=="__main__":
    main()
