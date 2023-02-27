import gzip,sys
import pandas as pd
from glob import glob

file_all = glob('*/meth_result/*.f.dedup.bedGraph.gz')
#bed read
feature = []
with open(sys.argv[1],'r') as f:
    for line in f:
        line = line.strip().split("\t")
        feature.append('_'.join(line))

def file_read(file,feature,colume_name,dict_feature_count):
    total_info = []
    with gzip.open(file,'rb') as f:
        for line in f:
            line = str(line,encoding='utf-8')
            if line.startswith('track'):continue
            line = line.strip().split('\t')
            head = '_'.join(line[:-1])
            total_info.append([head,float(line[-1])/100])
    df = pd.DataFrame(total_info)
    df.set_index([0],inplace=True)
    df = df.rename(columns={1:colume_name})
    feature_in =[]
    for i in feature:
        if i in df.index:
            feature_in.append(i)
        else:
            if i not in dict_feature_count:dict_feature_count[i] = 0
            dict_feature_count[i] += 1
    return df.loc[feature_in,:]

dict_feature_count = {}
colume_name = file_all[0].split('/')[0]
meth_info = file_read(file_all[0],feature,colume_name,dict_feature_count)
for file in file_all[1:]:
    colume_name = file.split('/')[0]
    df_file = file_read(file,feature,colume_name,dict_feature_count)
    meth_info = pd.concat([meth_info,df_file],join='inner',axis=1)

print(dict_feature_count)
meth_info.to_csv('result.csv',sep='\t')