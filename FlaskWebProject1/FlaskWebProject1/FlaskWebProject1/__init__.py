from flask import Flask, render_template,request,session
import sqlite3
import csv
import datetime
import pytesseract as tess
from PIL import Image
#Egemen KILIÇ 170201084
tess.pytesseract.tesseract_cmd=r'your tesseract'

app = Flask(__name__)
app.secret_key="egemen"

day= datetime.datetime.now().strftime("%d");
month= datetime.datetime.now().strftime("%m");
year= datetime.datetime.now().strftime("%Y");

time='7'#kitabı geri verme süresi


date= (day+"-"+month+"-"+year);


@app.route("/")
def anasayfa():
    return render_template('main.html')

@app.route("/main.html",methods=["GET"])
def get_anasayfa():
    return render_template('main.html')


#KAYIT OL ------------------------------------------------------------------------------------------------
@app.route("/signup.html",methods=["GET"])
def get_signup():
    return render_template('signup.html')


@app.route("/signup.html",methods=["POST"])
def post_signup():

        name=request.form["name"]
        password=request.form["password"]

        con=sqlite3.connect("Library.db")   
        cursor = con.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Users(name TEXT,password TEXT)")

        cursor.execute("SELECT * FROM Users")
        users=cursor.fetchall()
        i=0
        j=0

        for i in range(len(users)):
            if (users[i][0] == name and users[i][1]== password):
                j=j+1
                return "Zaten Kayıtlısınız..."

        
        if j==0:
          cursor.execute("INSERT INTO Users(name,password) VALUES(?,?)",(name,password))
          con.commit()
          return "Kayıt Alındı"
      
#KAYIT OL ------------------------------------------------------------------------------------------------

#GİRİŞ YAP ------------------------------------------------------------------------------------------------
@app.route("/signin.html",methods=["GET"])
def get_signin():
    return render_template('signin.html')


@app.route("/signin.html",methods=["POST"])
def post_signin():

        name=request.form["name"]
        password=request.form["password"]
        
        session["user_name"]=name

        con=sqlite3.connect("Library.db")   
        cursor = con.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Users(name TEXT,password TEXT)")
        con.commit()

        cursor.execute("SELECT * FROM Users")
        users=cursor.fetchall();
        i=-1

        if name=="admin" and password=="admin":
            return render_template('adminpage.html')

        else:
            while True:

                i=i+1

                if i== len(users):
                    break

                if (users[i][0] == name and users[i][1] == password):
                    return render_template ("userspage.html")

            return "Hatalı Giriş"
#GİRİŞ YAP ------------------------------------------------------------------------------------------------




#KULLANICI LİSTELE ------------------------------------------------------------------------------------------------
@app.route("/listusers.html",methods=["GET"])
def get_listusers():
    return render_template('listusers.html')


@app.route("/listusers.html",methods=["POST"])
def post_listusers():

        con=sqlite3.connect("Library.db")   
        cursor = con.cursor()
        cursor.execute("SELECT Users.name,Books.ISBN,Books.name,books.author FROM Users INNER JOIN Books ON users.name=books.control")
        con.commit() 
        users=cursor.fetchall();

        return render_template('listusers.html',users=users)
#KULLANICI LİSTELE ------------------------------------------------------------------------------------------------


#KİTAP EKLE ------------------------------------------------------------------------------------------------
@app.route("/addbook.html",methods=["GET"])
def get_addbook():
    return render_template('addbook.html')

@app.route("/addbook.html",methods=["POST"])
def post_addbook():

    ISBN=request.form["ISBN"]
    name=request.form["name"]
    author=request.form["author"]
    control=""
    t=""
    tt="0"
    conf="Kitap ekleme işlemi başarıyla gerçekleştirildi."
    if "ISBN_no" in session:
        ISBN_no=session["ISBN_no"]
    
    
    con=sqlite3.connect("Library.db")   
    cursor = con.cursor()
    cursor.execute("INSERT INTO Books(ISBN,name,author,control,taketime,time) VALUES(?,?,?,?,?,?)",(ISBN_no,name,author,control,t,tt))
    con.commit()
 
   
    return render_template('addbook.html',conf=conf)

#KİTAP EKLE ------------------------------------------------------------------------------------------------

#KİTAP LİSTELE ------------------------------------------------------------------------------------------------
@app.route("/listbooks.html",methods=["GET"])
def get_listbooks():
    return render_template('listbooks.html')

@app.route("/listbooks.html",methods=["POST"])
def post_listbooks():

    ISBN=request.form["ISBN"]
    name=request.form["name"]
    control=""
    
    con=sqlite3.connect("Library.db")   
    cursor = con.cursor()

    if ISBN=="" and name=="":
        cursor.execute("SELECT Books.ISBN,Books.name,Books.author,Books.control FROM Books")
        con.commit()
        books=cursor.fetchall();
        return render_template('listbooks.html',books=books)
    else:
        cursor.execute("SELECT * FROM Books WHERE name='"+name+"' OR ISBN='"+ISBN+"'")
        con.commit()
        books=cursor.fetchall();
        return render_template('listbooks.html',books=books)

    

#KİTAP LİSTELE ------------------------------------------------------------------------------------------------


#KİTAP AL ------------------------------------------------------------------------------------------------
@app.route("/takebook.html",methods=["GET"])
def get_takebook():
    return render_template('takebook.html')

@app.route("/takebook.html",methods=["POST"])
def post_takebook():

    ISBN=request.form["ISBN"]
    name=request.form["name"]
    

    if "user_name" in session:
        user_name=session["user_name"]

    con=sqlite3.connect("Library.db")   
    cursor = con.cursor()
    cursor1=con.cursor()

    cursor1.execute("SELECT Books.time FROM books where Books.control='"+user_name+"'")
    count=cursor1.fetchall()


    cursor.execute("SELECT Books.control FROM Books WHERE name='"+name+"' OR ISBN='"+ISBN+"'")
    control=cursor.fetchall()

    a=0

    error=""
    conf=""
    error2=""
    error3=""


    for i in range (len(count)):
        if int(count[i][0]) < int(0):
            a=a+1

    if a >= 1:
        error3="Teslim etmeniz gereken kitaplar mevcut.Teslim etmeden kitap alamazsınız"
        return render_template('takebook.html',error3=error3)

    elif len(count)>=3:
        error2="Kitap sayınız 3 tür.Daha fazla kitap alamassınız"
        return render_template('takebook.html',error2=error2)

    elif control[0][0]=="":
        cursor.execute("UPDATE Books SET control='"+user_name+"' WHERE name='"+name+"' OR ISBN='"+ISBN+"'")
        cursor.execute("UPDATE Books SET taketime='"+date+"' WHERE name='"+name+"' OR ISBN='"+ISBN+"'")
        cursor.execute("UPDATE Books SET time='"+time+"' WHERE name='"+name+"' OR ISBN='"+ISBN+"'")
        con.commit()
        conf="Kitap alındı"
        return render_template('takebook.html',conf=conf)
    
    else:
        error="İstediğiniz kitap alınmıştır."
        return render_template('takebook.html',error=error)

#KİTAP AL ------------------------------------------------------------------------------------------------



#KİTAP VER ------------------------------------------------------------------------------------------------
@app.route("/givebook.html",methods=["GET"])
def get_givebook():
    return render_template('givebook.html')

@app.route("/givebook.html",methods=["POST"])
def post_givebook():

    ISBN=request.form["ISBN"]
    name=request.form["name"]

    if "user_name" in session:
        user_name=session["user_name"]
    
    if "ISBN_no" in session:
        ISBN_no=session["ISBN_no"]


    con=sqlite3.connect("Library.db")   
    cursor = con.cursor()

    cursor.execute("SELECT Books.control FROM Books WHERE name='"+name+"' OR ISBN='"+ISBN_no+"'")
    control=cursor.fetchall()

    error=""
    conf=""
    tt=""
    t="0"

    if control[0][0]==user_name:
        customer=""
        cursor.execute("UPDATE Books SET control='"+customer+"' WHERE name='"+name+"' OR ISBN='"+ISBN_no+"'")
        cursor.execute("UPDATE Books SET taketime='"+tt+"' WHERE name='"+name+"' OR ISBN='"+ISBN_no+"'")
        cursor.execute("UPDATE Books SET time='"+t+"' WHERE name='"+name+"' OR ISBN='"+ISBN_no+"'")
        con.commit()
        conf="Kitap teslim edildi."
        return render_template('givebook.html',conf=conf)
    
    else:
        error="Kitap teslim edilirken hata oluştu."
        return render_template('givebook.html',error=error)

#KİTAP VER ------------------------------------------------------------------------------------------------



#ZAMAN ATLA ------------------------------------------------------------------------------------------------
@app.route("/addtime.html",methods=["GET"])
def get_addtime():
    return render_template('addtime.html')


@app.route("/addtime.html",methods=["POST"])
def post_addtime():
    
    daytime=request.form["daytime"]
    con=sqlite3.connect("Library.db")   
    cursor = con.cursor()

    cursor.execute("SELECT Books.time FROM books")
    count=cursor.fetchall()
    
    conf="'"+daytime+"' gün atlanmıştır."
    t=1
    for i in range (len(count)):
        
        a = int(count[i][0]) - int(daytime)
        astr=str(a)
        tstr=str(t)
        cursor.execute("UPDATE Books SET time='"+astr+"' WHERE id='"+tstr+"'")
        con.commit()
        t=t+1
         
    
    return render_template('addtime.html',conf=conf)        
       
#ZAMAN ATLA ------------------------------------------------------------------------------------------------


#FOTOĞRAF ------------------------------------------------------------------------------------------------
@app.route("/photo.html",methods=["GET"])
def get_photo():
    return render_template('photo.html')


@app.route("/photo.html",methods=["POST"])
def post_photo():

    photo=request.form["photo"]
    #print(photo)
    
    img=Image.open(photo)

    text=tess.image_to_string(img)
    a=[]
    a=text.split()

    for i in range(len(a)):
        if(a[i]=="ISBN" or a[i]=="ISBN;" or a[i]=="ISBN:" or a[i]=="ISBN "):
            ISBN_no=a[i+1]
    
    
    session["ISBN_no"]=ISBN_no

    return "Kayıt Alındı"
      
#FOTOĞRAF ------------------------------------------------------------------------------------------------