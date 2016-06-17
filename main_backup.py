
import webapp2
import jinja2
import os
import cyclicEncoder
import cgi
import cyclicDecoder

class MainHandler(webapp2.RequestHandler):
    def get(self):
        jinja_environment = jinja2.Environment(autoescape=True,
                                               loader=jinja2.FileSystemLoader(
                                                   os.path.join(os.path.dirname(__file__), 'templates')))

        template = jinja_environment.get_template('main.html')
        self.response.write(template.render())

    def post(self):
        archivo = self.request.get("archivo")
        polinomio = 11 #int(cgi.escape(self.request.get("polinomio")))
        algoritmo = cgi.escape(self.request.get("algoritmo"))
        accion = cgi.escape(self.request.get("accion"))
        nombre = cgi.escape(self.request.get("nombre"))



        array = bytearray(archivo)
        encoder = cyclicEncoder.CyclicEncoder(array, polinomio)
        encodedFileArray = encoder.encodeFile()
        encodedFile = "".join(map(chr, encodedFileArray))

        array = bytearray(encodedFile)
        decoder = cyclicDecoder.CyclicDecoder(array, polinomio)
        decodedFileArray = decoder.decodeFile()

        decodedFile = "".join(map(chr, decodedFileArray))

        self.response.write(encodedFile + " <br><br> "+decodedFile)

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)