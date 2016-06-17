#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Desarrollado Por: Andres Molina Torres Arpi
import webapp2
import jinja2
import os
import cgi
import cyclicEncoder
import cyclicDecoder
import reedSolomon
import math

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

        if algoritmo == "ciclico":
            array = bytearray(archivo)
            if accion == "codificar":
                encoder = cyclicEncoder.CyclicEncoder(array, polinomio)
                encodedFileArray = encoder.encodeFile()
                encodedFile = "".join(map(chr, encodedFileArray))
                self.response.write(encodedFile)
            elif accion == "decodificar" :
                decoder = cyclicDecoder.CyclicDecoder(array, polinomio)
                decodedFileArray = decoder.decodeFile()
                decodedFile = "".join(map(chr, decodedFileArray))
                self.response.write(decodedFile)
            else :
                encoder = cyclicEncoder.CyclicEncoder(array, polinomio)
                encodedFileArray = encoder.encodeFile()
                encodedFile = "".join(map(chr, encodedFileArray))
                decoder = cyclicDecoder.CyclicDecoder(encodedFileArray, polinomio)
                decodedFileArray = decoder.decodeFile()
                decodedFile = "".join(map(chr, decodedFileArray))

                self.response.write("Encoded: "+encodedFile + " <br><br><br>Decoded: "+decodedFile)
        else :
            output = ""
            coder = reedSolomon.RSCoder(255, 223)
            act = False

            if accion == "codificar":
                act = True
                accion = coder.encode
                blockSize = 223
            elif accion == "decodificar" :
                accion = coder.decode
                blockSize = 255
                act = True
            else :
                output += "Encoded: "
                accion = coder.encode
                blockSize = 223
                for i in range(0, int(math.ceil(float(len(archivo)) / float(blockSize)))):
                    if i * blockSize > len(archivo):
                        segmento = archivo[i * blockSize:]
                    else:
                        segmento = archivo[i * blockSize: (i + 1) * blockSize]

                    output += accion(segmento)

                newOutput = ""
                accion = coder.decode
                blockSize = 255

                for i in range(0, int(math.ceil(float(len(output)) / float(blockSize)))):
                    if i * blockSize > len(output):
                        segmento = output[i * blockSize:]
                    else:
                        segmento = output[i * blockSize: (i + 1) * blockSize]

                    newOutput += accion(segmento)

                output += " <br><br><br> Decoded: " + newOutput
                self.response.write(output)

            if act:
                for i in range(0, int(math.ceil(float(len(archivo)) / float(blockSize)))):
                    if i*blockSize > len(archivo):
                        segmento = archivo[i*blockSize:]
                    else :
                        segmento = archivo[i*blockSize: (i+1)*blockSize]

                    output += accion(segmento)
                    self.response.write(output)




app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
