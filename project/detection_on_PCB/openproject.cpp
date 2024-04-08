#include "openproject.h"
#include "ui_openproject.h"

OpenProject::OpenProject(QWidget *parent)
    : QWidget(parent)
    , ui(new Ui::OpenProject)
{
    ui->setupUi(this);

    dirmodel = new QFileSystemModel(this);
    dirmodel->setFilter(QDir::NoDotAndDotDot | QDir::AllDirs);
    dirmodel->setRootPath("/");

    ui->treeView->setModel(dirmodel);
    ui->treeView->setColumnHidden(1,true);
    ui->treeView->setColumnHidden(2,true);
    ui->treeView->setColumnHidden(3,true);
    ui->treeView->setColumnWidth(0,100);

    filemodel = new QFileSystemModel(this);
    filemodel->setFilter(QDir::NoDotAndDotDot | QDir::Files);

    ui->listView->setModel(filemodel);
}

OpenProject::~OpenProject()
{
    delete ui;
}

void OpenProject::on_b_accept_clicked()
{
    if(ui->lineEdit->displayText().isEmpty()){
        QMessageBox msgBox;
        msgBox.setText("Неуказано путь к файлу");
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.exec();
    }else{
        QString sPath = ui->lineEdit->text();
        sPath.remove("data.json");
        emit SignalPath(sPath);
        this->close();
    }
}

void OpenProject::on_b_cancel_clicked()
{
    this->close();
}


void OpenProject::on_treeView_clicked(const QModelIndex &index)
{
    QString sPath = dirmodel->fileInfo(index).absoluteFilePath();
    ui->listView->setRootIndex(filemodel->setRootPath(sPath));
}


void OpenProject::on_listView_doubleClicked(const QModelIndex &index)
{
    if (filemodel->fileInfo(index).absoluteFilePath().contains("data.json")){
        ui->lineEdit->setText(filemodel->fileInfo(index).absoluteFilePath());
    }else{
        QMessageBox msgBox;
        msgBox.setText("Выбран не файл проекта");
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.exec();
    }
}

