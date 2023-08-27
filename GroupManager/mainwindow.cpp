#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "grouptools.h"
#include <QApplication>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}


void MainWindow::on_ManageGroup_clicked()
{
    grouptools = new GroupTools(this);
    grouptools->show();

}
