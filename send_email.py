from flask import Flask, request
from flask_mail import Mail, Message

app =Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'trytestapp007@gmail.com'
app.config['MAIL_PASSWORD'] = 'trytestapp@123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
recepients_list = ['ayuxm10@gmail.com']

def send_email(subject, msg_body, recepients_list=recepients_list, sender=app.config['MAIL_USERNAME']):
   msg = Message(subject, sender = sender, recipients = recepients_list)
   msg.body = msg_body
   mail.send(msg)
   return "Sent"

@app.route("/")
def index():
   msg_body = "New job updates available. Please click here {}common/".format(request.base_url)
   send_email('TEST EMAIL', msg_body)
   return "EMAIL SENT"

if __name__ == '__main__':
   app.run(debug = True)