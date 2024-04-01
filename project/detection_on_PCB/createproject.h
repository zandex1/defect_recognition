#ifndef CREATEPROJECT_H
#define CREATEPROJECT_H

#include <QWidget>
#include <QCloseEvent>
#include <QMessageBox>
#include <QFile>
#include <QTextStream>
#include "filebrowser.h"
namespace Ui {
class CreateProject;
}

class CreateProject : public QWidget
{
    Q_OBJECT

public:
    explicit CreateProject(QWidget *parent = nullptr);
    ~CreateProject();

public slots:
    void set_Path(QString sPath);

private slots:
    void on_b_cancel_clicked();

    void on_b_create_clicked();

    void on_b_show_explorer_clicked();

    void closeEvent(QCloseEvent *event);

private:
    Ui::CreateProject *ui;
    FileBrowser *fileBrowser;
};

#endif // CREATEPROJECT_H
