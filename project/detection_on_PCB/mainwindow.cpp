#include "mainwindow.h"
#include "./ui_mainwindow.h"

QString projectDir;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    this->setWindowTitle("Основное окно");
    ui->setupUi(this);

    create_project = new CreateProject();
    open_project = new OpenProject();

    connect(create_project, &CreateProject::SignalPath, this, &MainWindow::set_Project);
    connect(open_project, &OpenProject::SignalPath, this, &MainWindow::set_Project);

}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::set_Project(QString sPath)
{
    projectDir = sPath;
    qDebug() << projectDir;

    QString val;
    QFile file;
    QDir dir;
    dir.cd(projectDir);
    file.setFileName(dir.absoluteFilePath("data.json"));
    file.open(QIODevice::ReadOnly | QIODevice::Text);
    val = file.readAll();
    file.close();

    // Чтение JSON файла
    QJsonDocument doc = QJsonDocument::fromJson(val.toUtf8());
    QJsonObject json = doc.object();
    QString projectName = json["project_name"].toString();
    QString refPath = json["reference_folder"].toString();
    QString insPath = json["inspected_folder"].toString();
    QJsonArray insPathToFolderJ = json["inspected_path_to_folder"].toArray();
    QList <QVariant> insPathToFolder = insPathToFolderJ.toVariantList();

    qDebug() << projectName << Qt::endl << refPath <<Qt::endl << insPath << Qt::endl << insPathToFolder;
    this->setWindowTitle(projectName);
}

void MainWindow::on_mb_create_triggered()
{
    create_project->show();

}


void MainWindow::on_mb_open_triggered()
{
    open_project->show();
}


void MainWindow::on_mb_settings_triggered()
{

}

