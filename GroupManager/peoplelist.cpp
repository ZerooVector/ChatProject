#include "peoplelist.h"
#include "ui_peoplelist.h"
#include <QListWidgetItem>

PeopleList::PeopleList(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::PeopleList)
{
    ui->setupUi(this);
    QListWidgetItem * item = new QListWidgetItem("PeopleList");
    ui->People->addItem(item);
}

PeopleList::~PeopleList()
{
    delete ui;
}
