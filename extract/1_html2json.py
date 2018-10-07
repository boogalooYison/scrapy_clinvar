#!/usr/bin/env python
# coding=utf-8

import re
import json
from lxml import etree
import sys

def pmid(Cl_Description,Cl_Citation_PubMed):
    """ 这个是为了提取数据里Cl_Description列中的pubmed号 """
    # PMID = re.compile('\(PMID:( [0-9]+,)*( [0-9]+)\)')
    PMID = re.compile('\(PMID:.*\)')
    Cl_Description = str(Cl_Description)
    try:
        desc_id = PMID.search(Cl_Description).group()
    except (AttributeError, IndexError):  # AttributeError是group的是空，IndexError是没有group，即不能strip
        merge_list = Cl_Citation_PubMed
    else:
        desc_id_list = desc_id.lstrip("(PMID: ").rstrip(")").split(", ")
        merge_id = desc_id_list + Cl_Citation_PubMed
        merge_list = list(set(merge_id))
    return merge_list

def get_content_list(i):
    """ 用xpath提取html里的cnv数据的关键信息，并导入到list里 """
    # i有换行符，要去掉
    f = i.strip()
    html = etree.parse(f)
    result = html.xpath('/ClinVarResult-Set/VariationReport')
    content_list = []
    for table in result:
        item = {}
        item["VariationID"] = table.xpath('./@VariationID')
        item["Chr"] = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@Chr')
        start = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@start')
        outerStart = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@outerStart')
        display_start = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@display_start')
        if len(start)>0:
            item["start"] = start
        elif len(outerStart)>0:
            item["start"] = outerStart
        elif len(display_start)>0:
            item["start"] = display_start
        stop = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@stop')
        outerStop = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@outerStop')
        display_stop = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@display_stop')
        if len(stop)>0:
            item["stop"] = stop
        elif len(outerStop)>0:
            item["stop"] = outerStop
        elif len(display_stop)>0:
            item["stop"] = display_stop
        item["variantLength"] = table.xpath('./Allele/SequenceLocation[@Assembly="GRCh37"]/@variantLength')
        item["VariantType"] = table.xpath('./Allele/VariantType/text()')
        item["VariationName"] = table.xpath('./@VariationName')
        item["Ob_ReviewStatus"] = table.xpath('./ObservationList/Observation/ReviewStatus/text()')
        item["Ob_Description"] = table.xpath('./ObservationList/Observation/ClinicalSignificance/Description/text()')
        item["Ob_DateLastEvaluated"] = table.xpath('./ObservationList/Observation/ClinicalSignificance/@DateLastEvaluated')
        # 判断judge大小
        try:
            judge = int(item["variantLength"][0])
        except IndexError:
            continue
        # print(judge)
        # 范围大于50，小于1M
        if judge >= 50 and judge <= 1048576:
            # 分出每个Submitter的信息，再遍历提取,不嵌套在dict里面
            clinical = table.xpath('./ClinicalAssertionList/GermlineList/Germline')
            # print(clinical)
            # 加上一个计数器，作为Submitter的编号
            count = 1
            for clin in clinical:
                # if stop > 5 and stop < 20:
                # print("stop is: ",stop)
                # count也转换成list
                item["count"] = list(str(count))
                # print("count is: ",count)
                item["Cl_SubmitterName"] = clin.xpath('./@SubmitterName')
                item["Cl_DateLastEvaluated"] = clin.xpath('./ClinicalSignificance/@DateLastEvaluated')
                item["Cl_Description"] = clin.xpath('./ClinicalSignificance/Description/text()')
                item["Cl_ReviewStatus"] = clin.xpath('./ReviewStatus/text()')
                item["Cl_Method"] = clin.xpath('./ClinicalSignificance/Method/text()')
                item["Cl_Phenotype_Name"] = clin.xpath('./PhenotypeList/Phenotype/@Name')
                item["Cl_AlleleOrigin_Origin"] = clin.xpath('./AlleleOriginList/AlleleOrigin/@Origin')
                item["Cl_Accession"] = clin.xpath('./@Accession')
                item["Cl_Comment"] = clin.xpath('./ClinicalSignificance/Comment/text()')
                item["Cl_Citation_PubMed"] = clin.xpath('./ClinicalSignificance/Citation/ID/text()')
                # 1.正则提取所有文献编号,merge去重
                Cl_Description = item["Cl_Description"]
                Cl_Citation_PubMed = item["Cl_Citation_PubMed"]
                merge_list = pmid(Cl_Description,Cl_Citation_PubMed)
                item["Cl_Merge_PubMed"] = merge_list

                content_list.append(item.copy())
                count += 1
    # html文件里内容重复了一次，所以取一半的数据就行
    content_list_half = content_list[:int(len(content_list) / 2)]
    return content_list_half

def save_content_list(content_list):
    with open("cnv.json", "a", encoding="utf-8") as f:
        for content in content_list:
            f.write(json.dumps(content, ensure_ascii=False))
            f.write("\n")


def main():
    """
    ls_file是包含所有html文件名称路径的文件
    """
    ls_file = sys.argv[1]
    with open(ls_file,"r") as ls_f:
        for i in ls_f:
            # print("i is: ",i)
            # 1.提取数据
            content_list = get_content_list(i)
            # 2.保存数据
            save_content_list(content_list)


if __name__ == '__main__':
    main()
