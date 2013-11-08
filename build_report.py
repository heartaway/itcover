#coding:utf-8
__author__ = 'mxk'

"""
   本脚本需要完成的任务：
   1.解析conf配置内容；
   2.扫描工程路径；
   3.生成build.xml脚本；
   4.执行报告构建；
"""
import os

def parse_conf():
    import ConfigParser
    global server_host,agent_port,svn_path,svn_account,svn_password,code_package_pattern

    cf=ConfigParser.ConfigParser()
    cf.read("config")
    server_host=cf.get("targetServerInfo","target.server.host")
    agent_port=cf.get("targetServerInfo","target.server.coveragent.port")
    svn_path=cf.get("targetServerInfo","target.app.sourcecode.svn.path")
    svn_account=cf.get("targetServerInfo","target.app.sourcecode.svn.account")
    svn_password=cf.get("targetServerInfo","target.app.sourcecode.svn.password")
    code_package_pattern=cf.get("targetServerInfo","target.app.sourcecode.package.pattern")

def scane_maven_modules():
    global code_modules
    code_modules={}
    ''' code_modules的存储结构是： {模块名称:模块根路径}  '''

    #从svn下载源代码并编译
    codebase="%s/codebase" % os.getcwd()
    for root, dirs, files in os.walk(codebase, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.system("cd %s && svn co %s --username %s --password %s" % (codebase,svn_path,svn_account,svn_password))
    project_path="%s/%s" % (codebase,os.listdir(codebase)[0])
    os.system("cd %s && mvn clean install -Dmaven.test.skip" % project_path)

    #扫描maven工程的目录结构,并取得模块名和路径
    _find_modules(project_path)

def _find_modules(parent_dir):
    """
       递归查找模块
    """
    sub_files = os.listdir(parent_dir)
    try:
        if sub_files.index("pom.xml") > -1 and sub_files.index("src") > -1 :
            tmp=os.path.split(parent_dir)
            code_modules[tmp[1]]=parent_dir
    except :
        for file in sub_files:
            if os.path.isdir(file):
                _find_modules(file)

def build_report_task_script():
    try:
        import xml.etree.cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET

    #解析build.xml模板并修成新的构建脚本
    tree = ET.ElementTree(file='template/build.xml.template')
    root = tree.getroot()
    #写入代码模块信息
    structureNode = None
    reportTargetEle = tree.find('target[@name="report"]')
    for item in reportTargetEle.iter():
        if item.tag == 'structure':
            structureNode=item
    for name,path in code_modules.items():
        #新增属性
        p = ET.Element('property')
        p.set('name',name)
        p.set('location',path)
        root.append(p)
        #新增应用代码结构组
        group = ET.Element('group')
        group.set('name','%s' % name)
        #新增应用二进制码信息
        classfiles = ET.SubElement(group, 'classfiles')
        fileset = ET.SubElement(classfiles, 'fileset')
        fileset.set('dir','${%s}/target/classes' % name)
        pkgs=code_package_pattern.split(',')
        for pkg in pkgs :
            include = ET.SubElement(fileset, 'include')
            include.set('name','%s/**/*.class' % (pkg.replace('.','/')))
        #新增应用源代码信息
        sourcefiles = ET.SubElement(group, 'sourcefiles')
        fileset = ET.SubElement(sourcefiles, 'fileset')
        fileset.set('dir','${%s}/src/main/java' % name)
        #存入原结构
        structureNode.append(group)

    #另存为build.xml文件
    o = open('build.xml','w')
    tree.write(o)
    o.close()

def execute_cover_report():
    os.system("ant")


if __name__ == "__main__":
    parse_conf()
    scane_maven_modules()
    build_report_task_script()
    execute_cover_report()