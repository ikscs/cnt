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

def change_currency(s, curr_in, curr_out):
    vocabl = {
        'UAH': {
            'USD': {'гривень': 'долларів', 'гривна': 'доллар', 'гривні': 'доллари', 'копійок': 'центів', 'копійка': 'цент', 'копійки': 'центи',},
            'EUR': {'гривень': 'євро', 'гривна': 'євро', 'гривні': 'євро', 'копійок': 'центів', 'копійка': 'цент', 'копійки': 'центи',},
        },
        'USD': {
            'EUR': {'dollars': 'euro', 'dollar': 'euro',},
        },
    }

    if (curr_in not in vocabl) or (curr_out not in vocabl[curr_in]):
        return 'error'

    for k, v in vocabl[curr_in][curr_out].items():
        s = s.replace(k, v)
    return s

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

def int_to_english(n: int) -> str:
    if n == 0:
        return "zero"

    if n < 0:
        return "minus " + int_to_english(-n)

    ones = (
        "", "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine"
    )

    teens = (
        "ten", "eleven", "twelve", "thirteen", "fourteen",
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"
    )

    tens = (
        "", "", "twenty", "thirty", "forty",
        "fifty", "sixty", "seventy", "eighty", "ninety"
    )

    thousands = (
        "", "thousand", "million", "billion", "trillion"
    )

    def chunk_to_words(num: int) -> str:
        words = []

        if num >= 100:
            words.append(ones[int(num // 100)])
            words.append("hundred")
            num = int(num % 100)

        if 10 <= num < 20:
            words.append(teens[int(num - 10)])
        else:
            if num >= 20:
                words.append(tens[int(num // 10)])
                num = int(num % 10)
            if num > 0:
                words.append(ones[int(num)])

        return " ".join(words)

    words = []
    chunk_index = 0

    while n > 0:
        chunk = int(n % 1000)
        if chunk:
            part = chunk_to_words(chunk)
            if thousands[chunk_index]:
                part += " " + thousands[chunk_index]
            words.append(part)
        n //= 1000
        chunk_index += 1

    return " ".join(reversed(words))

def usd_text(s):
    usd = int(s)
    cent = round((s - usd)*100)

    res = ''

    if usd == 0:
        res += 'zero dollars'
    elif usd == 1:
        res += 'one dollar'
    else:
        res += int_to_english(usd)
        res += ' dollars'

    res += f' {cent:02} '
    res += ' cents'

    res = res.replace('  ', ' ').capitalize()
    return res

if __name__ == '__main__':
    import random

    for e in range(10):
        v = round(1000000*random.random(), 2)
        print(v, '\t', grn_text(v))

    print()

    for e in range(10):
        v = round(100000*random.random(), 2)
        print(v, '\t', usd_text(v))
