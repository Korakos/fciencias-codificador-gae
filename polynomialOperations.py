def divideBytes(dividend, divisor):
    quotient = 0
    dividendDegree = polynomialDegree(dividend)
    divisorDegree = polynomialDegree(divisor)
    for i in range(7 - divisorDegree + 1):
        placement = 7 - divisorDegree - i
        temp = (dividend >> (7 - i)) & 1
        if (dividend >> (7 - i)) & 1:
            substractor = (divisor << placement)
            dividend = dividend ^ substractor

            quotient = quotient | (1 << (placement))

    remainder = dividend
    return quotient, remainder


def polynomialDegree(byte):
    for i in range(8):
        if (byte >> (8 - i)) & 1:
            return 8 - i
    return 0