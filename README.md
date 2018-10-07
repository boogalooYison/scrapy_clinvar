# scrapy_clinvar
    此项目的功能是爬取NCBI网站中clinvar所有网页的数据，并对关键信息进行提取和注释，爬虫框架使用scrapy。

## 文件介绍：
### clinvar:爬虫文件
    通过动态设置user agent，使用IP地址池，禁用cookies，设置延迟下载防止爬虫被ban的情况
### extract:提取和注释数据文件
    使用json,lxml的xpath模块将html文件关键信息提取到json文件中，并将json文件导成tsv格式
    使用pandas,re,subprocess等模块对关键信息进行整合和注释，并保存为excel格式
