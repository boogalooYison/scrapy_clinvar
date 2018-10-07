#!/usr/bin/env python
#coding=utf-8

import json
import sys
import codecs

def trans(cnv_json):
    """ 将json文件格式导成tsv格式，加上表头 """
    json_data = codecs.open(cnv_json,"r","utf-8")
    with open("cnv.tsv", "w") as ouhand:
        flag = True
        for line in json_data:
            # 以list的顺序，依此导入字典的值
            list = ["VariationID","count","Chr","start","stop","variantLength","VariantType","VariationName","Ob_ReviewStatus","Ob_Description","Ob_DateLastEvaluated","Cl_SubmitterName","Cl_DateLastEvaluated","Cl_Description","Cl_ReviewStatus","Cl_Method","Cl_Phenotype_Name","Cl_AlleleOrigin_Origin","Cl_Accession","Cl_Comment","Cl_Citation_PubMed","Cl_Merge_PubMed"]
            tmpdict = json.loads(line[0:-1])

            if flag:
                ouhand.write("{}\n".format("\t".join(list)))
                flag = False

            # join(fields)里面元素不能是list,不然会报错；if就是放在前面的，详情见sort_dict.py
            # fields = [str(tmpdict[x]) if x in tmpdict.keys() else "NA" for x in list]
            fields = []
            for x in list:
                if x in tmpdict.keys():
                    # 去除列表，用', '分割，逗号加空格，如果只用逗号，用excel打开pmid号会出现乱码
                    if tmpdict[x] is not None:
                        fields.append(', '.join(tmpdict[x]))
                    else:
                        fields.append("NA")
                else:
                    fields.append("NA")
            ouhand.write("{}\n".format("\t".join(fields)))


if __name__ == '__main__':
    cnv_json = sys.argv[1]
    trans(cnv_json)
