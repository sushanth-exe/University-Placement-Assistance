from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import json
import mysql.connector
import random
import atexit
import signal
import sys
#user dictionary to store the user details
app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
db = mysql.connector.connect(
    host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
    user="admin",
    password="database",
    database="LoginInfo"
)
#initialize the users database if is not already created
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS USERS (username VARCHAR(255), email VARCHAR(255), password VARCHAR(255))")

#initialize the blogs database if is not already created, add blog id as primary key and also tags
cursor.execute("CREATE TABLE IF NOT EXISTS BLOGS (blogid INT PRIMARY KEY, title VARCHAR(255), content TEXT, username VARCHAR(255), tags TEXT)")


#initialize the blogLikes database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS BLOGLIKES (blogid INT, username VARCHAR(255))")

#initialize the blogDislikes database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS BLOGDISLIKES (blogid INT, username VARCHAR(255))")

#initialize the comments database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS COMMENTS (comment_id INT, reply_id INT, name VARCHAR(255), text TEXT)")

#initialize the likes database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS LIKES (comment_id INT, username VARCHAR(255))")

#initialize the dislikes database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS DISLIKES (comment_id INT, username VARCHAR(255))")

#initialize the tags database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS TAGS (tag VARCHAR(255))")

#initialize the questions database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS QUESTIONS (ProblemStatement Text, Link Text, CompanyTags Text, TopicTags Text)")

#initialize the companytags database if is not already created and make the tag unique
cursor.execute("CREATE TABLE IF NOT EXISTS COMPANYTAGS (tag VARCHAR(255), UNIQUE(tag))")

#initialize the topictags database if is not already created
cursor.execute("CREATE TABLE IF NOT EXISTS TOPICTAGS (tag VARCHAR(255), UNIQUE(tag))")

#initialize the jobs database if is not already created using jobid and job details
cursor.execute("CREATE TABLE IF NOT EXISTS JOBS (jobid INT PRIMARY KEY, jobdetails TEXT)")



@app.route('/')
def index():
    return render_template('login.html')

#login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = False
        cursor = db.cursor()
        cursor.execute("SELECT * FROM USERS WHERE username=%s AND password=%s and email = %s", (username, password, email))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('landing'))
        else:
            error = "Invalid username or password. Please try again."
    return render_template('login.html', login_error = error)
    
#register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # # Check if username or email already exists
        cursor = db.cursor()
        cursor.execute("SELECT * FROM USERS WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        # existing_user = False
        # if username in user_dict:
        #     existing_user = True

        if existing_user:
            error = "Username or email already exists"
        else:
            # Insert new user into the database
            insert_query = "INSERT INTO USERS (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (username, email, password))
            db.commit()

            return redirect('/')
    return render_template('register.html', reg_error=error)

# @app.route('/landing', methods = ['GET', 'POST'])
# def landing():
#     return render_template('landing.html')


#blog page
@app.route('/newblog', methods = ['GET', 'POST'])
def newblog():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        return redirect('/landing')
    return render_template('newblog.html')

@app.route('/publishblog', methods = ['POST'])
def publishblog():
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    if request.method == 'POST':
        topic = request.json['topic']
        content = request.json['content']
        print(content)
        tags = request.json['tags']
        # convert tags and content to string
        tags = ', '.join(tags)
        # print(tags)
        
        
        while True:
            id = random.randint(1, 100000)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM BLOGS WHERE blogid = %s", (id,))
            existing_blog = cursor.fetchone()
            if not existing_blog:
                break
        cursor = db.cursor()
        # cursor.execute("INSERT INTO BLOGS (blogid, title, content, username, tags, ) VALUES (%s, %s, %s, %s, %s)", (id, topic, content, session['username'], tags))
        # add publish_status = 1, datetime = current time to the blog
        cursor.execute("INSERT INTO BLOGS (blogid, title, content, username, tags, publish_status, date) VALUES (%s, %s, %s, %s, %s, 1, NOW())", (id, topic, content, session['username'], tags))
        # cursor.execute("INSERT INTO BLOGS (blogid, title, content, username, tags) VALUES (%s, %s, %s, %s, %s)", (id, topic, content, session['username'], tags))

        db.commit()
        # save the tags in the tags database if not already present
        tags = tags.split(', ')
        for tag in tags:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM TAGS WHERE tag = %s", (tag,))
            existing_tag = cursor.fetchone()
            if not existing_tag:
                cursor.execute("INSERT INTO TAGS (tag) VALUES (%s)", (tag,))
                db.commit()
        return 'success'
@app.route('/saveblog', methods = ['POST'])
def saveblog():
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    if request.method == 'POST':
        topic = request.json['topic']
        content = request.json['content']
        tags = request.json['tags']
        # convert tags and content to string
        tags = ', '.join(tags)
        # print(tags)
        while True:
            id = random.randint(1, 100000)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM BLOGS WHERE blogid = %s", (id,))
            existing_blog = cursor.fetchone()
            if not existing_blog:
                break
        cursor = db.cursor()
        # cursor.execute("INSERT INTO BLOGS (blogid, title, content, username, tags, ) VALUES (%s, %s, %s, %s, %s)", (id, topic, content, session['username'], tags))
        # add publish_status = 0, datetime = current time to the blog
        cursor.execute("INSERT INTO BLOGS (blogid, title, content, username, tags, publish_status, date) VALUES (%s, %s, %s, %s, %s, 0, NOW())", (id, topic, content, session['username'], tags))
        # cursor.execute("INSERT INTO BLOGS (blogid, title, content, username, tags) VALUES (%s, %s, %s, %s, %s)", (id, topic, content, session['username'], tags))

        db.commit()
        # save the tags in the tags database if not already present
        tags = tags.split(', ')
        for tag in tags:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM TAGS WHERE tag = %s", (tag,))
            existing_tag = cursor.fetchone()
            if not existing_tag:
                cursor.execute("INSERT INTO TAGS (tag) VALUES (%s)", (tag,))
                db.commit()
        return 'success'
@app.route('/savedblogs', methods = ['GET', 'POST'])
def savedblogs():
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    #only send the id, and topic of the blogs of the user
    cursor.execute("SELECT blogid, title FROM BLOGS WHERE username = %s and publish_status = 0 order by date desc", (session['username'],))
    # cursor.execute("SELECT * FROM BLOGS")
    userblogs = cursor.fetchall()
    # print(userblogs)
    #convert userblogs to a dictionary
    userblogs = [{'id': blog[0], 'topic': blog[1]} for blog in userblogs]
    return render_template('savedblogs.html', userblogs = userblogs)
@app.route('/editblog/<id>', methods = ['GET', 'POST'])
def editblog(id):
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(

        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    print(id)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM BLOGS WHERE blogid = %s", (id,))
    blog = cursor.fetchone()
    print(blog)
    content = blog[2]
    print(content)
    topic = blog[1]
    print(topic)
    tags = blog[4].split(', ')
    return render_template('editblog.html', content = content, topic = topic, tags = tags, blogId = id)
@app.route('/saveblog/<id>', methods = ['POST'])
def saveblogid(id):
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(

        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    # if request.method == 'POST':
    topic = request.json['topic']
    content = request.json['content']
    tags = request.json['tags']
    # convert tags and content to string
    tags = ', '.join(tags)
    # print(tags)
    cursor = db.cursor()
    cursor.execute("UPDATE BLOGS SET title = %s, content = %s, tags = %s, date = NOW() WHERE blogid = %s", (topic, content, tags, id))
    db.commit()
    return 'success'
@app.route('/publishblog/<id>', methods = ['POST'])
def publishblogid(id):
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(

        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    #save the blog with the id, topic, content, tags, publish_status = 1
    topic = request.json['topic']
    content = request.json['content']
    tags = request.json['tags']
    # convert tags and content to string
    tags = ', '.join(tags)
    # print(tags)
    cursor = db.cursor()
    cursor.execute("UPDATE BLOGS SET title = %s, content = %s, tags = %s, publish_status = 1 WHERE blogid = %s", (topic, content, tags, id))
    db.commit()
    return 'success'
@app.route('/allblogs', methods = ['GET', 'POST'])
def allblogs():
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    #only send the id, and topic of the blogs of the user
    cursor.execute("SELECT blogid, title, tags FROM BLOGS where publish_status = 1 order by date desc")
    # cursor.execute("SELECT * FROM BLOGS")
    blogs = cursor.fetchall()
    # print(userblogs)
    #convert userblogs to a dictionary
    # blogs = [{'id': blog[0], 'topic': blog[1]} for blog in blogs]
    blogs = [{'id': blog[0], 'topic': blog[1], 'tags': blog[2]} for blog in blogs]
    return render_template('allblogs.html', allblogs = blogs)
@app.route('/userblogs', methods = ['GET', 'POST'])
def userblogs():
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    #only send the id, and topic of the blogs of the user
    cursor.execute("SELECT blogid, title FROM BLOGS WHERE username = %s and publish_status = 1 order by date desc", (session['username'],))
    # cursor.execute("SELECT * FROM BLOGS")
    userblogs = cursor.fetchall()
    # print(userblogs)
    #convert userblogs to a dictionary
    userblogs = [{'id': blog[0], 'topic': blog[1]} for blog in userblogs]


    return render_template('userblogs.html', userblogs = userblogs)

@app.route('/displayblogs/<id>', methods = ['GET', 'POST'])
def displayblogs(id):
    if 'username' not in session:
        return redirect('/')
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM BLOGS WHERE blogid = %s", (id,))
    blog = cursor.fetchone()
    content = blog[2]
    topic = blog[1]
    tags = blog[4].split(', ')
    #fetch the likes and dislikes
    cursor.execute("SELECT * FROM BLOGLIKES WHERE blogid = %s", (id,))
    likes = cursor.fetchall()
    cursor.execute("SELECT * FROM BLOGDISLIKES WHERE blogid = %s", (id,))
    dislikes = cursor.fetchall()
    cursor.execute("SELECT * FROM BLOGLIKES WHERE blogid = %s AND username = %s", (id, session['username']))
    existing_like = cursor.fetchone()
    cursor.execute("SELECT * FROM BLOGDISLIKES WHERE blogid = %s AND username = %s", (id, session['username']))
    existing_dislike = cursor.fetchone()
    totalBlogLikesDislikes = len(likes) - len(dislikes)
    if existing_like:
        existing_like = "True"
    else:
        existing_like = "False"
    if existing_dislike:
        existing_dislike = "True"
    else:
        existing_dislike = "False"
    return render_template('displayblog.html', 
                           content = content, 
                           topic = topic, 
                           tags = tags, 
                           author = blog[3], 
                           blogId = id, 
                           totalBlogLikesDislikes = totalBlogLikesDislikes, 
                           existing_like = existing_like, 
                           existing_dislike = existing_dislike,
                           userName = session['username'])
# @app.route('/editblog/<id>', methods = ['GET', 'POST'])
# def editblog(id):
#     #fetch the blog details with the id
#     if request.method == 'POST':
#         return redirect('/userblogs')
#     db = mysql.connector.connect(

@app.route('/likeBlog', methods = ['POST'])
def likeBlog():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        blogid = request.json['blogId']
        print(blogid)
        db = mysql.connector.connect(
            host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
            user="admin",
            password="database",
            database="LoginInfo"
        )
        cursor = db.cursor()
        #first check if the user has already liked the blog
        cursor.execute("SELECT * FROM BLOGLIKES WHERE blogid = %s AND username = %s", (blogid, session['username']))
        existing_like = cursor.fetchone()
        # remove from dislikes if already disliked
        db = mysql.connector.connect(
            host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
            user="admin",
            password="database",
            database="LoginInfo"
        )
        cursor = db.cursor()
        cursor.execute("DELETE FROM BLOGDISLIKES WHERE blogid = %s AND username = %s", (blogid, session['username']))
        db.commit()
        if not existing_like:
            db = mysql.connector.connect(
                host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
                user="admin",
                password="database",
                database="LoginInfo"
            )
            cursor = db.cursor()
            cursor.execute("INSERT INTO BLOGLIKES (blogid, username) VALUES (%s, %s)", (blogid, session['username']))
            db.commit()
        else:
            db = mysql.connector.connect(
                host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
                user="admin",
                password="database",
                database="LoginInfo"
            )
            cursor = db.cursor()
            cursor.execute("DELETE FROM BLOGLIKES WHERE blogid = %s AND username = %s", (blogid, session['username']))
            db.commit()
        return 'success'

@app.route('/dislikeBlog', methods = ['POST'])
def dislikeBlog():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        db = mysql.connector.connect(
            host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
            user="admin",
            password="database",
            database="LoginInfo"
        )
        blogid = request.json['blogId']
        cursor = db.cursor()
        #first check if the user has already disliked the blog
        cursor.execute("SELECT * FROM BLOGDISLIKES WHERE blogid = %s AND username = %s", (blogid, session['username']))
        existing_dislike = cursor.fetchone()
        # remove from likes if already liked
        db = mysql.connector.connect(
            host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
            user="admin",
            password="database",
            database="LoginInfo"
        )
        cursor = db.cursor()
        cursor.execute("DELETE FROM BLOGLIKES WHERE blogid = %s AND username = %s", (blogid, session['username']))
        db.commit()
        if not existing_dislike:
            db = mysql.connector.connect(
                host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
                user="admin",
                password="database",
                database="LoginInfo"
            )
            cursor = db.cursor()
            cursor.execute("INSERT INTO BLOGDISLIKES (blogid, username) VALUES (%s, %s)", (blogid, session['username']))
            db.commit()
        else:
            db = mysql.connector.connect(
                host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
                user="admin",
                password="database",
                database="LoginInfo"
            )
            cursor = db.cursor()
            cursor.execute("DELETE FROM BLOGDISLIKES WHERE blogid = %s AND username = %s", (blogid, session['username']))
            db.commit()
        return 'success'

@app.route('/landing', methods = ['GET', 'POST'])
def landing():
    # print(session['username'])
    if 'username' not in session:
        return redirect('/')
    # print('a')
    # get the questions from the database
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM QUESTIONS")
    questions = cursor.fetchall()
    #merge company and topic tags
    questions = [{'problem': question[0], 'link': question[1], 'tags': question[2] + ',' + question[3]} for question in questions]

    # questions = [{'problem': question[0], 'link': question[1], 'company': question[2], 'topics': question[3]} for question in questions]
    return render_template('landing.html', questions = questions)
@app.route('/getallcompanytags', methods=['GET'])
def getallcompanytags():
    if 'username' not in session:
        return redirect('/')
    #define examples tags
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM COMPANYTAGS")
    tags = cursor.fetchall()
    tags = [tag[0] for tag in tags]
    return jsonify({'tags': tags})
@app.route('/getalltopictags', methods=['GET'])
def getalltopictags():
    if 'username' not in session:
        return redirect('/')
    #define examples tags
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM TOPICTAGS")
    tags = cursor.fetchall()
    tags = [tag[0] for tag in tags]
    return jsonify({'tags': tags})
@app.route('/getalltags', methods=['GET'])
def getalltags():
    if 'username' not in session:
        return redirect('/')
    #define examples tags
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM TAGS")
    tags = cursor.fetchall()
    tags = [tag[0] for tag in tags]
    tags = tags
    return jsonify({'tags': tags})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')
#comment-section backend:
#generate a random comment id
@app.route("/comments/get_comment_id/", methods=["GET", "POST"])
def get_comment_id():
    if 'username' not in session:
        return redirect('/')
    print('a')
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    while True:
        new_id = random.randint(100001, 1000000)
        print(new_id)
        # check if the id is already used in reply_id of the comments in the database
        cursor.execute("SELECT * FROM COMMENTS WHERE reply_id=%s", (new_id,))
        if not cursor.fetchone():
            return jsonify({"comment_id": new_id})
#save the comment
@app.route("/comments/<comment_id>/<reply_id>", methods=["GET", "POST"])
def comments(comment_id, reply_id):
    if 'username' not in session:
        return redirect('/')
    if request.method == "POST":
        db = mysql.connector.connect(
            host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
            user="admin",
            password="database",
            database="LoginInfo"
        )
        name = request.json['name']
        text = request.json['text']
        print(name)
        print(type(name))
        cursor = db.cursor()
        cursor.execute("INSERT INTO COMMENTS (comment_id, reply_id, name, text) VALUES (%s, %s, %s, %s)", (comment_id, reply_id, name, text))
        db.commit()
        return jsonify({"message": "Reply added successfully."})
    elif request.method == "GET":
        db = mysql.connector.connect(
            host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
            user="admin",
            password="database",
            database="LoginInfo"
        )
        cursor = db.cursor()
        cursor.execute("SELECT * FROM COMMENTS WHERE reply_id=%s", (reply_id,))
        comments = cursor.fetchall()
        if not comments:
            return jsonify({})
        comments = [{'name': comment[2], 'text': comment[3]} for comment in comments]
        return jsonify(comments)
@app.route("/comments/replies/<comment_id>", methods=["GET"])
def replies(comment_id):
    if 'username' not in session:
        return redirect('/')
    if request.method == "GET":
        db = mysql.connector.connect(
            host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
            user="admin",
            password="database",
            database="LoginInfo"
        )
        cursor = db.cursor()
        cursor.execute("SELECT reply_id, name, text FROM COMMENTS WHERE comment_id=%s", (comment_id,))
        comments = cursor.fetchall()
        if not comments:
            return jsonify({})
        replies = {}
        for comment in comments:
            print(comment[0])
            replies[comment[0]] = {'name': comment[1], 'text': comment[2]}
            # replies[comment[0]] = {'name': comment[1], 'text': comment[2]}
        print(comments)
        return jsonify(replies)

# jobs page code starts from here:
# all_jobs = {}

@app.route('/add-job', methods=['GET'])
def job_post():
    if 'username' not in session:
        return redirect('/')
    return render_template('job-post.html')
@app.route('/save-job', methods=['POST'])
def save_job():
    if 'username' not in session:
        return redirect('/')
    # read the json data
    # global all_jobs
    job_data = request.json
    # #create a job id
    job_id = random.randint(1, 1000)
    # all_jobs[job_id] = job_data
    # print(all_jobs[job_id])
    # save the job in the database
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("INSERT INTO JOBS (jobid, jobdetails) VALUES (%s, %s)", (job_id, json.dumps(job_data)))
    db.commit()

    # job_data = jsonify(job_data)
    # for i in range(1, n):
        # print(job_data[i]['requirements'])
    # print(job_data[1]['requirements'])
    return jsonify({'status': 'success', 'message': 'Job has been saved successfully!'})

@app.route('/job-details/<id>', methods=['GET'])
def job_details(id):
    if 'username' not in session:
        return redirect('/')
    # global all_jobs
    # print(all_jobs)
    # job = all_jobs[int(id)]
    #get the job details from the database
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM JOBS WHERE jobid = %s", (id,))
    job_data = cursor.fetchone()
    job_data = json.loads(job_data[1])
    job = job_data

    # print(job)
    # print(job_data)
    return render_template('job-display.html', job=job)

@app.route('/all-jobs', methods=['GET'])
def alljobs():
    if 'username' not in session:
        return redirect('/')
    # get all jobs with their details like jobid, company name only
    # global all_jobs
    # print(all_jobs)
    # jobs = {}
    # for job in all_jobs:
    #     id = job
    #     company = all_jobs[job][0]['company']
    #     #add id, company to jobs with key as jobid
    #     jobs[id] = company
    # print(jobs)
    #get the job id and company name from the database
    db = mysql.connector.connect(
        host="database-1.cp608kyc6sh5.ap-south-2.rds.amazonaws.com",
        user="admin",
        password="database",
        database="LoginInfo"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM JOBS")
    jobs = cursor.fetchall()
    new_jobs = {}
    for job in jobs:
        # print(type(json.loads(job[1])[0]))
        print(json.loads(job[1])[0]['company'])
        id = job[0]
        company = json.loads(job[1])[0]['company']
        new_jobs[id] = company
    print(new_jobs)
    # print(1 + jobs)

    return render_template('all-jobs.html', jobs=new_jobs)

        
if __name__ == '__main__':
    app.run(debug=True)
