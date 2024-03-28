#ifndef CREATEPROJECT_H
#define CREATEPROJECT_H

#include <QWidget>

namespace Ui {
class CreateProject;
}

class CreateProject : public QWidget
{
    Q_OBJECT

public:
    explicit CreateProject(QWidget *parent = nullptr);
    ~CreateProject();

private slots:
    void on_b_cancel_clicked();

    void on_b_create_clicked();

    void on_b_show_explorer_clicked();

private:
    Ui::CreateProject *ui;
};

#endif // CREATEPROJECT_H
