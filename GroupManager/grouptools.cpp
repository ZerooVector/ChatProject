#include "grouptools.h"
#include "ui_grouptools.h"
#include "peoplelist.h"
#include "managerlist.h"

GroupTools::GroupTools(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::GroupTools)
{
    ui->setupUi(this);
}

GroupTools::~GroupTools()
{
    delete ui;
}

void GroupTools::on_ManagerList_clicked()
{
    managerlist = new ManagerList(this);
    managerlist->show();
}

void GroupTools::on_PeopleGroup_clicked()
{
    peoplelist = new PeopleList(this);
    peoplelist->show();
}
