#!/usr/bin/env python
#coding=utf-8

import pandas
import subprocess


def loadExcel(cnv_excel):
    """ 载入excel，以indexs为键，每一行数据为值，导入到字典中 """
    # 参数是sheet_name;dtype=object是将所有类型转换成字符串，浮点型能转换，但Int貌似转不了字符串
    df = pandas.read_excel(cnv_excel,sheet_name=0,dtype=object)
    tmpdict = {}
    # 表头
    head = df.columns.values.tolist()
    for indexs in df.index:
        row_list = df.loc[indexs].values.tolist()
        tmpdict[indexs] = row_list
    return tmpdict,head

def transcript(tmpdict,head):
    """ 
    使用TransGene.py通过基因start位点和end位点提取转录本，基因，外显子，通过nm.txt过滤掉文件里不存在的转录本，将这些
数据加到原有数据中 
    """
    flag = True
    nm_list = []
    with open("nm.txt", "r") as f:
        f_list = f.read().splitlines()
        nm_list.extend(f_list)

    for numb in tmpdict.keys():
        old_list = tmpdict[numb]
        start = str(old_list[2]) + ":" + str(old_list[3])
        end = str(old_list[2]) + ":" + str(old_list[4])

        # linux命令行找出转录本，基因，外显子
        start_cmd = "python  /home/TransGene.py -p " + start
        end_cmd = "python  /home/TransGene.py -p " + end
        # print("start_cmd is: {} \nend_cmd is: {} \n".format(start_cmd,end_cmd))

        # [1:]表示去除第1行
        start_rt = subprocess.getoutput(start_cmd).split('\n')[1:]
        end_rt = subprocess.getoutput(end_cmd).split('\n')[1:]
        # print("start_rt is: {} \nend_rt is: {} \n".format(start_rt,end_rt))

        start_dict = {}
        for i in start_rt:
            st = i.split('\t')
            try:
                gene,nm,exon,strand = st[0],st[1],st[2],st[7]
            # 当list元素不够，st[1],st[2]索引会报错
            except IndexError:
                print("{}_{} start_result is error,start_rt is {},st is {}\n".format(old_list[0],old_list[1],start_rt,st))
            else:
                # print("start:gene,nm,exon is: ",gene,nm,exon,"\n")
                if nm in nm_list:
                    st_nm = "start:" + nm
                    # 加个正负链
                    start_dict[st_nm] = st[:3] + st[7:]
        # print("start_dict is: ",start_dict,"\n")

        end_dict = {}
        for j in end_rt:
            en = j.split('\t')
            try:
                gene, nm, exon,strand = en[0], en[1], en[2],en[7]
            except IndexError:
                print("{}_{} end_result is error,end_rt is {},en is {}\n".format(old_list[0], old_list[1], end_rt,en))
            else:
                # print("end:gene, nm, exon is: ",gene, nm, exon,"\n")
                if nm in nm_list:
                    en_nm = "end:" + nm
                    end_dict[en_nm] = en[:3] + en[7:]
        # print("end_dict is: ",end_dict,"\n")

        # 合并start,end
        total_dict = {}
        start_list = list(start_dict.values())
        end_list = list(end_dict.values())
        if len(start_list)>1 or len(end_list)>1:
            # 如果超过一个的nm则显示出来
            print("{}_{} start_list or end_list element exceed 1".format(old_list[0],old_list[1]))
            continue
        elif len(start_list) == 0 and len(end_list) == 1:
            total_dict["total"] = ["NA","NA","NA","NA"] + end_list[0]
        elif len(start_list) == 1 and len(end_list) == 0:
            total_dict["total"] = start_list[0] + ["NA", "NA", "NA","NA"]
        elif len(start_list) == 1 and len(end_list) == 1:
            total_dict["total"] = start_list[0] + end_list[0]
        else:
            continue


        # 将字典值插入到原来的list中,并导出文件
        with open("annotation_1.tsv","a") as ouhand:
            if flag:
                merge_head = head[:5]
                merge_head.extend(["start_Gene","start_Transcript","start_Exon","start_strand","end_Gene","end_Transcript","end_Exon","end_strand"])
                merge_head.extend(head[5:])
                ouhand.write("{}\n".format("\t".join(merge_head)))
                flag = False

            merge_list = []
            if len(total_dict.keys())>0:
                for nm_name in total_dict.keys():
                    merge_list.extend(old_list[:5])
                    merge_list.extend(total_dict[nm_name])
                    merge_list.extend(old_list[5:])
                    ouhand.write("{}\n".format("\t".join(str(s) for s in merge_list)))     #全部转换成字符串格式


def main():
    """ 载入excel，通过TransGene.py软件将转录本，基因，外显子提取注释到数据中 """
    cnv_excel = sys.argv[1]
    tmpdict, head = loadExcel(cnv_excel)
    transcript(tmpdict, head)

if __name__ == '__main__':
    main()
