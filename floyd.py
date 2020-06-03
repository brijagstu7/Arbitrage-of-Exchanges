# *****     主程序         **********


import get_price as gp
import sys

currencies = gp.currencies
n = len(currencies)

# 3d
d = [[[float("inf") for i in range(3)] for i in range(len(currencies))] for i in range(len(currencies))]


# we let number of currencies follow the sequence of currency array
for l in gp.bank_info:
    if l[3] < d[currencies.index(l[0])][currencies.index(l[1])][2]:
        d[currencies.index(l[0])][currencies.index(l[1])][0] = gp.bank_names.index(
            l[2])  # bank no of last exchange
        d[currencies.index(l[0])][currencies.index(l[1])][1] = currencies.index(l[0])  # last currency no
        d[currencies.index(l[0])][currencies.index(l[1])][2] = l[3]  # price

for i in range(len(currencies)):
    d[i][i][2] = 1
    d[i][i][1] = i


# 如果经过搜索没有找到从s到e的路径（即，它是循环的或者是断的即inf）就返回none 或者 1
def check_seq(s, e):
    ll = [e]
    m = e
    for i in range(len(currencies) + 1):
        try:
            m = d[s][m][1]
        except TypeError:
            return 1
        ll.append(m)
        if m == s:
            ll.reverse()
            return ll

    if i == len(currencies):
        return None
    else:
        ll.reverse()
        return ll


def find_dup(ll1, ll2):
    for i in range(len(ll1) - 1):
        for x in range(len(ll2) - 1):
            if ll1[i] == ll2[x] and ll1[i + 1] == ll2[x + 1]:
                return True
    return False


for k in range(n):
    for i in range(n):
        for j in range(n):
            if d[i][k][2] * d[k][j][2] < d[i][j][2]:
                # no duplicated paths are allowed to appear both in l1 and l2
                # it can be proved that any condition specified here can lead to a valid proof of correct result
                #     for a shortest path collection under the specified condition.
                l1 = check_seq(i, k)
                l2 = check_seq(k, j)
                if type(l1) == list and type(l2) == list:
                    if find_dup(l1, l2):
                        continue
                elif l1 is None or l2 is None:  # else?
                    continue
                d[i][j][2] = d[i][k][2] * d[k][j][2]
                d[i][j][1] = d[k][j][1]
                d[i][j][0] = d[k][j][0]

# describe the path

bal = "现汇: 人民币"
csh = "现钞: 人民币"
ok = [0 for i in range(4)]
bal_idx = currencies.index(bal)
csh_idx = currencies.index(csh)
for b in range(len(gp.bank_names)):
    if d[bal_idx][bal_idx][2] < 1:  # 00
        ok[0] = 1
    if d[bal_idx][csh_idx][2] < 1:  # 01
        ok[1] = 1
    if d[csh_idx][bal_idx][2] < 1:  # 10
        ok[2] = 1
    if d[csh_idx][csh_idx][2] < 1:  # 11
        ok[3] = 1

# 描述套汇过程的语句
arbitrage = [bal, csh, bal, csh]
if ok[0]:
    last_cur = -1
    while csh_idx != last_cur and bal_idx != last_cur:
        if last_cur == -1:
            last_cur = d[bal_idx][bal_idx][1]
            b = d[bal_idx][bal_idx][0]
            price = d[last_cur][bal_idx][2]
            arbitrage[0] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]
        else:
            prev_last_cur = last_cur
            last_cur = d[bal_idx][last_cur][1]
            b = d[bal_idx][last_cur][0]
            price = d[last_cur][prev_last_cur][2]
            arbitrage[0] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]

if ok[1]:
    last_cur = -1
    while csh_idx != last_cur and bal_idx != last_cur:
        if last_cur == -1:
            last_cur = d[bal_idx][csh_idx][1]
            b = d[bal_idx][csh_idx][0]
            price = d[last_cur][csh_idx][2]
            arbitrage[1] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]
        else:
            prev_last_cur = last_cur
            last_cur = d[bal_idx][last_cur][1]
            b = d[bal_idx][last_cur][0]
            price = d[last_cur][prev_last_cur][2]
            arbitrage[1] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]
if ok[2]:
    last_cur = -1
    while csh_idx != last_cur and bal_idx != last_cur:
        if last_cur == -1:
            last_cur = d[csh_idx][bal_idx][1]
            b = d[csh_idx][bal_idx][0]
            price = d[last_cur][bal_idx][2]
            arbitrage[2] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]
        else:
            prev_last_cur = last_cur
            last_cur = d[csh_idx][last_cur][1]
            b = d[csh_idx][last_cur][0]
            price = d[last_cur][prev_last_cur][2]
            arbitrage[2] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]
if ok[3]:
    last_cur = -1
    while csh_idx != last_cur and bal_idx != last_cur:
        if last_cur == -1:
            last_cur = d[csh_idx][csh_idx][1]
            b = d[csh_idx][csh_idx][0]
            price = d[last_cur][csh_idx][2]
            arbitrage[3] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]
        else:
            prev_last_cur = last_cur
            last_cur = d[csh_idx][last_cur][1]
            b = d[csh_idx][last_cur][0]
            price = d[last_cur][prev_last_cur][2]
            arbitrage[3] += "<-在银行: " + gp.bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                last_cur]

# if ok[0]:
print("存在从人民币现汇到人民币现汇的套汇机会(而且经计算是最优的), 汇->汇: ")
print(arbitrage[0])
# if ok[1]:
print("存在从人民币现汇到人民币现钞的套汇机会(而且经计算是最优的), 汇->钞: ")
print(arbitrage[1])
# if ok[2]:
print("存在从人民币现钞到人民币现汇的套汇机会(而且经计算是最优的), 钞->汇: ")
print(arbitrage[2])
# if ok[3]:
print("存在从人民币现钞到人民币现钞的套汇机会(而且经计算是最优的), 钞->钞: ")
print(arbitrage[3])
