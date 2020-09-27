import all as gp


def get_elem_with_prefix(l, e):
    for el in l:
        flag = True
        for i in range(0, len(e)):
            if el[i] != e[i]:
                flag = False
                break
        if flag == True:
            return el
    return None


currencies = []

for item in gp.bi:
    name0 = item[0]
    name1 = item[1]
    if name0 not in currencies:
        currencies.append(name0)
    if name1 not in currencies:
        currencies.append(name1)

# for all v0 in cur , v1 in cur, b in bank, (v0, v1, b, x) is defined in bank_info


# for v0 in currencies:
#     for v1 in currencies:
#         if v0 == v1:
#             continue
#         for b in gp.bank_names:
#             if get_elem_with_prefix(gp.bank_info, [v0, v1, b]) is None:
#                 y0 = get_elem_with_prefix(gp.bank_info, [v0, '人民币现汇', b])[3]
#                 y1 = get_elem_with_prefix(gp.bank_info, ['人民币现钞', v1, b])[3]
#                 gp.bank_info.append([v0, v1, b, y0 * y1])
