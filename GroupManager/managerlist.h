#ifndef MANAGERLIST_H
#define MANAGERLIST_H

#include <QDialog>

namespace Ui {
class ManagerList;
}

class ManagerList : public QDialog
{
    Q_OBJECT

public:
    explicit ManagerList(QWidget *parent = nullptr);
    ~ManagerList();

private:
    Ui::ManagerList *ui;
};

#endif // MANAGERLIST_H
