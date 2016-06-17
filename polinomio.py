from StringIO import StringIO

class Polinomio(object):

    def __init__(self, coeficientes=(), **sparse):

        if coeficientes and sparse:
            raise TypeError("Specify coeficientes list /or/ keyword terms, not"
                            " both")
        if coeficientes:
            # Polynomial((1, 2, 3, ...))
            c = list(coeficientes)
            # Expunge any leading 0 coeficientes
            while c and c[0] == 0:
                c.pop(0)
            if not c:
                c.append(0)

            self.coeficientes = tuple(c)
        elif sparse:
            # Polynomial(x32=...)
            powers = sparse.keys()
            powers.sort(reverse=1)
            # Not catching possible exceptions from the following line, let
            # them bubble up.
            highest = int(powers[0][1:])
            coeficientes = [0] * (highest + 1)

            for power, coeff in sparse.iteritems():
                power = int(power[1:])
                coeficientes[highest - power] = coeff

            self.coeficientes = tuple(coeficientes)
        else:
            # Polynomial()
            self.coeficientes = (0,)

    def __len__(self):
        return len(self.coeficientes)

    def grado(self):
        return len(self.coeficientes) - 1

    def __add__(self, otro):
        dif = len(self) - len(otro)
        if dif > 0:
            t1 = self.coeficientes
            t2 = (0,) * dif + otro.coeficientes
        else :
            t1 = (0,) * (-dif) + self.coeficientes
            t2 = otro.coeficientes

        return self.__class__(x+y for x,y in zip(t1,t2))

    def __neg__(self):
        return self.__class__(-x for x in self.coeficientes)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        coeficientes = [0] * (len(self) + len(other))
        for i1, c1 in enumerate(reversed(self.coeficientes)):
            if c1 == 0:
                continue
            for i2, c2 in enumerate(reversed(other.coeficientes)):
                coeficientes[i1+i2] += c1*c2

        return self.__class__(reversed(coeficientes))

    def __floordiv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]

    def __divmod__(dividendo, divisor):
        class_ = dividendo.__class__

        dividendoGrado = dividendo.grado()
        dividendoCoeficiente = dividendo.coeficientes[0]

        divisorGrado = divisor.grado()
        divisorCoeficiente = divisor.coeficientes[0]

        cocienteGrado = dividendoGrado - divisorGrado
        if cocienteGrado < 0:
            return class_((0,)), dividendo

        cocienteCoeficiente = dividendoCoeficiente / divisorCoeficiente
        cociente = class_((cocienteCoeficiente,) + (0,) * cocienteGrado)

        residuo = dividendo - cociente * divisor

        if residuo.coeficientes == (0,):
            return cociente, residuo

        cociente2, residuo = divmod(residuo, divisor)

        return cociente + cociente2, residuo

    def __eq__(self, other):
        return self.coeficientes == other.coeficientes

    def __ne__(self, other):
        return self.coeficientes != other.coeficientes

    def __hash__(self):
        return hash(self.coeficientes)

    def __repr__(self):
        n = self.__class__.__name__
        return "%s(%r)" % (n, self.coeficientes)

    def __str__(self):
        buf = StringIO()
        l = len(self) - 1
        for i, c in enumerate(self.coeficientes):
            if not c and i > 0:
                continue
            grado = l - i
            if c == 1 and grado != 0:
                c = ""
            if grado > 1:
                buf.write("%sx^%s" % (c, grado))
            elif grado == 1:
                buf.write("%sx" % c)
            else:
                buf.write("%s" % c)
            buf.write(" + ")
        return buf.getvalue()[:-3]

    def evaluate(self, x):
        c = 0
        p = 1

        for term in reversed(self.coeficientes):
            c = c + term * p

            p = p * x

        return c

    def get_coefficient(self, degree):
        if degree > self.grado():
            return 0
        else:
            return self.coeficientes[-(degree + 1)]