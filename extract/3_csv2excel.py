#!/usr/bin/env python
#conding=utf-8

import sys
import pandas

inf = sys.argv[1]
df = pandas.read_csv(inf,delimiter='\t')
df.to_excel('cnv.xlsx',index=False)
