# encoding=utf8 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#import random
#from deskDB import desks


from flask import Flask, render_template, request , json, session, redirect
from flask.ext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import string

app = Flask(__name__)
mysql = MySQL()
app.secret_key = 'why would I tell you my secret key?'

 # MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'dbgood'
app.config['MYSQL_DATABASE_DB'] = 'dbDeskProject'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)




@app.route("/")
def main():
	return render_template('index.html')



@app.route("/showSignUp")
def showSignUp():
	return render_template('signup.html')


@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
       return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        

        
        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()
        print(data)

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
               session['user'] = data[0][0]
               return redirect('/userHome')
            else:
               return render_template('error.html',error = 'Wrong NikcName or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

	
@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
	try:
		_name = request.form['inputName']
		_nickName = request.form['inputEmail']
		_password = request.form['inputPassword']

		if _name and _nickName and _password:
			conn = mysql.connect()
			cursor = conn.cursor()
			_hashed_password = generate_password_hash(_password)
			cursor.callproc('sp_createUser',(_name,_nickName,_hashed_password))
			data = cursor.fetchall()
	 
			if len(data) is 0:
	   			conn.commit()
	    		return json.dumps({'message':'User created successfully !'})
	    	else: 
				return json.dumps({'error':str(data[0])})

		#else:
		#	return json.dumps({'html':'<span>Enter the required fields</span>'})
			
	except Exception as e:
		return json.dumps({'error':str(e)})
	finally:
		cursor.close() 
		conn.close()


@app.route('/showAddDesk')
def showAddDesk():
    return render_template('addDesk.html')

@app.route('/addWish',methods=['POST'])
def addWish():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _img = request.form['pic']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addDesk',(_title,_img,_user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')

        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
	app.run(debug=True, port=5001)

