from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
from . import Permission, Role
from .. import db, login_manager

class Submission(db.Model):
    
    __tablename__ = 'submission'

    id = db.Column(db.Integer, primary_key=True)
    notas = db.Column(db.String, unique=False) #notas1 TYPE
    #utente = db.Column(db.String) #notas2 TYPE
    diag_id = db.Column(db.Integer, db.ForeignKey('diagnostico.id'))
    diag = db.relationship('Diagnostico')

    dor = db.Column(db.Integer)
    dn4 = db.Column(db.Integer)
    localizacao_id = db.Column(db.String, db.ForeignKey('anatomia.id'))
    localizacao = db.relationship('Anatomia')
    area = db.Column(db.Float)
    sub_images = db.relationship('Images', backref='sub')
    stamp_save = db.Column(db.DateTime,unique = False)
    id_pac = db.Column(db.Integer, db.ForeignKey('paciente.id'))

    def __repr__(self):
        return '<Submission(id=%r)>'%(str(self.id))



class Images(db.Model):

    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    img_name= db.Column(db.String, unique=True)
    img_data = db.Column(db.LargeBinary, unique=False)
    stamp_save = db.Column(db.DateTime,unique = False)
    stamp_acquisiton = db.Column(db.String,unique = False)
    #id_pac = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    '''
    __tablename__ = 'sessao'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime)
    imagem = db.Column(db.String)
    id_user = db.Column(db.Integer, db.ForeignKey('utilizador.id'))
    id_pac = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    '''
    def __repr__(self):
        return '<Images(img_name=%r)>'%(self.img_name)


class Diagnostico(db.Model): #Doenças
    '''
    __tablename__ = 'utilizador'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    id_sessao = db.Column(db.Integer, db.ForeignKey('sessao.id')) 
    '''
    id = db.Column(db.Integer, primary_key=True)
    diag_type = db.Column(db.String, unique = True)
    sub_diag = db.relationship('Submission', backref='diagnostico')

    def __repr__(self):
        return'<Diagnostico %r>' % (self.id)


class Anatomia(db.Model):
    '''
    __tablename__ = 'paciente'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    id_sessao = db.Column(db.Integer, db.ForeignKey('sessao.id'))
    '''
    
    id = db.Column(db.Integer, primary_key=True)
    membros = db.Column(db.String)
    ana_localizacao = db.relationship('Submission', backref='anatomia')


    def __repr__(self):
        return'<Anatomia %r>' % (self.id)


class Paciente(db.Model):
    
    __tablename__ = 'paciente'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True)
    id_pacient = db.relationship('Submission', backref='paciente')
    
    def __repr__(self):
        return '<Paciente \'%s\'>' % (self.nome) 

#user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#security = Security(app, user_datastore)

