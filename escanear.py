#! /usr/bin/python
# -*- coding:utf-8 -*-

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from os import chdir,system
from PIL import Image
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from twilio.rest import Client
import img2pdf 
import cgi,time
import smtplib
import telebot

class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})   
        extension=self.extensionArchivo(form.getvalue("tipo"))
        nombreArchivo=time.strftime("%b%d%Y%H%M%S", time.gmtime(time.time()))
        pathImagen="/home/pi/iot/appWeb/escaneo/"+nombreArchivo+"."+extension
        pathPdf="/home/pi/iot/appWeb/escaneo/"+nombreArchivo+".pdf"  
        miEscaner="$(scanimage --list-devices | sed -n 1p | cut -c9-29)"
        system("scanimage -d %s --mode %s --resolution %s --format %s > %s"%(miEscaner,form.getvalue('color'), form.getvalue('calidad'),extension,pathImagen))
        if form.getvalue("tipo") == "pdf":
            self.crearPdf(pathImagen,pathPdf)
            path = pathPdf
        else:
            path = pathImagen
        archivo=open(path,"rb")
        data=archivo.read()
        archivo.close()
        self.definirHeaderPost(data,form.getvalue("tipo"),nombreArchivo)
        self.wfile.write(data)
        if form.getvalue("correo")!="":
            self.enviarCorreoEscaneo(path,form.getvalue("correo"),form.getvalue("tipo"),nombreArchivo)
        if form.getvalue("telefono")!="":
            self.enviaraWhatApp(form.getvalue("telefono"),form.getvalue("correo"))
        if form.getvalue("telefonoTelegram")!="":
            self.enviaraTelegram(path,form.getvalue("telefonoTelegram"),form.getvalue("tipo"))
                

    def enviaraWhatApp(self, numero, correo):      
        account_sid = 'SID TOKEN TWILIO'
        auth_token = 'TOKER TWILIO'
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body='se le envío un archivo a su correo :) '+ correo,
            from_='whatsapp:+14155238886',
            to='whatsapp:+593'+numero
        )
        print(message.sid)
    def enviaraTelegram(self,pathArchivo,idTelegram,extension):
        TOKEN = 'TOKEN BOT TELEGRAM'
        tb = telebot.TeleBot(TOKEN)
        doc = open(pathArchivo, 'rb') 
        if extension =="pdf":
            tb.send_document(idTelegram, doc)
        else:
            tb.send_photo(idTelegram, doc)
        doc.close()
            
    def crearPdf(self,pathImagen,pathPdf):
        imagen = Image.open(pathImagen) 
        pdf_bytes = img2pdf.convert(imagen.filename) 
        dataPdf = open(pathPdf, "wb")  
        dataPdf.write(pdf_bytes) 
        imagen.close() 
        dataPdf.close()
    def definirHeaderPost(self, data,extension,nombre):
        self.send_response(200)
        if extension != "pdf":
            self.send_header('Content-type', 'image/'+extension)
        else:
            self.send_header('Content-type', 'application/'+extension)
        self.send_header("Content-Disposition","attachment;filename="+nombre+"."+extension);
        self.send_header("Content-length", len(data))
        self.end_headers()
    def enviarCorreoEscaneo(self,path,toCorreo,tipo,nombreArchivo):
        msg = MIMEMultipart()
        password = "CLAVE CORREO"
        msg['From'] = "CORREO"
        msg['To'] = toCorreo
        msg['Subject'] = "Archivo de Escaner"
        msg.attach(MIMEText("Envío automático. Por favor no contestar este correo.", 'plain'))
        archivo_adjunto = open(path, 'rb')
        adjunto_MIME = MIMEBase('application', 'octet-stream')
        adjunto_MIME.set_payload((archivo_adjunto).read())
        encoders.encode_base64(adjunto_MIME)
        adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s.%s" % (nombreArchivo,tipo))
        msg.attach(adjunto_MIME)         
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print ("el mensaje fue enviado a %s:" % (msg['To']))        
    def do_GET(self):
        pagina = """
        <html><body>
        <form enctype="multipart/form-data" method="post">
        <div align="center">
        	<div align="center">RASPBERRY - EPSON L210 - PYTHON - SMTP GOOGLE</div>
	<div style="width:400px">
	<div align="left" >
		<fieldset>
		<legend>Seleccione el tipo de escaneado</legend>
        	<input type="radio" name="color" value="Color" checked> Color<br>
       		<input type="radio" name="color" value="Gray" > Blanco y negro<br>
		</fieldset>
        </div>
	<div align="left">
      	<fieldset>
		<legend>Seleccione la calidad</legend>
       			<select name="calidad">
        			<option value="100">100ppp</option>
        			<option value="300" selected>300ppp</option>
        			<option value="600">600ppp</option>
        			<option value="1200">1200ppp</option>
	   		</select>
        </fieldset>
	</div>
	<div align="left" >
      	<fieldset>
		<legend>Tipo de archivo</legend>
       			<select name="tipo">
                                <option value="pdf" selected>pdf</option>
        			<option value="tiff">tiff</option>
        			<option value="png">png</option>
				<option value="jpeg">jpeg</option>
       			</select>
        </fieldset>
	</div>
	<div align="left" >
      	<fieldset>
		<legend>Correo</legend>
		<input name="correo" style="width:260px"/>
        </fieldset>
        <fieldset>
		<legend>Celular notificación a Whatsapp</legend>
		<input name="telefono" style="width:260px"/>
        </fieldset>
          <fieldset>
		<legend>ID de Telegram @jhefestoBot comando /yo</legend>
		<input name="telefonoTelegram" style="width:260px"/>
        </fieldset>
	</div>
        <div>
		<input type="submit" value="Escanear">
	</div>
	</div>
	</div>
        </form>
        </body></html>
        """        
        self.definirHeaderHtml(pagina)
        self.wfile.write(pagina)
    def definirHeaderHtml(self,pagina):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(pagina))
        self.end_headers()
    def extensionArchivo(self, tipo):
        aTipo = ["jpeg","tiff","png"]
        if (tipo in aTipo):
            return tipo
        else:
            return "jpeg"
def main():
    try:
        server = HTTPServer(('', 1986), StoreHandler)
        print("servidor iniciado...")
        chdir("/home/pi/iot/appWeb")
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Ctrl C - Apagando Servidor'
        server.socket.close()
if __name__ == '__main__':
    main()
