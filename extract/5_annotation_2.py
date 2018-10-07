#!/usr/bin/env python
#coding=utf-8

import pandas
import re

def geneMerge(a,b):
    """ 合并基因 """
    if a == b:
        new_gene = a
    elif a == "0":
        new_gene = "NON;" + b
    elif b == "0":
        new_gene = a + ":NON"
    else:
        new_gene = a + ";" + b
    return new_gene

def geneTag(a,b):
    """ 基因标签 """
    if a == b:
        return "Y"
    else:
        return "N"

def nmMerge(a,b):
    """ 合并转录本 """
    # 转录本只保留小数点之前的
    NM_RM = re.compile('\w*')
    a_new = NM_RM.search(a).group()
    b_new = NM_RM.search(b).group()
    if a_new == b_new:
        nm_new = a_new
    elif a_new == "0":
        nm_new = "NON;" + b_new
    elif b_new == "0":
        nm_new = a_new + ";NON"
    else:
        nm_new = a + ";" + b
    return nm_new

def toExon(a,b):
    """ 转内含子为外显子 """
    if a == ".":
        new_str = "EX1"
    elif a.startswith("IVS"):
        NUM = re.compile('[0-9]+')
        num = NUM.search(a).group().strip()
        if b == "+":
            new_num = str(int(num) + 1)
            new_str = "EX" + new_num
        elif b == "-":
            new_str = "EX" + num
        else:
            new_str = "unknown strand"
    else:
        new_str = a
    return new_str

def exonMerge(a,b):
    """ 合并外显子 """
    if a == "0":
        new_exon = "NON-" + b
    elif b == "0":
        new_exon = a + "-NON"
    elif a == b:
        new_exon = a
    else:
        NUM = re.compile('[0-9]+')
        num_a = NUM.search(a).group().strip()
        num_b = NUM.search(b).group().strip()
        if int(num_a) < int(num_b):
            new_exon = a + "-" + b
        else:
            new_exon = b + "-" + a
    return new_exon

def exonTag(a,b):
    """ 外显子标签 """
    if a == b:
        return "N"
    else:
        return "Y"

def strandMerge(a,b):
    """ 合并正负链 """
    if a == b:
        return a
    else:
        return "different strand"

def Status(a):
    """ 改status """
    if a == "copy number gain" or a == "Duplication":
        return "gain"
    elif a == "copy number loss" or a == "Deletion":
        return "loss"
    else:
        return "mapping_rate status"

def main():
    """ 将start和end的基因，转录本，外显子列信息进行合并 """

    # 打开excel
    anno_1 = sys.argv[1]
    df = pandas.read_excel(anno_1, sheet_name=0, dtype=object)

    # 将操作的8行，nan填充为0
    # 此处不能用inplace,不然会报错SettingWithCopyWarning
    # df.loc[:, 'start_Gene':'end_strand'].fillna(0, inplace=True)
    df.loc[:, 'start_Gene':'end_strand'] = df.loc[:, 'start_Gene':'end_strand'].fillna(0)

    # 删掉不要的行
    # ~表示反选
    # df = df[~df['VariantType'].str.contains("Complex")]
    # df = df[~df['VariantType'].str.contains("Insertion")]
    Pattern = re.compile("Complex|Insertion|Indel")
    df = df[~df['VariantType'].str.contains(Pattern)]

    # 合并基因
    # 因为会出现浮点型的错误，需要把数据转换成str
    # 其中x带表当前行，可以通过下标进行索引
    df['gene_merge'] = df.apply(lambda x: geneMerge(str(x['start_Gene']), str(x['end_Gene'])), axis=1)
    # 基因标签
    df['gene_tag'] = df.apply(lambda x: geneTag(str(x['start_Gene']), str(x['end_Gene'])), axis=1)

    # 合并转录本
    df['nm_merge'] = df.apply(lambda x: nmMerge(str(x['start_Transcript']), str(x['end_Transcript'])), axis=1)

    # 合并外显子
    # 转内含子为外显子
    df['start_to_exon'] = df.apply(lambda x: toExon(str(x['start_Exon']), str(x['start_strand'])), axis=1)
    df['end_to_exon'] = df.apply(lambda x: toExon(str(x['end_Exon']), str(x['end_strand'])), axis=1)
    # 合并外显子
    df['exon_merge'] = df.apply(lambda x: exonMerge(str(x['start_to_exon']), str(x['end_to_exon'])), axis=1)
    # 外显子标签
    df['exon_tag'] = df.apply(lambda x: exonTag(str(x['start_to_exon']), str(x['end_to_exon'])), axis=1)
    # 合并正负链
    df['strand_merge'] = df.apply(lambda x: strandMerge(str(x['start_strand']), str(x['end_strand'])), axis=1)

    # 改status
    df['status'] = df.apply(lambda x: Status(str(x['VariantType'])), axis=1)

    # 插入列
    # 用拼接更快，这里用insert
    df.insert(0, 'gene_tag', df.pop('gene_tag'))
    df.insert(1, 'exon_tag', df.pop('exon_tag'))
    df.insert(2, 'strand_merge', df.pop('strand_merge'))
    df.insert(8, 'gene_merge', df.pop('gene_merge'))
    df.insert(9, 'nm_merge', df.pop('nm_merge'))
    df.insert(10, 'exon_merge', df.pop('exon_merge'))
    df.insert(11, 'status', df.pop('status'))

    # 导入新excel
    df.to_excel("annotation_2.xlsx", sheet_name="Sheet1", index=False)

if __name__ == '__main__':
    main()
