from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from os import chdir,system
from pyPdf import PdfFileReader
import cgi,time

# You have to edit the HTML code if you change one of them!
selColorOps=['COLOR','MONO']
QualityOps=['PLAIN_DRAFT','PLAIN_NORMAL','PLAIN_HIGH','PMPHOTO_DRAFT','PMPHOTO_NORMAL','PMPHOTO_HIGH']
selPagesOps=['all','even','odd']

class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        filename = form['file'].filename
        data = form['file'].file.read()
        
        #SPECIFIC PRINTING CODE
        if form.getvalue('selcolor') in selColorOps:
           opColor= form.getvalue('selcolor')
           
        else:
           opColor = "MONO"
          
        if form.getvalue('Quality') in QualityOps:
           opQuality = form.getvalue('Quality')
        else:
           opQuality = "PLAIN_DRAFT"

        if form.getvalue('selpages') in selPagesOps:
           opPages = form.getvalue('selpages')
        else:
           opPages = "all"

        t=time.time()
        localfilename=time.strftime("%b%d%Y%H%M%S", time.gmtime(t))
	localfilepath="/tmp/"+localfilename
        actfile=open(localfilepath, "wb")
        actfile.write(data)
        actfile.close();
	try:
	   doc = PdfFileReader(file(localfilepath, "rb"))
        except:
           self.respond("ERROR: No es un PDF")
           return      
        else:
           self.respond("Archivo subido: %s, imprimiendo."%filename)
           escaner="$(lpstat -a | sed -n 1p | cut -d ' ' -f 1)"
           #print "lp -d %s -o \"Quality=%s Ink/Ink=%s\" %s"%(escaner,opQuality,opColor,localfilepath)
           system("lp -d %s -o \"media=A4 Quality=%s page-set=%s Ink=%s\" %s"%(escaner,opQuality,opPages,opColor,localfilepath))
           #print "rm %s"%localfilepath 
           system("rm %s"%localfilepath)


    def do_GET(self):
        response = """
        <html><body>
        <form enctype="multipart/form-data" method="post">
        <p>Archivo: <input type="file" name="file"></p>
        <p>Imprimir en: </p>
	    <p>
        <input type="radio" name="selcolor" value="COLOR"> Color<br>
        <input type="radio" name="selcolor" value="MONO" checked> Blanco y negro<br>
        </p>
        <p>
        Seleccione la calidad de la impresion:
        <select name="Quality">
        <option value="PLAIN_DRAFT" selected>Borrador (se ve bien)</option>
        <option value="PLAIN_NORMAL">Normal</option>
        <option value="PLAIN_HIGH">Alta</option>
        <option value="PMPHOTO_DRAFT">Borrador foto</option>
        <option value="PMPHOTO_NORMAL">Normal foto</option>
        <option value="PMPHOTO_HIGH">Alta foto</option>
        </select>
        </p>
        <p>
        Seleccione las paginas a imprimir:
        <select name="selpages">
        <option value="all" selected>Todas</option>
        <option value="odd">Impares</option>
        <option value="even">Pares</option>
        </select>
        </p>
        <p><input type="submit" value="Subir"></p>
        </form>
        </body></html>
        """        

        self.respond(response)

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)  


def main():

    try:

        server = HTTPServer(('', 1478), StoreHandler)

        #print 'started httpserver...'
        chdir("/tmp")

        server.serve_forever()

    except KeyboardInterrupt:
        print 'shutting down server'
        server.socket.close()


if __name__ == '__main__':

    main()
