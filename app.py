from bson.objectid import ObjectId
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import threading


import time
import schedule



app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"


SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb://3.35.11.153', 27017, username="test", password="test")
db = client.dbsparta_plus_week4


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        # 받은 jwt를 secretkey랑 알고리즘을 기준으로 해독
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        ## print(payload)->{'id': 'aaa', 'exp': 1631618191}
        ##진자 템플릿 사용할 수 있도록 해줌
        user_info = db.users.find_one({"username": payload["id"]})
        # print(user_info)->{'_id': ObjectId('613f0818515d075a40a503cd'), 'username': 'aaa', 'password': '754068f93ca0903e1db7f0ad3ec5a616179c738f462959dd2380b6e2743680db', 'profile_name': 'aaa', 'profile_pic': '', 'profile_pic_real': 'profile_pics/profile_placeholder.png', 'profile_info': ''}
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "password": password_hash,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        "profile_info": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        print(request.form)
        # ImmutableMultiDict([('file_give', 'undefined'), ('name_give', 'aaa'), ('about_give', '나는 에이에이다!ㄴㅁ')])
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


##################################################댓글
# 댓글 업로드
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        print(request.form)
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        postId_receive = request.form["postId_give"]

        if postId_receive:  # postid 있으면(=기존 게시물 수정하면)
            new_doc = {"comment": comment_receive}
            db.posts.update_one({'_id': ObjectId(postId_receive)},{'$set':new_doc})
            print(type(ObjectId(postId_receive)))
            return jsonify({"result": "success", 'msg': '수정 성공'})
        else:
            doc = {
                "username": user_info["username"],
                "profile_name": user_info["profile_name"],
                "profile_pic_real": user_info["profile_pic_real"],
                "comment": comment_receive,
                "date": date_receive
            }
            db.posts.insert_one(doc)
            return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 댓글 가져오기
@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username_receive = request.args.get("username_give")
        # print(request.args); -> ImmutableMultiDict([('username_give', 'hi')])
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(db.posts.find({"username": username_receive}).sort("date", -1).limit(20))
        for post in posts:
            # print(type(post["_id"]))
            post["_id"] = str(post["_id"])
            # 좋아요 몇개인지
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            # 내가 좋아요 했는지
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
            # 내가쓴건지
            post['by_me'] = True if post["username"] == str(payload['id']) else False
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts, "my_username": payload["id"]})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        print(count)
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))



@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})
    comment_receive = request.form["comment_give"]

    doc = {
        "username": user_info['username'],
        "comment": comment_receive
    }

    db.posts.delete_one(doc)
    # return jsonify({'result': 'success', 'msg': f'단어 {user_info} 삭제'})
    return jsonify({'result': 'success', 'msg': '코멘트 삭제'})



@app.route('/delete_post', methods=['POST'])
def delete_post():
    db.posts.remove({})
    return jsonify({'result': 'success'})


@app.route('/get_url_from_db', methods=['GET'])
def get_url_from_db():
    videos = db.video.find()
    for video in videos:
        url = video['url']
        return jsonify({'result': 'success', 'video': url})



# url 크롤링해서 리턴해주는 함수
def get_url():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://randomvideo.pythonanywhere.com/', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    raw_source = str(soup.select('body > iframe'))
    try:
        src = raw_source.split("=")[-2][1:]
        print(src)
        return src
    except:
        get_url()


# url 새로 받아와서 디비에 저장하는 함수
def save_url_in_db():
    db.video.remove({})
    url = get_url()
    doc = {
        "url": url
    }
    db.video.insert_one(doc)
    return "saved url in db"


# 새로운 쓰레드로  7초마다 반복하는 함수
def refresh_url_in_db():
    save_url_in_db()
    threading.Timer(15, refresh_url_in_db).start()


refresh_url_in_db()



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
