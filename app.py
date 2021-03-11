from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import Automatization as at
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    stock = db.Column(db.String(5), nullable = False)
    real_price = db.Column(db.Float, nullable = False)
    predicted = db.Column(db.Float, nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow().date)


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
    predicted_price = at.predicted_list
    if request.method == 'GET':
        for st, last, pred in zip(stocks, last_price, predicted_price):
            if Stock.query.filter(Stock.date_created).count() < len(stocks):
                new_prices = Stock(stock=st, real_price=last, predicted=pred)
                db.session.add(new_prices)
                db.session.commit()
            else:
                break
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
        try:
            user = request.form['user']
            user_mail = request.form['mail']
            new_mail = Mail(username=user, email=user_mail)
            db.session.add(new_mail)
            db.session.commit()
            return redirect('/contact')
        except:
            db.session.rollback()
            tasks = Mail.query.order_by(Mail.id).all()
            return render_template('contact.html', tasks=tasks)

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
               "These are the predicted variations for today: <br><br>"\
                "<table style='text-align:center; border: 3px solid #aaa'><tr style=' border: 3px solid #aaa'><th style=' border: 3px solid #aaa'>Stock Ticker</th><th style=' border: 3px solid #aaa'>Stock Price</th><th style=' border: 3px solid #aaa'>Predicted Variation</th></tr>"
    for i in range(len(stocks)):
        msg.html += "<tr style=' border: 3px solid #aaa'><td style=' border: 3px solid #aaa'>" + stocks[i].upper()+"</td><td style=' border: 3px solid #aaa'td>"+str(last_price[i])+"$</td><td style=' border: 3px solid #aaa'>"+ str(var_prices[i])+"%</td></tr>"
    msg.html += "</table>" \
                "<br>Best Regards,<br>" \
                "<i>Portfolio MR<tr>"
    mail.send(msg)
    return redirect('/contact')

@app.route('/graph', methods = ['GET'])
def graph():
    data_stock = Stock.query.order_by(Stock.date_created).all()
    data = []
    real_price = []
    pred_price = []
    stock = []

    for i in data_stock:
        data.append(i.date_created)
        real_price.append(i.real_price)
        pred_price.append(i.predicted)
        stock.append(i.stock)
    stock_dic = {'date': data,
                'real_price': real_price,
                'predicted_price': pred_price,
                'stock_ticker': stock}

    stock_df = pd.DataFrame(stock_dic)
    stock_df['date'] = pd.to_datetime(stock_df['date'])

    for ticker in stock:
        ticker_values = stock_df[stock_df['stock_ticker'] == ticker]
        plt.scatter(ticker_values['date'], ticker_values['real_price'], label='real')
        plt.scatter(ticker_values['date'], ticker_values['predicted_price'], label='predicted')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.gcf().autofmt_xdate()
        plt.title(ticker)
        plt.ylabel('Prices')
        plt.xlabel('Days')
        plt.legend()
        plt.savefig(f'./static/{ticker}_plot.png')
        plt.clf()


    return render_template('/graph.html', t=data)

if __name__ == "__main__":
    app.run(debug=True)

