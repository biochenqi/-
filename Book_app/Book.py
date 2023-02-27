from flask import Blueprint , render_template, request, url_for, redirect
from bson.objectid import ObjectId
import pymongo
from flask_paginate import Pagination, get_page_parameter,get_page_args

#使用数据库
client=pymongo.MongoClient("127.0.0.1", 27017)
db = client.BookBorrow

book = Blueprint('book',__name__,url_prefix='/user/',template_folder='templates',static_folder='static')
dict_info = {}
dict_info['name'] = '诗文'
head_list = ['书名','作者','借阅室','编号','备注(阅读次数)','评价']
total_cols = db.collection_names()


@book.route('/test/',methods=['GET', 'POST'])
def test():
    per_page = int(request.args.get('per_page', 10))
    page = request.args.get(get_page_parameter(), type=int, default=1)
    #获取mongo数据库内容
    collection = db['历史']
    url_count = collection.count()
    pagination = Pagination(bs_version=5,page=page, total=url_count,per_page=per_page,css_framework='foundation')
    return render_template('test_book.html', collection=collection,head_name = head_list,page=page,per_page=per_page,pagination=pagination)

@book.route('/book/',methods=['GET', 'POST'])
def book_demo():
    if request.method == 'GET':
        #获取集合名称
        col = request.values.get('select')
        if col:
            collection = db[col].find()
            dict_info['name'] = col
        else:
            collection = db[dict_info['name']].find()
        info = request.values.get('delete')
        if info: 
            db[dict_info['name']].find_one_and_delete({'_id':ObjectId(info)})
        update_info = request.values.get('Update')
        if update_info:
            return redirect(url_for('book.update_page',idname=update_info))

    elif request.method == 'POST':
        #获取查询的结果
        collection = []
        for i in total_cols:
            for info in db[i].find({request.form['select']:request.form['path_upload']}):
                collection.append(info)
    return render_template('book.html',col_name=total_cols,head_name = head_list, table_info = collection, select_head=dict_info['name'])

@book.route('/update_page/<idname>',methods=['GET', 'POST'])
def update_page(idname=None):
    search_info = db[dict_info['name']].find_one({'_id':ObjectId(idname)})
    if not search_info:
        for class_col in total_cols:
            search_info = db[class_col].find_one({'_id':ObjectId(idname)})
            if search_info:
                dict_info['name'] = class_col
                break
    if request.method == 'POST':
        target_col = request.values.get('select')
        result_info = {head_list[i]:request.form[head_list[i]] for i in range(len(head_list))}
        if dict_info['name'] == target_col:
            db[dict_info['name']].find_one_and_update({'_id':ObjectId(idname)},{'$set':result_info})
        else:
            db[dict_info['name']].find_one_and_delete({'_id':ObjectId(idname)})
            db[target_col].insert_one(result_info)
            dict_info['name'] = target_col
        return redirect(url_for('book.book_demo'))

    return render_template('update.html',head_name=head_list,search_update = search_info,class_cols=total_cols,now_col=dict_info['name'])

#增加新的书籍
@book.route('/upload_info/',methods=['GET', 'POST'])
def upload_info():
    list_head = ['书名','作者','借阅室','编号','备注(阅读次数)','评价']
    dict_info, head_name, exists_book = {}, '哲学', []
    if request.method == 'POST':
        for i in list_head:
            dict_info[i] = request.form[i]
        head_name = request.form['select']
        #判断是否储存过该书籍
        check_storage = 1
        for i in total_cols:
            if db[i].find_one({'书名':dict_info['书名']}):
                check_storage = 0
                exists_book = [i,'    '.join(list(db[i].find_one({'书名':dict_info['书名']}).values())[1:])]
        #插入到数据库中
        if check_storage:
            db[head_name].insert_one(dict_info)
    return render_template('upload_info.html',col_name=db.collection_names(),select_head=head_name,check_book=exists_book)