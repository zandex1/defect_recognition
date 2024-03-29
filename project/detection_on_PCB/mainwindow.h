#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "createproject.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void on_mb_create_triggered();

    void on_mb_open_triggered();

    void on_mb_settings_triggered();

private:
    Ui::MainWindow *ui;
    CreateProject *create_project;
};
#endif // MAINWINDOW_H
