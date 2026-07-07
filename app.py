import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=os.path.join(base_dir, 'static')
)

# --- CONFIGURAÇÃO DA BASE DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'luxurywheels.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'luxurywheels2026'

db = SQLAlchemy(app)

# Preços por dia de cada carro
PRECOS_CARROS = {
    'Pajero Rang': 50,
    'Mirage Ranger': 40,
    'Volkswagen': 45,
    'Rolls-Royce': 200,
    'Subaru Forester': 55,
    'Porsche': 180
}

# --- MODELOS (TABELAS) ---
class Utilizador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(100), nullable=False)
    ultimo_nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    data_registo = db.Column(db.DateTime, default=datetime.utcnow)

class Reserva(db.Model):
    class Reserva(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        utilizador_id = db.Column(db.Integer, db.ForeignKey('utilizador.id'), nullable=True)
        carro = db.Column(db.String(100), nullable=False)
        local_retirada = db.Column(db.String(200))
        local_devolucao = db.Column(db.String(200))
        data_retirada = db.Column(db.String(50))
        hora_retirada = db.Column(db.String(20))
        data_devolucao = db.Column(db.String(50))
        hora_devolucao = db.Column(db.String(20))
        nome_cartao = db.Column(db.String(150))
        data_reserva = db.Column(db.DateTime, default=datetime.utcnow)

# --- ROTAS ---

# 1ª Página: Login
from flask import Flask, render_template, request, redirect, url_for, session

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        utilizador = Utilizador.query.filter_by(email=email, password=password).first()
        if utilizador:
            session['utilizador_id'] = utilizador.id
            session['utilizador_nome'] = utilizador.primeiro_nome
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro='Email ou senha incorretos.')
    return render_template('login.html')

# 2ª Página: Registo
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        primeiro_nome = request.form.get('primeiro_nome')
        ultimo_nome = request.form.get('ultimo_nome')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('register.html', erro='As senhas não coincidem.')

        email_existente = Utilizador.query.filter_by(email=email).first()
        if email_existente:
            return render_template('register.html', erro='Este email já está registado.')

        novo_utilizador = Utilizador(
            primeiro_nome=primeiro_nome,
            ultimo_nome=ultimo_nome,
            email=email,
            password=password
        )
        db.session.add(novo_utilizador)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

# 3ª Página: Home
@app.route('/index')
def index():
    return render_template('index.html')

# 4ª Página: Lista de carros
@app.route('/car_list')
def car_list():
    pesquisa = request.args.get('pesquisa', '')
    return render_template('car_list.html', pesquisa=pesquisa)

# 5ª Página: Escolher datas e locais
@app.route('/escolher-datas', methods=['GET', 'POST'])
def escolher_datas():
    if request.method == 'POST':
        carro = request.form.get('carro')
        data_retirada = request.form.get('data_levantamento')
        data_devolucao = request.form.get('data_entrega')

        # Calcular número de dias e preço total
        from datetime import datetime
        try:
            d1 = datetime.strptime(data_retirada, '%Y-%m-%d')
            d2 = datetime.strptime(data_devolucao, '%Y-%m-%d')
            dias = (d2 - d1).days
            if dias <= 0:
                dias = 1
        except:
            dias = 1

        preco_dia = PRECOS_CARROS.get(carro, 50)
        total = dias * preco_dia

        dados_reserva = {
            'carro_selecionado': carro,
            'local_retirada': request.form.get('local_levantamento'),
            'local_devolucao': request.form.get('local_entrega'),
            'data_retirada': data_retirada,
            'hora_retirada': request.form.get('hora_levantamento'),
            'data_devolucao': data_devolucao,
            'hora_devolucao': request.form.get('hora_entrega'),
            'dias': dias,
            'preco_dia': preco_dia,
            'total': total
        }
        return render_template('efetuar_aluguer.html', **dados_reserva)

    carro = request.args.get('carro')
    return render_template('escolher_datas.html', carro=carro)

# 6ª Página: Efetuar aluguer
@app.route('/submeter-aluguer', methods=['POST'])
def submeter_aluguer():
    dados_reserva = {
        'carro_selecionado': request.form.get('carro'),
        'local_retirada': request.form.get('local_levantamento'),
        'local_devolucao': request.form.get('local_entrega'),
        'data_retirada': request.form.get('data_levantamento'),
        'hora_retirada': request.form.get('hora_levantamento'),
        'data_devolucao': request.form.get('data_entrega'),
        'hora_devolucao': request.form.get('hora_entrega')
    }
    return render_template('efetuar_aluguer.html', **dados_reserva)

# 7ª Página: Pagamento
@app.route('/pagamento', methods=['GET', 'POST'])
def pagamento():
    if request.method == 'POST':
        dados = {
            'carro_selecionado': request.form.get('carro'),
            'local_retirada': request.form.get('local_retirada'),
            'local_devolucao': request.form.get('local_entrega'),
            'data_retirada': request.form.get('data_levantamento'),
            'hora_retirada': request.form.get('hora_levantamento'),
            'data_devolucao': request.form.get('data_entrega'),
            'hora_devolucao': request.form.get('hora_entrega'),
            'dias': request.form.get('dias'),
            'preco_dia': request.form.get('preco_dia'),
            'total': request.form.get('total'),
        }
        return render_template('efetuar_pay.html', **dados)
    return render_template('efetuar_pay.html')

# 8ª Página: Confirmação e guardar reserva na BD
@app.route('/confirmar-pagamento', methods=['POST'])
def confirmar_pagamento():
    dados = {
        'carro_selecionado': request.form.get('carro_selecionado'),
        'local_retirada': request.form.get('local_retirada'),
        'local_devolucao': request.form.get('local_devolucao'),
        'data_retirada': request.form.get('data_retirada'),
        'hora_retirada': request.form.get('hora_retirada'),
        'data_devolucao': request.form.get('data_devolucao'),
        'hora_devolucao': request.form.get('hora_devolucao'),
        'nome_cartao': request.form.get('nome_cartao'),
        'dias': request.form.get('dias'),
        'preco_dia': request.form.get('preco_dia'),
        'total': request.form.get('total'),
    }

    nova_reserva = Reserva(
        utilizador_id=session.get('utilizador_id'),
        carro=dados['carro_selecionado'] or '',
        local_retirada=dados['local_retirada'] or '',
        local_devolucao=dados['local_devolucao'] or '',
        data_retirada=dados['data_retirada'] or '',
        hora_retirada=dados['hora_retirada'] or '',
        data_devolucao=dados['data_devolucao'] or '',
        hora_devolucao=dados['hora_devolucao'] or '',
        nome_cartao=dados['nome_cartao'] or '',
    )
    db.session.add(nova_reserva)
    db.session.commit()

    return render_template('confirmacao.html', **dados)

# Página de Contacto
@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    mensagem_enviada = False
    if request.method == 'POST':
        mensagem_enviada = True
    return render_template('contacto.html', mensagem_enviada=mensagem_enviada)

# Página: As Minhas Reservas
@app.route('/minhas-reservas')
def minhas_reservas():
    utilizador_id = session.get('utilizador_id')
    if not utilizador_id:
        return redirect(url_for('login'))
    reservas = Reserva.query.filter_by(utilizador_id=utilizador_id).order_by(Reserva.data_reserva.desc()).all()
    return render_template('minhas_reservas.html', reservas=reservas)

# Cancelar reserva
@app.route('/cancelar-reserva/<int:id>', methods=['POST'])
def cancelar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    return redirect(url_for('minhas_reservas'))

# Editar reserva
@app.route('/editar-reserva/<int:id>', methods=['GET', 'POST'])
def editar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    if request.method == 'POST':
        reserva.local_retirada = request.form.get('local_retirada')
        reserva.local_devolucao = request.form.get('local_devolucao')
        reserva.data_retirada = request.form.get('data_retirada')
        reserva.hora_retirada = request.form.get('hora_retirada')
        reserva.data_devolucao = request.form.get('data_devolucao')
        reserva.hora_devolucao = request.form.get('hora_devolucao')
        db.session.commit()
        return redirect(url_for('minhas_reservas'))
    return render_template('editar_reserva.html', reserva=reserva)

# --- CRIAR TABELAS E INICIAR ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




