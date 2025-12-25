def grn_text(s):
    grn = int(s)
    kop = round((s - grn)*100)
    tys = int(grn/1000)
    g = grn - tys*1000

    res = ''
    if tys > 0:
        res += txt(tys) + ' ' + {0: 'тисячь', 1: 'тисяча', 2: 'тисячи'}.get(sklon(tys), 'error') + ' '

    if tys == 0 and g == 0:
        res += 'ноль гривень'

    if g == 0 and tys > 0:
        res += ' гривень'

    if g > 0:
        res += txt(g) + ' ' + {0: 'гривень', 1: 'гривна', 2: 'гривні'}.get(sklon(g), 'error')

    res += f' {kop:02} '

    res += {0: 'копійок', 1: 'копійка', 2: 'копійки'}.get(sklon(kop), 'error')

    res = res.replace('  ', ' ').capitalize()
    return res

def txt(v):
    s = int(v/100)
    d = int((v - s*100)/10)
    e = v%10

    ss = {0: '', 1: 'сто', 2: 'двісти', 3: 'триста', 4: 'чотиреста', 5: 'п\'ятьсот', 6: 'шістьсот', 7: 'сімсот', 8: 'вісімьсот', 9: 'девятьсот'}.get(s, 'error')
    ds = {0: '', 1: '', 2: 'двадцять', 3: 'тридцять', 4: 'сорок', 5: 'п\'ятдесят', 6: 'шістьдесят', 7: 'сімдесят', 8: 'вісімдесят', 9: 'дев\'яносто'}.get(d, 'error')
    es = {0: '', 1: 'одна', 2: 'дві', 3: 'три', 4: 'чотири', 5: 'п\'ять', 6: 'шість', 7: 'сім', 8: 'вісім', 9: 'дев\'ять'}.get(e, 'error')

    if d==1:
        es = {0: 'десять', 1: 'одинадцять', 2: 'дванадцять', 3: 'тринадцять', 4: 'чотирнадцять', 5: 'п\'ятнадцять', 6: 'шістьнадцять', 7: 'сімнадцять', 8: 'вісімнадцять', 9: 'дев\'ятнадцять'}.get(e, 'error')

    x = f'{ss} {ds} {es}'.strip()
    return x

def sklon(v):
    if v>=11 and v<=19:
        return 0

    ed = v % 10
 
    if ed == 1:
        return 1

    if ed in [2, 3, 4]:
        return 2

    return 0

if __name__ == '__main__':
    import random

    for e in range(10):
        v = round(1000000*random.random(), 2)
        print(v, '\t', grn_text(v))
