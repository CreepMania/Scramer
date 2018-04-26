if __name__ == "__main__":
    import Scraper
    from PyQt5 import QtWidgets
    import sys

    Qapp = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Scraper.Scraper(Qapp, MainWindow)
    ui.show()

    while MainWindow.isVisible():
        sys.exit(Qapp.exec_())
