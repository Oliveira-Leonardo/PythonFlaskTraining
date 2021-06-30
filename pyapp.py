#!/usr/bin/env python
from flask import Flask, Response, request
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
import urllib.parse 
import json



# Configure Database URI: 
params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=python-data.database.windows.net;DATABASE=python-data;UID=oliverleo;PWD=A1b02C13!")


# initialization
app = Flask(__name__)
#app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params


# extensions
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column (db.String(100))
    cidade = db.Column(db.String(100))
    idade = db.Column(db.Integer)

    def to_json(self):
        return {"id":self.id, "nome":self.nome, "cidade":self.cidade, "idade":self.idade}



##############
#Selecionar Tudo


@app.route("/usuarios", methods=['GET'])
#@cross_origins()
def seleciona_usuarios():
    users_objeto =Users.query.all()

    users_json = [users.to_json() for users in users_objeto]

    return gera_response(200, "usuarios", users_json)


# Selecionar Individual
@app.route("/usuario/<id>", methods=['GET'])
def seleciona_usuario(id):
    users_objeto = Users.query.filter_by(id=id).first()
    users_json = users_objeto.to_json()


    return gera_response(200, "Usuario", users_json)


#Cadastro
@app.route("/usuario", methods=['POST'])
def cria_usuario():
    body = request.get_json() 
    try:
        user = Users(nome=body["nome"],cidade= body["cidade"], idade= body["idade"])
        db.session.add(user)
        db.session.commit()
        return gera_response(201, "usuario", user.to_json(), "criado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "usuario",{},"Erro ao cadastrar")


#update
@app.route("/usuario/<id>", methods=["PUT"])
def atualiza_usuario(id):
    users_objeto = Users.query.filter_by(id=id).first()
    body = request.get_json() 

    try:
        if('nome' in body):
            users_objeto.nome= body['nome']
        if('cidade' in body):
            users_objeto.cidade= body['cidade']
        if('idade' in body):
            users_objeto.idade= body['idade']
        
        db.session.add(users_objeto)
        db.session.commit()
        return gera_response(200, "usuario", users_objeto.to_json(), "atualizado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "usuario",{},"erro ao atualizar")




#deletar

@app.route("/usuario/<id>", methods=['DELETE'])
def deleta_usuario(id):
    users_objeto = Users.query.filter_by(id=id).first()


    try:
        db.session.delete(users_objeto)
        db.session.commit()
        return gera_response(200, "usuario", users_objeto.to_json(), "deletado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "usuario",{},"erro ao deletar")




def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body={}
    body[nome_do_conteudo] = conteudo

    if (mensagem):
        body["mensagem"] = mensagem

    return Response (json.dumps(body), status=status, mimetype="application/json")


app.run()