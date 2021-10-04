from typing import Type
from flask import Blueprint, render_template, request
from flask_login.utils import login_fresh
from werkzeug.utils import secure_filename
from app.models import EditableHTML
from flask_login import login_required

from flask import Flask, render_template, Response, request, url_for, jsonify, session, make_response, abort
from flask import redirect, flash, g

from app.models.pacienteInfo import Images, Diagnostico, Paciente, Submission, Anatomia
from app.models import User
# from pain_app import app, db
from .. import db
import os
from config import *

from datetime import datetime, time, date
import urllib

import json
from werkzeug.datastructures import FileStorage
import random
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt

import json
import cv2
import io

# from flask_login import LoginManager , UserMixin , login_required ,login_user, logout_user,current_user

main = Blueprint('main', __name__)

file_path = 'uploads/photos'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html', editable_html_obj=editable_html_obj)

@main.route('/form')
@login_required
def form():
    body = [membro.membros for membro in Anatomia.query.all()]
    diags = [dor.diag_type for dor in Diagnostico.query.all()]
    #patients = ["C++", "Python", "PHP", "Java", "C", "Ruby",
                     #"R", "C#", "Dart", "Fortran", "Pascal", "Javascript"]
    return render_template('main/form.html', diags=diags, body=body)#, patients=patients)

@main.route('/handle_form', methods=['POST'])
@login_required
def handle_form():

    print(request)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        print('1')
        flash('No image selected for uploading')
        return redirect(request.url)    
    '''
    nome = request.form.get('nome')
    print('nome', nome, type(nome))
    if nome == '':
        print(request)
        flash('Please insert Pacient name')
        return redirect(request.url)
    '''
    
    if file and allowed_file(file.filename):
        load_info = {}
        filename = secure_filename(file.filename)
        
        image = file.read()
        print(type(image))
        data = np.fromstring(image, dtype=np.uint8)
        color_image_flag = 1
        img = cv2.imdecode(data, color_image_flag)

        imag = Image.open(io.BytesIO(image))
        imag.save(os.path.join(Config.UPLOAD_FOLDER, filename))

        print(filename)

        load_info['filename'] = filename
        load_info['nome'] = request.form.get('nome')
        load_info['notas'] = request.form.get('notas')
        load_info['area'] = get_pain_area(img)
        load_info['diag'] = request.form.get('diag')
        load_info['dor'] = request.form.get('dor')
        load_info['dn4'] = request.form.get('dn4')
        load_info['local'] = request.form.get('local')
        print(filename)
        save_update_db(load_info)

        flash('Image successfully uploaded and displayed below')

        return render_template('main/displayInfo.html', filename=filename, load_info=load_info)
#print("{0:.2f}".format(area))7
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

NAMES=["abc","abcd","abcde","abcdef","Ruben Sobral", "Maria João"]

@main.route('/autocomplete',methods=['GET'])
def autocomplete():
    search = request.args.get('autocomplete')
    #app.logger.debug(search)
    return Response(json.dumps(NAMES), mimetype='application/json')
    
def get_pain_area(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(blur, -1, sharpen_kernel)

    thresh = cv2.threshold(sharpen,  100, 255, cv2.THRESH_BINARY_INV)[1]
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=4)

    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    
    area = 0
    for c in cnts:
        area = cv2.contourArea(c)

    cnts_image = cv2.drawContours(img, cnts, -1, (0, 255, 0), 10)

    height, width = img.shape[:2]
    Ap = height*width
    Acm = 21 * 29.7
    area_total = area*Acm/Ap
    print(area_total) #em cm2
    return area_total
    
@main.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static', filename='uploads/' + filename),code=301)

@main.route('/save_update_db')#, methods=[ 'POST'])
def save_update_db(load_info):

    nome = load_info['nome']
    notas = load_info['notas']
    area = load_info['area']
    sub_diag = load_info['diag']
    dor = load_info['dor']
    dn4 = load_info['dn4']
    localizacao = load_info['local']
    
    print ('entrou update db')
    diag = Diagnostico.query.filter_by(diag_type=sub_diag).first()
    loc = Anatomia.query.filter_by(membros=localizacao).first()
    nome_paci = Paciente.query.filter_by(nome=nome).first()
    
    if nome_paci is None:
        nome_paci = Paciente(nome=nome)
        db.session.add(nome_paci)
        db.session.flush()
    
    print(nome_paci.id,nome, notas)
    
    newsub = Submission(id_pac=nome_paci.id, notas=notas, area=area, diag_id=diag.id, dor=dor, dn4=dn4, localizacao_id=loc.id, stamp_save=date.today())
    
    db.session.add(newsub)
    db.session.flush()

    print('ppppp   ', newsub, newsub.id )

    file_urls = []


    filename = load_info['filename']
    ext = filename.rsplit(".", 1)[1]
    new_filename = filename.rsplit(".", 1)[0]+ '_sub'+str(newsub.id)+'.'+ext

    newfile = Images( sub=newsub, img_name= new_filename, stamp_save=date.today())
    db.session.add(newfile)

    print(file_urls)
    db.session.commit()    
    session['images_urls'] = file_urls
    print('saved to database')
    return 'Saved to database'

