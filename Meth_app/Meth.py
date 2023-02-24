from flask import Blueprint , render_template, request, url_for, redirect
from glob import glob
import subprocess

meth = Blueprint('meth',__name__,url_prefix='/meth/',template_folder='templates',static_folder='static')
#甲基化数据下载目录
# down_meth_path = '/project/NextSeqProject/mingma_210916/'
down_meth_path = '/project/usr/chenqi/test/test_read/Meth_app/test'

dict_para={'Double':
{'AdapterEnd':'AGATCGGAAGAGCACACGTC',
'AdapterTop':'ACACGACGCTCTTCCGATCT',
'TrimmomaticMinAdapterLength':'5',
'TrimmomaticMinLength':'40',
'TrimmomaticAverageQuality':'20'
},
'single':{
'AdapterEnd':'AGATCGGAAGAGCACACGTC',
'AdapterTop':'ACACGACGCTCTTCCGATCT',
'TrimmomaticAdapterMismatch':'2',
'TrimmomaticPalindromeThreshold':'30',
'TrimmomaticSimpleThreshold':'10',
'TrimmomaticWindowSize':'5',
'TrimmomaticRequiredQuality':'15',
'TrimmomaticStartQuality':'15',
'TrimmomaticEndQuality':'15',
}}

@meth.route('/',methods=['GET', 'POST'])
def meth_init():
    sin_dou, check_down = 'Double', 0
    total_project = [i.strip(down_meth_path) for i in glob(down_meth_path + '*')]
    global check_meth_run,subp
    if request.method == 'POST':
        # sin_dou = request.values.get('select')
        #从下载数据开始处理
        down_meth = request.values.get('down_meth')
        down_path = request.values.get('select_path')
        if down_meth:
            check_meth_run = 1
            command='/project/baowenjuan/APP/ossutil64 cp -r --update %s %s'%(down_meth,down_meth_path)
            subp = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
            return redirect(url_for('meth.meth_run'))

        #直接从已经下载好的数据开始处理
        elif down_path:
            check_meth_run = 2
            return redirect(url_for('meth.meth_run',file_path=down_path))
        TrimmomaticMinLength = request.values.get('TrimmomaticMinLength')
        

    elif request.method == 'GET':
        if request.values.get('select_down') == 'no':
            check_down = 0
        elif request.values.get('select_down') == 'yes':
            check_down = 1
    return render_template('meth.html',parameter=dict_para[sin_dou],check = check_down,projects = total_project)

@meth.route('/meth_run/',methods=['GET', 'POST'])
def meth_run():
    if check_meth_run == 1:
        #监控是否下载完
        if subp.poll() == 0:
            #已经完成下载
            check_down_finish = 1
        elif subp.poll() and subp.poll() != 0 :
            #说明下载出故障了
            check_down_finish = 2
            #故障原因
        else:
            #说明还在下载中
            check_down_finish = 0
        error_info = subp.stderr.read()
    elif check_meth_run == 2:
        pass
    return render_template('meth_run.html',check_down_sit=check_down_finish,error_message=error_info)

#数据下载
# def down_meth_func(command):
#     subp = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
#     return subp