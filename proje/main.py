

from datetime import date

import login as login
from flask import Flask, render_template, request, url_for, Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, login_required, logout_user
from flask_login import LoginManager
from flask_login import current_user
import psycopg2
import psycopg2.extras
from werkzeug.utils import redirect
import re

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/proje'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = "secret123"

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class Iller(db.Model):
    __tablename__ = 'iller'

    ilid = db.Column(db.String(100), primary_key=True)
    ilismi = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, ilid, ilismi):
        self.iladi = ilid
        self.ilkodu = ilismi

class Ilceler(db.Model):
    __tablename__ = 'ilceler'

    ilid = db.Column(db.String(100), db.ForeignKey('iller.ilid'),primary_key=True)
    ilceid = db.Column(db.String(100), primary_key=True,unique=True)
    ilceismi = db.Column(db.String(100))

    def __init__(self, ilid, ilceid, ilceismi):
        self.ilceid=ilceid
        self.ilid=ilid
        self.ilceismi=ilceismi




class Semtler(db.Model):
    __tablename__ = 'semtler'

    ilceid = db.Column(db.String(100), db.ForeignKey('ilceler.ilceid'))
    semtid = db.Column(db.String(100), primary_key=True)
    semtismi = db.Column(db.String(100))

    def __init__(self, ilceid, semtid, semtismi):
        self.ilceid=ilceid
        self.semtid=semtid
        self.semtismi=semtismi


class GuzellikSalonTurleri(db.Model):
    __tablename__ = 'guzelliksalonturleri'

    gstid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    gstismi = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self,gstismi):

        self.gstismi=gstismi



class GuzellikSalonlari(db.Model):
    __tablename__ = 'guzelliksalonlari'

    gsid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    gsadi= db.Column(db.String(100))
    semtid = db.Column(db.String(100), db.ForeignKey('semtler.semtid'))
    gstid = db.Column(db.Integer,db.ForeignKey('guzelliksalonturleri.gstid'))

    def __init__(self, semtid, gstid,gsadi):
        self.semtid=semtid
        self.gstid=gstid
        self.gsadi=gsadi


class Personeller(db.Model):
    __tablename__ = 'personeller'

    ssn = db.Column(db.String(100), primary_key=True)
    personelismi    = db.Column(db.String(100))
    personelsoyismi = db.Column(db.String(100))
    gsid = db.Column(db.Integer,db.ForeignKey('guzelliksalonlari.gsid'))

    def __init__(self, ssn,personelismi,personelsoyismi,gsid):
        self.ssn=ssn
        self.personelismi=personelismi
        self.personelsoyismi=personelsoyismi
        self.gsid=gsid


class Kampanyalar(db.Model):
    __tablename__ = 'kampanyalar'

    kampanyaid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    kampanyaismi = db.Column(db.String(100))

    def __init__(self,kampanyaismi):
        self.kampanyaismi=kampanyaismi


class SalonKampanyalar(db.Model):
    __tablename__ = 'salonkampanyalar'

    kampanyaid = db.Column(db.Integer,db.ForeignKey('kampanyalar.kampanyaid'), primary_key=True)
    gsid = db.Column(db.Integer,db.ForeignKey('guzelliksalonlari.gsid'),primary_key=True)

    def __init__(self, kampanyaid,gsid):
        self.kampanyaid=kampanyaid
        self.gsid=gsid


class Puanlar(db.Model): #sapma
    __tablename__ = 'puanlar'

    puanid = db.Column(db.String(100), primary_key=True)
    puan = db.Column(db.String(100))

    def __init__(self, puanid,puan):
        self.puanid=puanid
        self.puan=puan


class Anketler(db.Model): #sapma
    __tablename__ = 'anketler'

    anketno = db.Column(db.String(100), primary_key=True)
    ankettarihi    = db.Column(db.String(100))
    anketsorusu = db.Column(db.String(100))
    puanid = db.Column(db.String(100),db.ForeignKey('puanlar.puanid'))

    def __init__(self, anketno,ankettarihi,anketsorusu,puanid):
        self.anketsno=anketno
        self.ankettarihi=ankettarihi
        self.anketsorusu=anketsorusu
        self.puanid=puanid


class Randevular(db.Model): #sapma
    __tablename__ = 'randevular'

    randevuid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    uygunlukbilgisi    = db.Column(db.String(100))
    musteriid = db.Column(db.Integer,db.ForeignKey('musteriler.musteriid'))
    gsid = db.Column(db.Integer,db.ForeignKey('guzelliksalonlari.gsid'))

    def __init__(self,uygunluk_bilgisi,musteriid,gsid):
        self.uygunlukbilgisi=uygunluk_bilgisi
        self.musteriid=musteriid
        self.gsid=gsid



class Iletisimler(db.Model):
    __tablename__ = 'iletisimler'

    telefonno = db.Column(db.String(100), primary_key=True)
    adresbilgisi    = db.Column(db.String(100))
    eposta = db.Column(db.String(100))
    gsid = db.Column(db.Integer,db.ForeignKey('guzelliksalonlari.gsid'))
    musteriid = db.Column(db.Integer, db.ForeignKey('musteriler.musteriid'))

    def __init__(self, telefonno,adresbilgisi,eposta,gsid,musteriid):
        self.telefonno=telefonno
        self.adresbilgisi=adresbilgisi
        self.eposta=eposta
        self.gsid=gsid
        self.musteriid=musteriid


class HizmetTurleri(db.Model):
    __tablename__ = 'hizmetturleri'

    hizmetturu = db.Column(db.String(100), primary_key=True)

    def __init__(self, hizmetturu):
        self.hizmetturu=hizmetturu


class Hizmetler(db.Model):
    __tablename__ = 'hizmetler'

    hizmetismi = db.Column(db.String(100), primary_key=True)
    hizmetturu = db.Column(db.String(100), db.ForeignKey('hizmetturleri.hizmetturu'))

    def __init__(self, hizmetismi,hizmetturu):
        self.hizmetismi=hizmetismi
        self.hizmetturu=hizmetturu

class Musteriler(db.Model): #sapma
    __tablename__ = 'musteriler'

    musteriid     = db.Column(db.Integer, primary_key=True,autoincrement=True)
    musteriismi   = db.Column(db.String(100))
    musterisoyismi= db.Column(db.String(100))

    def __init__(self,musteriismi,musterisoyismi):
        self.musteriismi=musteriismi
        self.musterisoyismi=musterisoyismi


class MusteriHizmetler(db.Model): # sapma
    __tablename__ = 'musterihizmetler'

    hizmetismi  = db.Column(db.String(100),db.ForeignKey('hizmetler.hizmetismi') ,primary_key=True)
    musteriid   = db.Column(db.Integer, db.ForeignKey('musteriler.musteriid'),primary_key=True)
    gerceklesmis= db.Column(db.String(100))

    def __init__(self, hizmetismi,musteriid,gerceklesmis):
        self.hizmetismi=hizmetismi
        self.musteriid=musteriid
        self.gerceklesmis=gerceklesmis


class GSHizmetler(db.Model): # sapma
    __tablename__ = 'gshizmetler'

    hizmetismi  = db.Column(db.String(100),db.ForeignKey('hizmetler.hizmetismi') ,primary_key=True)
    gsid   = db.Column(db.Integer, db.ForeignKey('guzelliksalonlari.gsid'),primary_key=True)


    def __init__(self, hizmetismi,gsid):
        self.hizmetismi=hizmetismi
        self.gsid=gsid



class Kullanicilar(UserMixin, db.Model):#sapma
    __tablename__ = 'kullanicilar'
    kullaniciadi = db.Column(db.String(100), primary_key=True)
    sifre = db.Column(db.String(100))
    tur   = db.Column(db.String(100))
    gsid= db.Column(db.Integer,db.ForeignKey('guzelliksalonlari.gsid'))
    musteriid=db.Column(db.Integer,db.ForeignKey('musteriler.musteriid'))

    def get_id(self):
        return (self.kullaniciadi)

    def __init__(self, kullaniciadi, sifre,tur,gsid,musteriid):
        self.kullaniciadi = kullaniciadi
        self.sifre = sifre
        self.tur=tur
        self.gsid=gsid
        self.musteriid=musteriid

@login_manager.user_loader
def load_user(kullaniciadi):
    return Kullanicilar.query.get(kullaniciadi)


@app.route('/')
def Index():
    return render_template('login.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    kullaniciadi = request.form.get('kullaniciadi')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    kullanici = Kullanicilar.query.filter_by(kullaniciadi=kullaniciadi).first()

    if not kullanici or not check_password_hash(kullanici.sifre, password):
        flash('Giris bilgileriniz yanlis, tekrar deneyiniz.')
        return redirect('/login')

    login_user(kullanici, remember=remember)
    if kullanici.tur=="salon":
        return redirect('/salonprofile')
    elif kullanici.tur=="musteri":
        return redirect('/musteriprofile')
    else:
        flash('Bir seyler ters gitti,sonra tekrar deneyiniz')
        return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@login_required
@app.route('/salonprofile')
def salonprofil():
    ilgiliKampanyalar= Kampanyalar.query \
        .join(SalonKampanyalar,Kampanyalar.kampanyaid==SalonKampanyalar.kampanyaid) \
        .filter_by(gsid=current_user.gsid)

    ilgiliRandevular = Randevular.query \
        .filter_by(gsid=current_user.gsid)

    ilgiliHizmetler = Hizmetler.query \
        .join(GSHizmetler,GSHizmetler.hizmetismi==Hizmetler.hizmetismi)\
        .filter_by(gsid=current_user.gsid)

    return render_template('salonprofile.html',kampanyalar=ilgiliKampanyalar,randevular=ilgiliRandevular,hizmetler=ilgiliHizmetler)


@login_required
@app.route('/musteriprofile')
def musteriprofil():
    ilgiliRandevular = Randevular.query.filter_by(musteriid=current_user.musteriid)

    gerceklesmisHizmetler= Hizmetler.query \
        .join(MusteriHizmetler,MusteriHizmetler.hizmetismi==Hizmetler.hizmetismi)\
        .filter_by(musteriid=current_user.musteriid)\
        .filter_by(gerceklesmis="True")

    gerceklesecekHizmetler= Hizmetler.query \
        .join(MusteriHizmetler,MusteriHizmetler.hizmetismi==Hizmetler.hizmetismi)\
        .filter_by(musteriid=current_user.musteriid)\
        .filter_by(gerceklesmis="False")

    return render_template('musteriprofile.html',randevular=ilgiliRandevular,gerceklesmisHizmetler=gerceklesmisHizmetler,gerceklesecekHizmetler=gerceklesecekHizmetler)


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signupmusteri')
def signupmusteri():
    return render_template('signupmusteri.html')

@app.route('/signup/<kayitturu>', methods=['POST'])
def signup_post(kayitturu):
    kullaniciadi = request.form.get('name')
    password = request.form.get('password')

    kullanici = Kullanicilar.query.filter_by(kullaniciadi=kullaniciadi).first()

    if kullanici:
        flash("Kullanici adi kullanilmaktadir.")
        print("asdasdsa")
        return redirect('/signup')

    match = re.findall('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_=+-]).{8,}$', password)
    print(len(match))

    if len(match) == 0:
        flash(
            'Kullanici adi en az bir buyuk harf bir kucuk harf bir rakam bir noktalama isareti icermeli ve 8 karakter ya da daha uzun olmalidir.')
        return redirect('/signup')

    if kayitturu=="salon":
        semt = Semtler.query.filter_by(semtismi=request.form['semtismi']).first()
        gst  = GuzellikSalonTurleri.query.filter_by(gstismi=request.form['gstismi']).first()
        gsadi  = request.form['gsadi']
        print("GSADI"+gsadi)
        yenisalon = GuzellikSalonlari(semt.semtid,gst.gstid,gsadi)
        db.session.add(yenisalon)
        db.session.commit()
        yenikullanici = Kullanicilar(kullaniciadi, sifre=generate_password_hash(password, method='sha256'),tur=kayitturu,gsid=yenisalon.gsid,musteriid=None)
        print(yenisalon)

    else:
        yenimusteri = Musteriler(request.form['musteriismi'],request.form['musterisoyismi'])
        db.session.add(yenimusteri)
        db.session.commit()
        yenikullanici = Kullanicilar(kullaniciadi,sifre=generate_password_hash(password, method='sha256'),tur=kayitturu,musteriid=yenimusteri.musteriid,gsid=None)

    db.session.add(yenikullanici)
    db.session.commit()

    return redirect('/login')



@app.route('/create/<tablename>',methods=['POST'])
def create(tablename):
    if (tablename == "kampanyalar"):
        if request.method == 'POST':

            kampanyaadi=request.form['kampanyaadi']
            gsid=current_user.gsid
            yenikampanya= Kampanyalar(kampanyaadi)
            db.session.add(yenikampanya)
            db.session.commit()

            kampanyasalon=SalonKampanyalar(yenikampanya.kampanyaid,gsid)

            db.session.add(kampanyasalon)
            db.session.commit()
            if current_user.tur == "musteri":
                return redirect("/musteriprofile")
            else:
                return redirect("/salonprofile")
    elif(tablename=="randevular"):
        if request.method == 'POST':

            uygunluk_bilgisi="uygundur"

            musteriid=current_user.musteriid
            gsid = GuzellikSalonlari.query.filter_by(gsadi=request.form['gsadi']).first()

            randevu = Randevular(uygunluk_bilgisi=uygunluk_bilgisi,musteriid=musteriid,gsid=gsid.gsid)
            db.session.add(randevu)
            db.session.commit()
            if current_user.tur == "musteri":
                return redirect("/musteriprofile")
            else:
                print("HATA OLDU")
    elif(tablename=="hizmetler"):
        hizmetadi = request.form['hizmetadi']
        hizmetturu= request.form['hizmetturu']

        ht = HizmetTurleri.query.get(hizmetturu)
        hizmet=Hizmetler.query.get(hizmetadi)
        hizmetyenieklendi=False
        if not ht:
            yenihizmetturu= HizmetTurleri(hizmetturu)
            db.session.add(yenihizmetturu)
            db.session.commit()
        if not hizmet:
            yenihizmet= Hizmetler(hizmetadi,hizmetturu)
            db.session.add(yenihizmet)
            db.session.commit()
            hizmetyenieklendi=True

        if hizmetyenieklendi:
            yenigshizmet=GSHizmetler(yenihizmet.hizmetismi,current_user.gsid)
            db.session.add(yenigshizmet)
            db.session.commit()
        else:
            varolanhizmet = Hizmetler.query.filter_by(hizmetismi=hizmetadi).first()
            yenigshizmet=GSHizmetler(varolanhizmet.hizmetismi,current_user.gsid)
            db.session.add(yenigshizmet)
            db.session.commit()

        return redirect('/salonprofile')


@app.route('/update/<tablename>/<pk>')
@login_required
def updateGet(tablename,pk):
    if(tablename=="randevular"):
        r=Randevular.query.get(pk)
        return render_template('randevuedit.html',pk=pk,randevular=r)
    elif(tablename=="kampanyalar"):
        k=Kampanyalar.query.get(pk)
        return render_template('kampanyaedit.html',pk=pk,kampanyalar=k)
    elif(tablename=="hizmetler"):
        h=Hizmetler.query.get(pk)
        return render_template('hizmetedit.html',pk=pk,hizmetler=h)


@app.route('/update/<tablename>/<pk>', methods=['POST'])
@login_required
def update(tablename, pk):
    if (tablename == "randevular"):
        my_data = Randevular.query.get(pk)
        print("DATA====")
        print(my_data)

        my_data.uygunlukbilgisi=request.form['uygunlukbilgisi']
        db.session.commit()

        if current_user.tur=="musteri":
            return redirect("/musteriprofile")
        else:
            return redirect("/salonprofile")

    elif (tablename == "kampanyalar"):
        my_data = Kampanyalar.query.get(pk)
        print(my_data)

        my_data.kampanyaismi=request.form['kampanyaadi']
        db.session.commit()
        if current_user.tur=="musteri":
            return redirect("/musteriprofile")
        else:
            return redirect("/salonprofile")
    elif (tablename == "hizmetler"):
        my_data = Hizmetler.query.get(pk)
        my_data.hizmetismi=request.form['hizmetismi']
        db.session.commit()
        if current_user.tur=="musteri":
            return redirect("/musteriprofile")
        else:
            return redirect("/salonprofile")



@app.route('/delete/<tablename>/<pk>')
@login_required
def delete(tablename,pk):
    if(tablename=="randevular"):
        rtodelete=Randevular.query.get(pk)
        db.session.delete(rtodelete)
        db.session.commit()
        if current_user.tur=="salon":
            return redirect('/salonprofile')
        else:
            return redirect('/musteriprofile')
    elif(tablename=="kampanyalar"):
        sktodelete= SalonKampanyalar.query.get((pk,current_user.gsid))
        db.session.delete(sktodelete)
        db.session.commit()

        ktodelete=Kampanyalar.query.get(pk)
        db.session.delete(ktodelete)
        db.session.commit()
        if current_user.tur=="salon":
            return redirect('/salonprofile')
        else:
            return redirect('/musteriprofile')
    elif(tablename=="hizmetler"):
        gstodelete=GSHizmetler.query.get((pk,current_user.gsid))
        db.session.delete(gstodelete)
        db.session.commit()

        htodelete=Hizmetler.query.get(pk)
        db.session.delete(htodelete)
        db.session.commit()
        if current_user.tur=="salon":
            return redirect('/salonprofile')
        else:
            return redirect('/musteriprofile')





if __name__ == '__main__':
    app.run()

