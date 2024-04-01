#ifndef FILEBROWSER_H
#define FILEBROWSER_H

#include <QWidget>
#include <QTreeView>
#include <QFileSystemModel>
#include <QDebug>

namespace Ui {
class FileBrowser;
}

class FileBrowser : public QWidget
{
    Q_OBJECT

public:
    explicit FileBrowser(QWidget *parent = nullptr);
    ~FileBrowser();

private slots:
    void on_b_back_clicked();

    void on_b_accept_clicked();

    void on_treeView_clicked(const QModelIndex &index);

    void on_treeView_doubleClicked(const QModelIndex &index);

signals:
    void SignalPath(QString);

private:
    Ui::FileBrowser *ui;
    QFileSystemModel *dirmodel;
};

#endif // FILEBROWSER_H
