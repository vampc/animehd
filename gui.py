from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, pyqtSlot
from MainWindow import Ui_MainWindow
import sys
import json


from main_dialog import AddDialog
from worker import WorkerKilledException, WorkerSignals, Worker
from models import TableModel, ProgressDelegate


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.delegate = ProgressDelegate(self.table_view)
        self.table_view.setSelectionBehavior(
            QtWidgets.QTableView.SelectRows)
        self.table_view.setItemDelegateForColumn(2, self.delegate)
        self.data = [
            [1, 'Jujustu Kaisen episode 5', 30, 'Downloading'],
            [2, 2, 3, 'Paused'],
            [3, 2, 3, 'Paused'],
            [4, 2, 3, 'Paused']

        ]
        self.model = TableModel(self.data)
        self.table_view.setModel(self.model)

        # self.add_push_button.pressed.connect(self.on_add_button_clicked)
        self.add_push_button.pressed.connect(self.add)
        self.remove_push_button.pressed.connect(self.remove)
        self.start_push_button.pressed.connect(self.start)
        self.pause_push_button.pressed.connect(self.pause)
        self.worker_progress = {}
        self.threadpool = QThreadPool()

    def on_add_button_clicked(self):
        dlg = AddDialog(self)
        dlg.signals.data.connect(self.get_data_from_dialog)
        dlg.exec()

    def get_data_from_dialog(self, data):
        print(data)

    def update_progress(self, job_id, progress):
        row = job_id
        index = self.model.createIndex(row, 0)
        start_index = self.model.createIndex(row, 2)
        end_index = self.model.createIndex(row, 2)
        old_value = self.model.videos[index.row()]
        self.model.videos[index.row()] = [old_value[0],
                                          old_value[1], progress, 'Downloading']
        self.model.dataChanged.emit(index, end_index, [Qt.DisplayRole])

    def remove(self):
        print('Remove Clicked')
        return
        indexes = self.todo_list_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            del self.model.videos[index.row()]
            self.model.layoutChanged.emit()
            self.todo_list_view.clearSelection()
            self.save()

    def load(self):
        try:
            with open("data.json", 'r') as f:
                self.model.videos = json.load(f)
        except Exception:
            pass

    def save(self):
        with open("data.json", 'w') as f:
            data = json.dump(self.model.videos, f)

    def start(self):
        print('Start Clicked')
        return
        indexes = self.todo_list_view.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            status, text = self.model.videos[row]
            self.model.todos[row] = (True, text)
            self.model.dataChanged.emit(index, index)
            self.todo_list_view.clearSelection()
            self.save()

    def add(self):
        self.model.videos.append([5, 'Naruto', 0, 'Paused'])
        self.model.layoutChanged.emit()

        worker = Worker(len(self.model.videos)-1)
        worker.signals.progress.connect(self.update_progress)
        self.threadpool.start(worker)

    def pause(self):
        print('pause clicked')
        return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
