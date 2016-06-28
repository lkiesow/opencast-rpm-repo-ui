#!/bin/env python
# -*- coding: utf-8 -*-

# Set default encoding to UTF-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import config
from db import get_session, User
from hashlib import sha512

#import sqlite3
import re
import random
import string
import json
import smtplib
from datetime import date
from flask import Flask, render_template, request, Response, redirect, url_for, session
app = Flask(__name__)
app.secret_key = config.sessionkey


dbsession = get_session()


@app.route('/', methods=['POST', 'GET'])
def home():
    user, passwd = request.form.get('username'), request.form.get('password')
    if user:
        u = dbsession.query(User).filter(User.username==user)
        if not u.count():
            return redirect(url_for('error', e='loginerror'))
        session['login'] = (u[0].username, u[0].admin, u[0].access)


    # Don't accept self set users
    user = None
    try:
        user, admin, repoaccess = session.get('login')
    except:
        pass
    if user:
        return render_template('login.html', config=config, username=user,
                admin=admin)

    # No login? Show start page:
    return render_template('index.html', config=config)


@app.route('/matterhorn.repo', methods=['GET', 'POST'])
@app.route('/matterhorn-testing.repo', methods=['GET', 'POST'])
@app.route('/opencast.repo', methods=['GET', 'POST'])
@app.route('/opencast-testing.repo', methods=['GET', 'POST'])
def repofile():
    if not request.authorization:
        return '', 401
    user, passwd = request.authorization.username, request.authorization.password
    if not user:
        return '', 401
    try:
        with sqlite3.connect('users.db') as con:
            cur = con.cursor()
            cur.execute('''select username from user
                    where username=? and password=? and repoaccess''',
                    (user, passwd))
            if not cur.fetchone():
                return '', 400
    except:
        return '', 401

    # Get specs
    tpl     = request.path.lstrip('/')
    os      = request.form.get('os', 'el')
    version = request.form.get('version', '6')

    print tpl, user, passwd, os
    return render_template(tpl, user=user, passwd=passwd, os=os,
            version=version)


@app.route('/auth', methods=['GET'])
def auth():
    try:
        user, passwd = request.authorization.username, request.authorization.password
        if session.get('login') == (user, passwd):
            return '' # 200 OK
        with sqlite3.connect('users.db') as con:
            cur = con.cursor()
            cur.execute('''select username from user
                    where username=? and password=? and repoaccess''',
                    (user, passwd))
            data = cur.fetchone()
            if data:
                session['login'] = (user, passwd)
                return '' # 200 OK
    except:
        pass
    return Response('', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})



@app.route('/msg/<e>')
def error(e):
    try:
        msg = getattr(config, e)
        return render_template('message.html', config=config, message=msg)
    except:
        return '', 400


@app.route('/forgot', methods=['GET','POST'])
def forgot():
    email = request.form.get('email')
    if not email:
        return render_template('forgot.html', config=config)

    data = None
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('''select username, password from user
                where email=? and repoaccess''', (email,))
        data = cur.fetchall()

    if not data:
        return redirect(url_for('error', e='forgotmailerror'))

    # Send mail
    header  = 'From: %s\n' % config.mailsender
    header += 'To: %s\n' % email
    header += 'Subject: %s\n\n' % config.forgotmailtopic
    message = header + config.forgotmailtext
    for username, password in data:
        message += '\nusername: %s'   % username
        message += '\npassword: %s\n' % password

    server = smtplib.SMTP('smtp.serv.uos.de')
    server.sendmail(
            config.mailsender,
            email,
            message)
    server.quit()
    return redirect(url_for('error', e='forgotsuccess'))


@app.route('/terms')
def terms():
    return render_template('terms.html', config=config)


@app.route('/impressum')
def impressum():
    return render_template('impressum.html', config=config)


@app.route('/success')
def success():
    return render_template('success.html', config=config)


@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/<who>', methods=['GET', 'POST'])
def admin(who='new'):
    username, admin, repoaccess = [None]*3
    try:
        username, admin, repoaccess = session.get('login')
    except:
        pass
    if not username or not admin:
        return redirect(url_for('home'))

    # Handle save option
    if request.form:
        with sqlite3.connect('users.db') as con:
            cur = con.cursor()
            user = unicode(request.form.get('user'))
            action = request.form.get('action')
            cur.execute(u'''select repoaccess, email, password, firstname, lastname
                    from user where username=?''', (user,))
            data = cur.fetchone()
            if data:
                if action in (u'admin', u'user') and not data[0]:
                    registrationmail(user, data[1], data[2], data[3], data[4])
                if action == u'user':
                    cur.execute(u'update user set repoaccess=1, admin=0 where username=?', (user,))
                elif action == u'admin':
                    cur.execute(u'update user set repoaccess=1, admin=1 where username=?', (user,))
                elif action == u'delete':
                    cur.execute(u'delete from user where username=?', (user,))
                    reason = request.form.get(u'reason')
                    deletemail(user, data[1], data[3], data[4], reason)
                con.commit()

    user = []
    # Get user
    user = dbsession.query(User).order_by(User.username.asc())

    if who == 'new':
        user = user.filter(User.access==False)
        return render_template('adminnew.html', config=config, user=user,
                newusercount=user.count())
    return render_template('adminall.html', config=config, user=user,
            newusercount=len([ u for u in user if not u.access]),
            usercount=user.count())


@app.route('/access/<who>/<ref>', methods=['GET'])
def access(who, ref):
    username, admin, repoaccess = [None]*3
    try:
        username, admin, repoaccess = session.get('login')
    except:
        pass
    if not username or not admin:
        return redirect(url_for('home'))

    dbsession.query(User).filter(User.username==who).update({'access':True})
    dbsession.commit()

    return redirect(url_for('admin', who=ref))


@app.route('/delete/<who>/<ref>', methods=['GET'])
def delete(who, ref):
    username, admin, repoaccess = [None]*3
    try:
        username, admin, repoaccess = session.get('login')
    except:
        pass
    if not username or not admin:
        return redirect(url_for('home'))

    dbsession.query(User).filter(User.username==who).delete()
    dbsession.commit()

    return redirect(url_for('admin', who=ref))


@app.route('/csv', methods=['GET'])
def csv():
    username, admin, repoaccess = [None]*3
    try:
        username, admin, repoaccess = session.get('login')
    except:
        pass
    if not username or not admin:
        return redirect(url_for('home'))

    user = []
    # Get user
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('select * from user')
        user = cur.fetchall()

    user.sort(key=lambda u: u[0].lower())

    result = 'username, firstname, lastname, password, email, country, city, ' \
            + 'company, department, created, usematterhorn, installations, ' \
            + 'adoptiontime, admin, repoaccess, deleteaccess, comment\n'

    for u in user:
        result += '"' + '", "'.join([str(x) for x in u]) + '"\n'
    return Response(result, content_type='application/octet-stream')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/storeuser', methods=['POST'])
def storeuser():
    if request.form.get('terms') != 'agree':
        return redirect(url_for('error', e='termsofuseuerror'))

    if request.form.get('url'):
        return redirect(url_for('error', e='boterror'))

    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', request.form.get('email')):
        return redirect(url_for('error', e='emailerror'))

    if not re.match(r'^[a-z]+$', request.form.get('user')):
        return redirect(url_for('error', e='userexistserror'))

    for field in ['firstname', 'lastname', 'country', 'city', 'organization']:
        if not request.form.get(field):
            return redirect(url_for('error', e='requirederror'))

    dbsession.add(User(
        username=request.form.get('user'),
        firstname=request.form.get('firstname'),
        lastname=request.form.get('lastname'),
        email=request.form.get('email'),
        country=request.form.get('country'),
        city=request.form.get('city'),
        organization=request.form.get('organization'),
        department=request.form.get('department'),
        created=date.today(),
        usage=request.form.get('usage'),
        learned=request.form.get('learn-about'),
        admin=False,
        access=False))
    dbsession.commit()
    #except Exception as e:
    #    print(e)
    #    return redirect(url_for('error', e='dberror'))

    # Send registration mail to admin
    header  = 'From: %s\n' % request.form.get('email')
    header += 'To: %s\n' % config.adminmailadress
    header += 'Subject: %s\n\n' % (
            config.adminmailtopic % {'username' : request.form.get('user')})
    message = header + ( config.adminmailtext % {
        'username'  : request.form.get('user'),
        'firstname' : request.form.get('firstname'),
        'lastname'  : request.form.get('lastname') })

    server = smtplib.SMTP('smtp.serv.uos.de')
    for to in config.adminmailadress:
        server.sendmail(request.form.get('email'), to, message)
    server.quit()
    return redirect(url_for('success'))


def passwdgen():
    chars = string.letters + string.digits
    passwd = ''
    for i in xrange(10):
        passwd += chars[random.randrange(0, len(chars))]
    return passwd


def registrationmail(username, email, password, firstname, lastname):
    header  = 'From: %s\n' % config.mailsender
    header += 'To: %s\n' % email
    header += 'Subject: %s\n\n' % config.mailtopic
    message = header + config.mailtext % {
            'firstname' : firstname,
            'lastname'  : lastname,
            'username'  : username,
            'password'  : password}

    server = smtplib.SMTP('smtp.serv.uos.de')
    server.sendmail(config.mailsender, email, message)
    server.quit()


def deletemail(username, email, firstname, lastname, reason):

    text = reason

    header  = 'From: %s\n' % config.mailsender
    header += 'To: %s\n' % email
    header += 'Subject: OpencastRepo Accound has been Deleted\n\n'
    message = header + text

    server = smtplib.SMTP('smtp.serv.uos.de')
    server.sendmail(config.mailsender, email, message)
    server.quit()


if __name__ == "__main__":
    app.run(debug=True)
