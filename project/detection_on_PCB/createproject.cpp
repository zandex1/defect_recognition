#include "createproject.h"
#include "ui_createproject.h"

CreateProject::CreateProject(QWidget *parent)
    : QWidget(parent)
    , ui(new Ui::CreateProject)
{
    ui->setupUi(this);
}

CreateProject::~CreateProject()
{
    delete ui;
}


void CreateProject::on_b_cancel_clicked()
{

}


void CreateProject::on_b_create_clicked()
{

}


void CreateProject::on_b_show_explorer_clicked()
{

}

