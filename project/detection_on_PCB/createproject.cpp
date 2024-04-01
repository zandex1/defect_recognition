#include "createproject.h"
#include "ui_createproject.h"

CreateProject::CreateProject(QWidget *parent)
    : QWidget(parent)
    , ui(new Ui::CreateProject)
{
    ui->setupUi(this);

    fileBrowser = new FileBrowser();

    connect(fileBrowser, &FileBrowser::SignalPath, this, &CreateProject::set_Path);
}

CreateProject::~CreateProject()
{
    delete ui;
}

void CreateProject::set_Path(QString sPath)
{
    ui->tf_project_location->clear();
    ui->tf_project_location->insert(sPath);
}

void CreateProject::on_b_cancel_clicked()
{

    this->close();
}


void CreateProject::on_b_create_clicked()
{
    // Доработать проверку месторасположения на валидность пути
    if(ui->tf_project_name->displayText().isEmpty() | ui->tf_project_location->displayText().isEmpty()){
        QMessageBox msgBox;
        msgBox.setText("Неуказано имя или месторасположение");
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.exec();
    }else{
        QDir dir;
        dir.cd(ui->tf_project_location->text());
        if(!dir.exists("ms")){
            dir.mkdir(ui->tf_project_name->text());
            qDebug()<<"Save complete";
        }

        dir.cd(ui->tf_project_location->text() + "/" + ui->tf_project_name->text());
        qDebug()<<dir;

        QString filename = ui->tf_project_name->text() + ".json";
        QFile file;
        file.setFileName(dir.absoluteFilePath(filename));
        qDebug()<<dir.absoluteFilePath(filename);
        if (file.open(QIODevice::ReadWrite)) {
            QTextStream stream(&file);
            stream << "something" << Qt::endl;
        }
    }

}


void CreateProject::on_b_show_explorer_clicked()
{
    fileBrowser->show();
}

void CreateProject::closeEvent(QCloseEvent *event)
{
    if (fileBrowser->isEnabled()){
        fileBrowser->close();
    }

}
