from flask import Flask, request, jsonify, json
from flask.sessions import NullSession
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os



app=Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db=SQLAlchemy(app)
#Init ma
ma=Marshmallow(app)


class Hectareas(db.Model):
    __tablename__ = 'registro'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, unique=True)
    empresa_id = db.Column(db.Integer, unique=True)
    ha = db.Column(db.Float)

    def __init__(self, usuario_id, empresa_id, ha):
        self.usuario_id = usuario_id
        self.empresa_id = empresa_id
        self.ha = ha


class HectareaSchema(ma.Schema):
    class Meta:
        fields = ('id','usuario_id', 'empresa_id', 'ha')


hectarea_schema = HectareaSchema()
hectareas_schema = HectareaSchema(many=True)


@app.route('/nuevo', methods=['POST'])
def add_regisro():    
    usuario = request.json['usuario_id']    
    empresa = request.json['empresa_id']
    ha = request.json['ha']

    result = (db.session.query(Hectareas)
        .filter_by(usuario_id = usuario) \
        .filter_by(empresa_id = empresa)
        .first()
    )
    
    if result is None:
        new_registro = Hectareas(usuario, empresa, ha)   
        db.session.add(new_registro)
        db.session.commit()
        return hectarea_schema.jsonify(new_registro) 
    else:        
        result.ha = Hectareas.ha + ha
        db.session.commit()
        return hectarea_schema.jsonify(result)  
 


@app.route('/empresa/<id>', methods=['GET'])
def get_empresa(id):
    empresa=Hectareas.query.filter_by(empresa_id=id)
    return hectareas_schema.jsonify(empresa)


@app.route('/usuario/<id>', methods=['GET'])
def get_usuario(id):  
    usuario = Hectareas.query.filter_by(usuario_id=id)
    return hectareas_schema.jsonify(usuario)

@app.route('/registros', methods=['GET'])
def get_registros():
    all_registros=Hectareas.query.all()
    result=hectareas_schema.dump(all_registros)    
    return jsonify(result), 200

#Run Server
if __name__ == '__main__':
    app.run(debug=True)
