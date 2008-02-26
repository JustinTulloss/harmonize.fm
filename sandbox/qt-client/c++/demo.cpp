#include <QtGui/QApplication>
#include <QtGui/QMainWindow>

#include "uploader.ui.h"

int
main(int argc, char **argv)
{
    QApplication app(argc, argv);
    
    Ui_MainWindow *genwin = new Ui_MainWindow();
    QMainWindow *mainwin = new QMainWindow();

    genwin->setupUi(mainwin);
    mainwin->show();

    return app.exec();
}
