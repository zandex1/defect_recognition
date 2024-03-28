#include "mainwindow.h"
#include "./ui_mainwindow.h"



MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    create_project = new CreateProject();

    //Py_Initialize();
    //PyRun_SimpleString("print('Hello!'");
    //Py_Finalize();

}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_mb_create_triggered()
{
    create_project->show();

}


void MainWindow::on_mb_open_triggered()
{

}


void MainWindow::on_mb_settings_triggered()
{

}

