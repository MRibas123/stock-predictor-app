from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import Automatization as at
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///stock.db"
app.config['SQLALCHEMY_BINDS'] = {'mail_db':'sqlite:///mail.db'}

app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587 # Check the mail client maybe 25 ou 465?
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False #Try them out with Trues
#app.config['MAIL_DEBUG'] =  True
app.config['MAIL_USERNAME'] = 'portofolio.ironhack2021@gmail.com'
app.config['MAIL_PASSWORD'] = 'I+M<3forever'
app.config['MAIL_DEFAULT_SENDER'] = 'portofolio.ironhack2021@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)
db = SQLAlchemy(app)



class Stock(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    last = db.Column(db.String(200), nullable = False)
    tomorrow = db.Column(db.String(200), nullable = False)
    investment = db.Column (db.Integer, nullable = False)
    returns = db.Column (db.Integer, nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)


class Mail(db.Model):
    __bind_key__ = 'mail_db'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)



@app.route('/', methods=['POST','GET'])
def index():
    stocks = at.stocks
    var_prices = at.variation_list
    last_price = at.yesterday_list
    returns = 0
    investment = 0
    if request.method == 'POST':
        stocks_count_list = []
        stocks_count_list.append(int(request.form['price0']))
        stocks_count_list.append(int(request.form['price1']))
        stocks_count_list.append(int(request.form['price2']))
        stocks_count_list.append(int(request.form['price3']))
        stocks_count_list.append(int(request.form['price4']))
        stocks_count_list.append(int(request.form['price5']))
        stocks_count_list.append(int(request.form['price6']))
        stocks_count_list.append(int(request.form['price7']))
        stocks_count_list.append(int(request.form['price8']))
        investment = [a*b for a,b in zip(last_price,stocks_count_list)]
        returns = [a*b/100 for a,b in zip(investment,var_prices)]
        return render_template('index.html',tasks=stocks, var=var_prices, rtr=round(sum(returns),2), inv=round(sum(investment),2),lp = zip(stocks,last_price,var_prices))
    else:
        return render_template('index.html',tasks=stocks, var=var_prices,lp = zip(stocks,last_price,var_prices), rtr=returns, inv=investment)


@app.route('/contact', methods=['POST','GET'])
def contact():
    if request.method == 'POST':
        user = request.form['user']
        user_mail = request.form['mail']
        new_mail = Mail(username=user, email=user_mail)
        db.session.add(new_mail)
        db.session.commit()
        return redirect('/contact')
    else:
        tasks = Mail.query.order_by(Mail.id).all()
        return render_template('contact.html', tasks=tasks)


@app.route('/contact/delete/<int:id>')
def delete(id):
    mail_to_delete = Mail.query.get_or_404(id)
    try:
        db.session.delete(mail_to_delete)
        db.session.commit()
        return redirect('/contact')
    except:
        return 'There was a problem deleting that task'

@app.route('/contact/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Mail.query.get_or_404(id)
    if request.method == 'POST':
        task.email = request.form['mail']
        task.username = request.form['user']
        try:
            db.session.commit()
            return redirect('/contact')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task = task)

@app.route('/send_mail', methods = ['POST', 'GET'])
def send_mail():
    tasks = Mail.query.order_by(Mail.id).all()
    mails = []
    stocks = at.stocks
    var_prices = at.variation_list
    last_price = at.yesterday_list
    for task in tasks:
        mails.append(str(task.email))
    msg = Message('Stocks for today.', recipients=mails)
    msg.html = "Dear Subscriber,<br><br>" \
               "These are the predicted variations for today: <br><br>"
    for i in range(len(stocks)):
        msg.html += stocks[i].upper() + " closed yesterday at a price of " + str(last_price[i]) + "$ and it's expected to fluctuate "+ str(var_prices[i])+"%; <br>"
    msg.html += "<br>Best Regards,<br>" \
                "<i>Portfolio MR<i>"
    mail.send(msg)
    return redirect('/contact')

if __name__ == "__main__":
    app.run(debug=True)

