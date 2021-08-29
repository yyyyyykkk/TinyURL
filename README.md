# TinyURL

## 部署过程
1. 创建一个serverless服务，分别创建两个函数create-link和get，把CreateLink文件夹上传到create-link，Get文件夹上传到get
2. 把access key 和 secret key改成自己的
3. 部署并调用

## 截图
Create Link
![avatar](https://i.niupic.com/images/2021/08/29/9tAU.png)

Get Content
![avatar](https://i.niupic.com/images/2021/08/29/9tAV.png)

## 高可用架构
![avatar](https://i.niupic.com/images/2021/08/29/9tAW.png)

注：可以使用Offline Key Generator来产生不重复的key作为hash，以此来避免碰撞



