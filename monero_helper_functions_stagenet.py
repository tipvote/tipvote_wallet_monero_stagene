
def get_amount(amount):
    """
    decode cryptonote amount format to user friendly format.

    """

    cryptonote_display_decimal_point = 12
    str_amount = str(amount)
    fraction_size = 0

    if '.' in str_amount:
        point_index = str_amount.index('.')
        fraction_size = len(str_amount) - point_index - 1
        while fraction_size < cryptonote_display_decimal_point\
                and '0' == str_amount[-1]:
            str_amount = str_amount[:-1]
            fraction_size = fraction_size - 1
        if cryptonote_display_decimal_point < fraction_size:
            return False
        str_amount = str_amount[:point_index] + str_amount[point_index + 1:]
    if not str_amount:
        return False
    if fraction_size < cryptonote_display_decimal_point:
        str_amount = str_amount + '0' *\
                     (cryptonote_display_decimal_point - fraction_size)

    return str_amount


def get_money(amount):
    """
    decode cryptonote amount format to user friendly format.

    """

    cryptonote_display_decimal_point = 12
    s = amount

    if len(s) < cryptonote_display_decimal_point + 1:
        # add some trailing zeros, if needed, to have constant width
        s = '0' * (cryptonote_display_decimal_point + 1 - len(s)) + s
    idx = len(s) - cryptonote_display_decimal_point
    s = s[0:idx] + "." + s[idx:]

    return s
