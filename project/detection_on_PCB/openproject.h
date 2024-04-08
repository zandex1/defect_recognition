#ifndef OPENPROJECT_H
#define OPENPROJECT_H

#include <QWidget>
#include <QFileSystemModel>
#include <QDir>
#include <QMessageBox>
namespace Ui {
class OpenProject;
}

class OpenProject : public QWidget
{
    Q_OBJECT

public:
    explicit OpenProject(QWidget *parent = nullptr);
    ~OpenProject();

private slots:
    void on_b_accept_clicked();

    void on_b_cancel_clicked();

    void on_treeView_clicked(const QModelIndex &index);

    void on_listView_doubleClicked(const QModelIndex &index);

signals:
    void SignalPath(QString);

private:
    Ui::OpenProject *ui;
    QFileSystemModel *dirmodel;
    QFileSystemModel *filemodel;
};

#endif // OPENPROJECT_H
