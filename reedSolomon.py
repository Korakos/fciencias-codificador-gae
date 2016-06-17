from campoFinito import GF256int
from polinomio import Polinomio

class RSCoder(object):
    def __init__(self, n, k):
        self.n = n
        self.k = k

        # Generaremos el polinomio generador para nuestro codigo
        # g(x) = (x-a^1)(x-a^2)...(x-a^(2t))
        # con a un primitivo de GF(256), en este caso tomamos a = 3
        g = Polinomio((GF256int(1),))
        for alpha in xrange(1, n - k + 1):
            p = Polinomio((GF256int(1), GF256int(3) ** alpha))
            g = g * p
        self.g = g

        # h(x) = (x-a^(n-k+1))...(x-a^n)
        h = Polinomio((GF256int(1),))
        for alpha in xrange(n - k + 1, n + 1):
            p = Polinomio((GF256int(1), GF256int(3) ** alpha))
            h = h * p
        self.h = h

    def encode(self, message, poly=False):
        n = self.n
        k = self.k

        if len(message) > k:
            raise ValueError("Longitud maxima de mensaje es %d. Se pidio %d" % (k,
                                                                           len(message)))

        m = Polinomio(GF256int(ord(x)) for x in message)

        mprime = m * Polinomio((GF256int(1),) + (GF256int(0),) * (n - k))

        b = mprime % self.g
        c = mprime - b
        
        if poly:
            return c

        return "".join(chr(x) for x in c.coeficientes).rjust(n, "\0")

    def decode(self, r, nostrip=False):
        n = self.n
        k = self.k

        if self.verify(r):
            # los ultimos n-k bytes son de verificacion
            if nostrip:
                return r[:-(n - k)]
            else:
                return r[:-(n - k)].lstrip("\0")

        r = Polinomio(GF256int(ord(x)) for x in r)

        sz = self._sindrome(r)

        sigma, omega = self._berlekamp_massey(sz)

        # encontramos la posicion de los errores
        X, j = self.encErrores(sigma)

        # y encontramos la magnitud del error
        Y = self.encMagErr(omega, X)

        # y armamos el polinomio del error
        Elist = []
        for i in xrange(255):
            if i in j:
                Elist.append(Y[j.index(i)])
            else:
                Elist.append(GF256int(0))
        E = Polinomio(reversed(Elist))

        # obtenemos nuestra palabra original
        c = r - E

        # lo regresamos a una cadena, y eliminamos los bytes de verificacion
        ret = "".join(chr(x) for x in c.coeficientes[:-(n - k)])
        #                                            :-(

        if nostrip:
            return ret.rjust(k, "\0")
        else:
            return ret

    def verify(self, code):
        n = self.n
        k = self.k
        h = self.h
        g = self.g

        c = Polinomio(GF256int(ord(x)) for x in code)

        return c % g == Polinomio(x0=0)

    def _sindrome(self, r):
        # computamos el sindrome de una palabra recibida.
        n = self.n
        k = self.k

        # s[l] es la palabra recibida evaluada en a^t for 1 <= t <= s, con a = 3
        s = [GF256int(0)]  
        for l in xrange(1, n - k + 1):
            s.append(r.evaluate(GF256int(3) ** l))
            
        sz = Polinomio(reversed(s))

        return sz

    def _berlekamp_massey(self, s):
        n = self.n
        k = self.k

        sigma = [Polinomio((GF256int(1),))]
        omega = [Polinomio((GF256int(1),))]
        tao = [Polinomio((GF256int(1),))]
        gamma = [Polinomio((GF256int(0),))]
        D = [0]
        B = [0]

        ONE = Polinomio(z0=GF256int(1))
        ZERO = Polinomio(z0=GF256int(0))
        Z = Polinomio(z1=GF256int(1))

        for l in xrange(0, n - k):
            Delta = ((ONE + s) * sigma[l]).get_coefficient(l + 1)
            Delta = Polinomio(x0=Delta)

            sigma.append(sigma[l] - Delta * Z * tao[l])
            omega.append(omega[l] - Delta * Z * gamma[l])

            if Delta == ZERO or 2 * D[l] > (l + 1):
                D.append(D[l])
                B.append(B[l])
                tao.append(Z * tao[l])
                gamma.append(Z * gamma[l])

            elif Delta != ZERO and 2 * D[l] < (l + 1):
                D.append(l + 1 - D[l])
                B.append(1 - B[l])
                tao.append(sigma[l] // Delta)
                gamma.append(omega[l] // Delta)
            elif 2 * D[l] == (l + 1):
                if B[l] == 0:
                    D.append(D[l])
                    B.append(B[l])
                    tao.append(Z * tao[l])
                    gamma.append(Z * gamma[l])

                else:
                    D.append(l + 1 - D[l])
                    B.append(1 - B[l])
                    tao.append(sigma[l] // Delta)
                    gamma.append(omega[l] // Delta)
            else:
                raise Exception("Esto no deberia de pasar... :)")

        return sigma[-1], omega[-1]

    def encErrores(self, sigma):
        X = []
        j = []
        p = GF256int(3)
        for l in xrange(1, 256):
            if sigma.evaluate(p ** l) == 0:
                X.append(p ** (-l))
                j.append(255 - l)

        return X, j

    def encMagErr(self, omega, X):
        s = (self.n - self.k) // 2

        Y = []

        for l, Xl in enumerate(X):
            Yl = Xl ** s
            Yl *= omega.evaluate(Xl.inverse())
            Yl *= Xl.inverse()
            prod = GF256int(1)
            for ji in xrange(s):
                if ji == l:
                    continue
                if ji < len(X):
                    Xj = X[ji]
                else:
                    Xj = GF256int(0)
                prod = prod * (Xl - Xj)
            Yl = Yl * prod.inverse()

            Y.append(Yl)
        return Y


if __name__ == "__main__":
    import sys

    coder = RSCoder(255, 223)
    if "-d" in sys.argv:
        method = coder.decode
        blocksize = 255
    else:
        method = coder.encode
        blocksize = 223

    while True:
        block = sys.stdin.read(blocksize)
        if not block: break
        code = method(block)
        sys.stdout.write(code)