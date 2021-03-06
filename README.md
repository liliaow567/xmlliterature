# 环境
1. `python3`
2. package: `pandas`, `re`, `xml`
3. 建议安装 `anaconda` 并配置环境变量

# 流程


1. 准备文本文件 `<file>`（从 webofscience 核心数据库，plaintext 下载）

2. 进入命令行当前路径

3. 执行如下命令初始化`lite.xml`, 以及`xlsx` 文件

   ` python initial_xml.py <file>`

4. 修改 `xlsx` 文件（根据标题，关键字手动设置某篇文章可见以及其他）

5. 修改规则 

   * 排序使用大于0小于10的数
   * 不可见设为小于等于0即可
   * 图片名和图片文件名对应，多个名字应用英文分号 ;隔开,分号后应留有空格

6. 执行如下命令使修改生效，并生成摘要文稿

   `python change_xml.py <file>`

7. 可重复执行5，6步

8. 上传，需要上传相应的图片和`lite.xml`文件

   上传网址：[http://119.23.107.86/others/fileupload.html](http://119.23.107.86/others/fileupload.html)
   

9. 结果查看

   * 方式一：通过地址查看

      `http://119.23.107.86/others/<yourname>/journalread.php`

   * 方式二：利用页面重定向
   将`zhangsan.html` 重命名为 `<yourname>.html`
   
   * 方式三：利用方式一或方式二得到结果页面后，将页面离线保存下来即可。

# 示例
1. 从webofscience获取文本文件

![fig1](image/fig1.png)
![fig2](image/fig2.png)

2. 命令行执行


![fig3](image/fig3.png)
![fig4](image/fig4.png)

3. 结果示例

	示例：[http://119.23.107.86/others/zhangsan/journalread.php](http://119.23.107.86/others/zhangsan/journalread.php)


# 说明

相关测试皆在win10系统，Google浏览器下测试完成，屏幕分辨率为1920x1080.


