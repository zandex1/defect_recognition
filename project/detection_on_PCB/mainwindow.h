#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QDebug>
#include <QFile>
#include <QJsonObject>
#include <QJsonDocument>
#include <QJsonArray>
#include "createproject.h"
#include "openproject.h"

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

public slots:
    void set_Project(QString sPath);

private slots:
    void on_mb_create_triggered();

    void on_mb_open_triggered();

    void on_mb_settings_triggered();

signals:
    void signal_show_create();

private:
    Ui::MainWindow *ui;
    CreateProject *create_project;
    OpenProject *open_project;
};
#endif // MAINWINDOW_H
