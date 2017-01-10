from flask import Flask, render_template, flash, request, url_for, redirect, session

from wtforms import Form, BooleanField, TextField, StringField, PasswordField, validators

from functools import wraps

from passlib.hash import sha256_crypt

from MySQLdb import escape_string as thwart

from dbConnect import connection

import gc

import os

import subprocess

from werkzeug import secure_filename

import threading

import time


import bridge






UPLOAD_FOLDER = 'bots/'
ALLOWED_EXTENSIONS = set([ 'c', 'cpp', 'java'])

app = Flask(__name__)
app. secret_key = 'some_secret_key'
app. config[ 'UPLOAD_FOLDER'] = UPLOAD_FOLDER










def logoutRequired( f):
    @wraps( f)
    def wrap( *args, **kwargs):
        if 'logged_in' in session:
            flash( "Please logout first")
            return redirect( url_for( "dashboard") )
        else:
            return f( *args, **kwargs)

    return wrap










@app. route( "/", methods = ["GET", "POST"])
@logoutRequired
def login():
    try:
        error = ""

        if request. method == "POST":

            c, conn = connection()
            c. execute( "SELECT username, uid, password FROM users WHERE username = (%s)", (thwart( request. form[ 'username']), ) )

            for row in c:
                if sha256_crypt. verify( request. form[ 'password'], row[ 2] ):

                    session[ 'logged_in'] = True
                    session[ 'username'] = request. form[ 'username']

                    flash( "Login Successful!")
                    gc. collect()
                    c. close()
                    conn. close()
                    return redirect(url_for("dashboard"))

            error = "Invalid Credentials"
            gc. collect()
            c. close()
            conn. close()
            return render_template( "login.html", error = error)

        return render_template( "login.html", error = error)

    except Exception as e:
        #return( str( e) )
        return render_template( "login.html", error = "exceptOccured")












class RegistrationForm(Form):
    username = StringField('Choose new username', [validators.Length(min=3, max=25)])
    password = PasswordField('Choose new password', [
        validators.DataRequired()
    ])
    confirm = PasswordField('Re-enter password', [
        validators.EqualTo('password', message='Passwords must match')
    ])
    accept_TnC = BooleanField('I accept Terms & Conditions', [validators.DataRequired()])




@app. route( '/register/', methods = ["GET", 'POST'])
@logoutRequired
def register_page():
    try:

        form = RegistrationForm( request. form)
        error = ""

        if request. method == 'POST' and form. validate():

            username = form. username. data
            password = sha256_crypt. encrypt( str( form. password. data) )

            c, conn = connection()

            x = c. execute( "SELECT * FROM users WHERE username = (%s)", (thwart( username), ) )

            if int( x) > 0:

                error = "Username already taken :("
                return render_template( "register.html", form = form, error = error)

            else:
                c. execute( "INSERT INTO users (username, password) VALUES (%s, %s)",
                                                (thwart( username), thwart( password),)
                                                )

                conn. commit()
                flash( "Registration Complete")
                c. close()
                conn. close()
                gc. collect()

                session[ 'logged_in'] = True
                session[ 'username'] = username

                return redirect( url_for( 'dashboard') )

        return render_template( "register.html", form = form, error = error)

    except Exception as e:
        #return( str( e) )
        return render_template( "register.html")









def loginRequired( f):
    @wraps( f)
    def wrap( *args, **kwargs):
        if 'logged_in' in session:
            return f( *args, **kwargs)
        else:
            flash( "Please login first")
            return redirect( url_for( "login") )

    return wrap








@app. route( "/logout/")
@loginRequired
def logout():
    session. clear()
    flash( "Successfully logged out")
    gc. collect()
    return redirect( url_for( "login") )





class threadFunc( threading. Thread):

    def __init__( self, bot1, bot2):

        threading. Thread. __init__( self)
        self. bot1 = bot1
        self. bot2 = bot2


    def run( self):

        time. sleep( 3)
        os. chdir( "/home/vinay/Desktop/python/flask/pocketTanks/bots/")
        os. system( "java judge " + self. bot1 + " " + self. bot2)






@app. route( "/dashboard/", methods = ["GET", "POST"])
@loginRequired
def dashboard():
    try:
        submissions = []

        c, conn = connection()

        username = session[ 'username']

        c. execute( "select uid from users where username = (%s)", (username, ) )

        uid = c. fetchone()[ 0]

        if request. method == "POST":

            c. execute( "update bots set usersLastSubmission = 0 where uid = (%s)", (uid, ) )

            botID = 1

            c. execute( "select max( botID) from bots")
            st = str( c. fetchone()[ 0] )

            if st != 'None':
                botID = int( st) + 1


            fObj = request.files['file']
            fileName, fileExt = os. path. splitext( fObj. filename)
            fObj. filename = str( botID ) + fileExt
            fObj. save( os. path. join( app. config[ 'UPLOAD_FOLDER'], secure_filename( fObj.filename) ) )



            c. execute( "select botID, extn from bots where usersLastSubmission = 1")

            for row in c:
                if row[ 0] == "None":
                    break

                opponent = str( row[ 0] ) + row[ 1]

                thread1 = threadFunc( fObj. filename, opponent)
                thread1. start()






            c. execute( "insert into bots (botID, uid, usersLastSubmission, extn) values (%s, %s, 1, %s)",
                                        (botID, uid, fileExt, )
                    )
            conn. commit()


            gc. collect()
            render_template( "dashboard.html", submissions = submissions)




        c. execute( "select botID from bots where uid = (%s)", (uid, ))

        for row in c:
            submissions. append( row[ 0] )



        gc. collect()
        return render_template( "dashboard.html", user = username, submissions = submissions)



    except Exception as e:
        return( str( e) )
        #return render_template( "dashboard.html", error = str( e) )












if __name__ == "__main__":

    app.debug = True
    app.run()
