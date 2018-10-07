# -*- coding: utf-8 -*-
import scrapy

class ClinvarSpider(scrapy.Spider):
    name = 'clinvar'
    # allowed_domains = ['preview.ncbi.nlm.nih.gov']
    # url = "https://preview.ncbi.nlm.nih.gov/clinvar/variation/"
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.cgi?db=clinvar&id=48074,542074&rettype=variation"
    start_urls = ["https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.cgi?db=clinvar&id=48074,542074&rettype=variation"]


    def parse(self, response):
        # 以url最后一行第一个和最后一个id为文件名称
        filename = response.url.split("/")[-1].split(",")[0].strip("efetch.cgi?db=clinvar&id=") + "_" + response.url.split("/")[-1].split(",")[-1].strip("&rettype=variation")
        with open(filename, 'wb') as f:
            f.write(response.body)

        with open("url_id","r") as url_file:
            url_f = url_file.read().splitlines()
            # 将id文件每250个为单位切割
            for i in range(0,len(url_f),250):
                url_250 = url_f[i:i+250]
                print(url_250)
                offset = ",".join(url_250)
                print(offset)
                
                # yield scrapy.Request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.cgi?db=clinvar&id=" + offset + "&rettype=variation",callback = self.parse)
                yield scrapy.FormRequest("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.cgi?db=clinvar&id=" + offset + "&rettype=variation",formdata = {'db':'clinvar','id':offset, 'email':'2366786983@qq.com'},callback = self.parse)
                print("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.cgi?db=clinvar&id=" + offset + "&rettype=variation")
