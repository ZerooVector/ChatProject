#include "managerlist.h"
#include "ui_managerlist.h"
#include <QListWidgetItem>

ManagerList::ManagerList(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::ManagerList)
{
    ui->setupUi(this);
    QListWidgetItem * item = new QListWidgetItem("ManagerList");
    ui->Manager->addItem(item);
}

ManagerList::~ManagerList()
{
    delete ui;
}
