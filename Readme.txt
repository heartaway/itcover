itcover是一款用于统计集成测试对应用代码覆盖率并生成报告的框架。
操作分为客户端和服务端两部分，服务端只是对应用注入一条jvm参数；客户端即itcover这个包。
客户端基础环境依赖有：
1. jdk、maven和apache-ant框架。
2. python2.6及以上。

部署到实际测试环境的步骤有：

1. 上传jacocoagent.jar到服务器上，在应用容器启动文件中增加一条jvm参数并重新启动： 
-javaagent:<jacocoagent.jar所在目录>/jacocoagent.jar=output=tcpserver,address=<服务器IP>,port=6745
其中，这里的port是jacocoagent的采集端口，address和port需要与客户端config配置保持一致。

2. 修改客户端config文件，配置属性有：
* target.server.host：应用服务器IP，需要与服务器上的参数保持一致；
* target.server.coveragent.port：应用服务器上注入的覆盖率采集端口，需要与服务器上的参数保持一致；
* target.app.sourcecode.svn.path：应用代码的svn地址，如果有多模块，只要配置根路径就可以了，框架会自动扫描模块信息;
* target.app.sourcecode.svn.account：svn帐号；
* target.app.sourcecode.svn.password：svn密码；
* target.app.sourcecode.package.pattern：需要覆盖的java包，只要给出到根路径一级就够了，如com.aliyun.qa.portal.service,com.aliyun.qa.portal.dao。

3. 生成报表，执行python build_report.py。

4. 查看报表，进入到itcover/report目录下，用浏览器打开index.html。

