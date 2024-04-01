#include "filebrowser.h"
#include "ui_filebrowser.h"

QString selPath;

FileBrowser::FileBrowser(QWidget *parent)
    : QWidget(parent)
    , ui(new Ui::FileBrowser)
{
    ui->setupUi(this);

    QString sPath = "/home/";

    dirmodel = new QFileSystemModel(this);
    dirmodel->setFilter(QDir::NoDotAndDotDot | QDir::AllDirs);
    dirmodel->setRootPath(sPath);
    ui->treeView->setModel(dirmodel);
    ui->treeView->setColumnHidden(1,true);
    ui->treeView->setColumnHidden(2,true);
    ui->treeView->setColumnHidden(3,true);
    ui->treeView->setColumnWidth(0,100);
}

FileBrowser::~FileBrowser()
{
    delete ui;
}

void FileBrowser::on_b_back_clicked()
{
    this->close();
}


void FileBrowser::on_b_accept_clicked()
{
    emit SignalPath(selPath);
    this->close();
}


void FileBrowser::on_treeView_clicked(const QModelIndex &index)
{
    QString sPath = dirmodel->fileInfo(index).absoluteFilePath();
    selPath=sPath;
}



void FileBrowser::on_treeView_doubleClicked(const QModelIndex &index)
{
    emit SignalPath(selPath);
    this->close();
}

