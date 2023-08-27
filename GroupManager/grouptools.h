#ifndef GROUPTOOLS_H
#define GROUPTOOLS_H

#include <QDialog>
#include "peoplelist.h"
#include "managerlist.h"

namespace Ui {
class GroupTools;
}

class GroupTools : public QDialog
{
    Q_OBJECT

public:
    explicit GroupTools(QWidget *parent = nullptr);
    ~GroupTools();

private slots:
    void on_ManagerList_clicked();

    void on_PeopleGroup_clicked();

private:
    Ui::GroupTools *ui;
    PeopleList *peoplelist;
    ManagerList *managerlist;
};

#endif // GROUPTOOLS_H
