from selenium import webdriver as wb
from selenium.webdriver.chrome.options import Options
import re
import langconv as lang
from multiprocessing import Pool as pool
import time
import datetime

# 说明：此项目在2019年7月启动
# 数字会有0.1%内的误差
# 需要加入新的银行，并保证币种名字统一
# 搜索 *** 以发现暂时没有着手解决的问题

chrome_options = Options()
# 设置chrome浏览器无界面模式
# chrome_options.add_argument('--headless')

save_info_at = "/Users/yangsijie/Documents/MuMu共享文件夹/"

# 以下被注释的是不能正常爬取的银行门户（但是经过一番探索也有可能可以爬取），注意bank_names,bank_sites注释的行码需要同步
bank_names = ['bank of china',
              'bank of communications',
              'china merchants bank',
              # 'industrial and commercial bank of china',
              # 'china everbright bank',
              # 'china guangfa bank',
              'agricultural bank of china']
bank_sites = ['http://www.boc.cn/sourcedb/whpj/',
              'http://www.bankcomm.com/BankCommSite/simple/cn/whpj/queryExchangeResult.do?type=simple',
              'http://fx.cmbchina.com/hq/',
              # 'http://www.icbc.com.cn/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx',
              # 'http://www.cebbank.com/site/ygzx/whpj/index.html?page=1',
              # 'http://www.cgbchina.com.cn/Info/12154717',
              'http://ewealth.abchina.com/ForeignExchange/ListPrice/']

start = time.time()
document = wb.Chrome('/usr/local/Cellar/python@3.8/3.8.5/bin/chromedriver', chrome_options=chrome_options)

# 超时设置
document.set_page_load_timeout(5)
document.set_script_timeout(5)


# 这两种设置都进行才有效。如果超时，会报错（若不设置，则超时多久都不报错）


def itr_banks(i):
    try:
        document.get(bank_sites[i])
    except:
        print("Committed an error when visiting " + bank_names[i])
        return []

    bi = []

    # 此处用字符串比较会带来性能退步（和序号比较相比），但是当启用/禁用某个银行的爬取（通过注释bank_names和bank_sites）时
    # ，能够减轻维护的负担
    if bank_names[i] == "bank of china":
        # 货币名称 现汇买入价 现钞买入价 现汇卖出价  现钞卖出价 中行折算价
        # 0         1       2           3       4           5
        price_list = document.find_elements_by_class_name("odd")
        # ****  此处存在一个小问题：只有奇数项被选中，偶数项的牌价没有在 price_list 中

        for item in price_list:
            strs = item.text.split()
            if strs[0] == '货币名称':
                continue
            # (V1, V2, B, P)
            # v1 : v2 = price : 1
            try:
                bi.append(["现汇: 人民币", "现汇: " + strs[0], bank_names[i], float(strs[3]) / 100])  # 现汇卖出价
                bi.append(["现汇: " + strs[0], "现汇: 人民币", bank_names[i], 1 / (float(strs[1]) / 100)])  # 现汇买入价
            except BaseException:
                continue
    elif bank_names[i] == "bank of communications":
        price_list = document.find_elements_by_class_name("data")

        for item in price_list:
            # 币种	单位	  现汇买入价	现汇卖出价 现钞买入价 现钞卖出价
            #               2            3       4        5
            strs = item.text.split()
            # (V1, V2, B, P)
            # v1 : v2 = price : 1
            try:
                bi.append(
                    ["现汇: 人民币", "现汇: " + strs[0], bank_names[i], float(strs[3]) * (1 / int(strs[1]))])  # 现汇卖出价
                bi.append(
                    ["现汇: " + strs[0], "现汇: 人民币", bank_names[i],
                     1 / (float(strs[2]) * (1 / int(strs[1])))])  # 现汇买入价
            except BaseException:
                continue

    elif bank_names[i] == "china merchants bank":
        price_list = document.find_elements_by_css_selector(".data>tbody>tr")

        for item in price_list:
            # 交易币	交易币单位	基本币	现汇卖出价	现钞卖出价	现汇买入价	现钞买入价	时间
            #            1                   3                                   6
            strs = item.text.split()
            # (V1, V2, B, P)[
            # v1 : v2 = price : 1
            try:
                bi.append(
                    ["现汇: 人民币", "现汇: " + strs[0], bank_names[i], float(strs[3]) * (1 / int(strs[1]))])  # 现汇卖出价
                bi.append(
                    ["现汇: " + strs[0], "现汇: 人民币", bank_names[i],
                     1 / (float(strs[5]) * (1 / int(strs[1])))])  # 现汇买入价
            except BaseException:
                continue

    elif bank_names[i] == "industrial and commercial bank of china":
        document.find_element_by_id("refurbish").click()
        price_list = document.find_elements_by_css_selector(".tableDataTable>tbody>tr")
        for item in price_list:
            # 币种 现汇买入价 现钞买入价 现汇卖出价 现钞卖出价 发布时间
            #          1        2       3           4
            strs = item.text.split()
            # (V1, V2, B, P)
            # v1 : v2 = price : 1
            try:
                bi.append(
                    ["现汇: 人民币", "现汇: " + strs[0], bank_names[i], float(strs[3]) * (1 / 100)])  # 现汇卖出价
                bi.append(
                    ["现汇: " + strs[0], "现汇: 人民币", bank_names[i], 1 / (float(strs[1]) * (1 / 100))])  # 现汇买入价
            except BaseException:
                continue

    elif i == 4:
        # for unknown reason , webdriver cannot open site
        "lczj_box"
    elif bank_names[i] == "china guangfa bank":
        price_list = document.find_elements_by_css_selector('.ratetable>tbody>tr')

        for item in price_list:
            # '币种全称 币种简称 基数 中间价 现汇买入价 现钞买入价 现汇卖出价 现钞卖出价'
            #            1       2            4         5        6           7
            strs = item.text.split()
            # (V1, V2, B, P)
            # v1 : v2 = price : 1
            try:
                bi.append(
                    ["现汇: 人民币", "现汇: " + strs[0], bank_names[i], float(strs[6]) * (1 / int(strs[2]))])  # 现汇卖出价
                bi.append(
                    ["现汇: " + strs[0], "现汇: 人民币", bank_names[i],
                     1 / (float(strs[4]) * (1 / int(strs[2])))])  # 现汇买入价
            except BaseException:
                continue
    elif bank_names[i] == "agricultural bank of china":
        price_list = document.find_elements_by_css_selector('.bindCon>tr')

        for item in price_list:
            # 货币 买入汇率	卖出汇率	现钞买入汇率
            #  0    1           2       3
            strs = item.text.split()
            # (V1, V2, B, P)
            # v1 : v2 = price : 1
            try:
                bi.append(
                    ["现汇: 人民币", "现汇: " + strs[0], bank_names[i], float(strs[2]) * (1 / 100)])  # 现汇卖出价
                bi.append(
                    ["现汇: " + strs[0], "现汇: 人民币", bank_names[i], 1 / (float(strs[1]) * (1 / 100))])  # 现汇买入价
            except BaseException:
                continue
    # having problem getting citi bank , hsbc's exchange rate,

    document.close()
    return bi
    # your have to add d.close before end of the process (chrome driver does not handle auto-close for child processes)


if __name__ == '__main__':

    p = pool()

    bank_info = p.map(itr_banks, range(len(bank_sites)))
    # flatten the list using sum
    bank_info = sum(bank_info, [])

    p.close()
    p.join()
    end = time.time()
    print("Total time used on fetching: %0.3f" % (end - start))

    # a new manipulation will be needed if new bank's exchange rates are added to  bank_info
    for e in bank_info:  # normalize
        e[0] = re.sub("\(.*\)", "", e[0])
        e[1] = re.sub("\(.*\)", "", e[1])
        e[0] = re.sub("/.*", "", e[0])
        e[1] = re.sub("/.*", "", e[1])
    # !!!!!
    # CAUTION THERE MAY BE LOSSES OF WORD 现钞，现汇

    currencies = []
    for item in bank_info:
        name0 = item[0]
        name1 = item[1]
        if name0 not in currencies:
            currencies.append(name0)
        if name1 not in currencies:
            currencies.append(name1)

    n = len(currencies)

    # 3d
    floyd_matrix = [[[float("inf") for i in range(3)] for i in range(len(currencies))] for i in range(len(currencies))]

    # let number of currencies follow the sequence of currency array
    for l in bank_info:
        if l[3] < floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][2]:
            floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][0] = bank_names.index(
                l[2])  # bank no of last exchange
            floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][1] = currencies.index(l[0])  # last currency no
            floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][2] = l[3]  # price

    for i in range(len(currencies)):
        floyd_matrix[i][i][2] = 1
        floyd_matrix[i][i][1] = i


    # 如果经过搜索没有找到从s到e的路径（即，它是循环的"或者是断的即inf"）就返回none 或者 ，否则返回路径
    # 满足d[i][k][2] * d[k][j][2] < d[I][j][2]之后，d[i][k][2] 和 d[k][j][2] 都不为inf，因此d[k][j][1]
    #       和d[i][k][1]都不为inf（可以归纳的证明），所以也就不存在使得m为inf的情况
    def check_seq(s, e):
        ll = [e]
        m = e
        for i in range(len(currencies) + 1):
            try:
                m = floyd_matrix[s][m][1]
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
                if floyd_matrix[i][k][2] * floyd_matrix[k][j][2] < floyd_matrix[i][j][2]:
                    # no duplicated paths are allowed to appear both in l1 and l2
                    # it can be proved that any condition specified here can lead to a valid proof of correct result
                    #     for a shortest path collection under the specified condition.
                    l1 = check_seq(i, k)
                    l2 = check_seq(k, j)
                    if type(l1) == list and type(l2) == list:
                        if find_dup(l1, l2):
                            continue
                    else:  # else?
                        continue
                    floyd_matrix[i][j][2] = floyd_matrix[i][k][2] * floyd_matrix[k][j][2]
                    floyd_matrix[i][j][1] = floyd_matrix[k][j][1]
                    floyd_matrix[i][j][0] = floyd_matrix[k][j][0]

    # describe the path

    ok = [0 for i in range(n)]
    for i in range(n):
        if floyd_matrix[i][i][2] < 1:  # 00
            ok[i] = 1

    # It can be proved that all [price]s below are initial prices, that is, they exist in [bank_list].
    # 描述套汇过程的语句
    arbitrage = ["" for i in range(n)]
    for i in range(n):
        if ok[i] == 1:
            arbitrage[i] = bank_names[i]
            last_cur = -1
            while i != last_cur:
                if last_cur == -1:
                    last_cur = floyd_matrix[i][i][1]
                    b = floyd_matrix[i][i][0]
                    price = floyd_matrix[int(last_cur)][i][2]
                    arbitrage[i] += "<-在银行: " + bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                        int(last_cur)]
                else:
                    prev_last_cur = last_cur
                    last_cur = floyd_matrix[i][last_cur][1]
                    b = floyd_matrix[i][int(last_cur)][0]
                    price = floyd_matrix[int(last_cur)][prev_last_cur][2]
                    arbitrage[i] += "<-在银行: " + bank_names[b] + " 以价格（最低价）" + str(price) + "进行套算, 原币种: " + currencies[
                        int(last_cur)]

    for i in range(n):
        if ok[i] == 1:
            info = "存在" + bank_names[i] + "的套汇机会(而且经计算是最优的), 汇->汇: "
            print(info)
            print(arbitrage[i])
            history_options = save_info_at + "history_options.txt"
            with open(history_options, "a") as f:
                f.write(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                f.write('\n')
                f.write(info)
                f.write('\n')
                f.write(arbitrage[i])
                f.write('\n')
            current_options = save_info_at + "current_options.txt"
            with open(history_options, "w") as f:
                f.write('#')
                f.write(arbitrage[i])
                f.write('\n')
