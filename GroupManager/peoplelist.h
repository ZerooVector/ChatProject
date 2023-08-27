#ifndef PEOPLELIST_H
#define PEOPLELIST_H

#include <QDialog>

namespace Ui {
class PeopleList;
}

class PeopleList : public QDialog
{
    Q_OBJECT

public:
    explicit PeopleList(QWidget *parent = nullptr);
    ~PeopleList();

private:
    Ui::PeopleList *ui;
};

#endif // PEOPLELIST_H
