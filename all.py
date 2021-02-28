
# 说明：
# 此项目在2019年7月启动，由长沙理工大学计算机系杨思捷独立完成
# 顶点a->b->c的长度的现实意义就是1单位a币换成b币然后再换成c币最终得到多少c币
# 数字会有0.1%内的误差（由机器浮点误差导致）
# 需要加入新的银行，并保证币种名字统一
# 搜索 *** 以发现暂时没有着手解决的问题

from selenium import webdriver as wb
from selenium.webdriver.chrome.options import Options
import re
import langconv as lang
from multiprocessing import Pool as pool
import time
import datetime


chrome_options = Options()
# 设置chrome浏览器无界面模式
chrome_options.add_argument('--headless')
document = wb.Chrome('/usr/local/Cellar/python@3.8/3.8.5/bin/chromedriver', chrome_options=chrome_options)

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
currencies = []
bank_info = []


# 由于某些原因，此函数内记录的边的长度并不等于项目说明中定义的数，而是它的倒数
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


def run_iteration():
    start = time.time()

    # 超时设置
    # 这两种设置都进行才有效。如果超时，会报错（若不设置，则超时多久都不报错）
    document.set_page_load_timeout(5)
    document.set_script_timeout(5)

    p = pool()

    global bank_info
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
        e[3] = 1.0 / e[3]
    # !!!!!
    # CAUTION THERE MAY BE LOSSES OF WORD 现钞，现汇

    for item in bank_info:
        name0 = item[0]
        name1 = item[1]
        if name0 not in currencies:
            currencies.append(name0)
        if name1 not in currencies:
            currencies.append(name1)


def run_algo():
    LAST_EDGE = 0
    LAST_VERTEX = 1
    VAR_MIN = 2
    ORIGINAL_LEN = 3

    n = len(currencies)

    minus_vertexes = []
    minus_cycles = []

    # for fixed i and j, consider floyd_matrix[i][j][0~2], where floyd_matrix[i][j][2] works for conventional
    # usage of floyd_matrix[i][j] in Floyd-Warshall algorithm. floyd_matrix[i][j][0~1] are for floyd_next[i][j].
    # floyd_matrix[i][j][3] means original length of edge i->j
    floyd_matrix = [[[0 for i in range(4)] for i in range(len(currencies))] for i in range(len(currencies))]

    # let number of currencies follow the sequence of currency array
    for l in bank_info:
        if l[3] > floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][VAR_MIN]:
            floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][LAST_EDGE] = bank_names.index(l[2])
            floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][LAST_VERTEX] = currencies.index(l[0])
            floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][VAR_MIN] = l[3]
            floyd_matrix[currencies.index(l[0])][currencies.index(l[1])][ORIGINAL_LEN] = l[3]
            #
            #          ________________________________________
            #         /          bank1:0.8    ->               \         Assume two vertexes and two edges like this,
            #  ++++++                                           ++++++   floyd_matrix[*]["CNY"][LAST_EDGE] is "bank2"
            #  + USD+                                           +CNY +   floyd_matrix[*]["CNY"][LAST_VERTEX] is "USD"
            #  +    +                                           +    +   floyd_matrix["USD"]["CNY"][ORIGINAL_LEN] is 0.8
            #  ++++++            bank2:1.2    <-                ++++++
            #         \________________________________________/

    # Due to finding most negative cycle is NP-complete, I personally simplify our concern to a cycle of 2 and 3 vertex
    for i in range(n):
        for j in range(n):
            if floyd_matrix[i][j][VAR_MIN] * floyd_matrix[j][i][VAR_MIN] > 1:
                minus_cycles.append([i, j, floyd_matrix[i][j][VAR_MIN] * floyd_matrix[j][i][VAR_MIN]])

    for i in range(n):
        for j in range(n):
            for k in range(n):
                if floyd_matrix[i][j][VAR_MIN] * floyd_matrix[j][k][VAR_MIN] * floyd_matrix[k][i][VAR_MIN] > 1:
                    minus_cycles.append(
                        [i, j, k,
                         floyd_matrix[i][j][VAR_MIN] * floyd_matrix[j][k][VAR_MIN] * floyd_matrix[k][i][VAR_MIN]])
                if floyd_matrix[i][k][VAR_MIN] * floyd_matrix[k][j][VAR_MIN] * floyd_matrix[j][i][VAR_MIN] > 1:
                    minus_cycles.append(
                        [i, k, j,
                         floyd_matrix[i][k][VAR_MIN] * floyd_matrix[k][j][VAR_MIN] * floyd_matrix[j][i][VAR_MIN]])

    print(str(len(minus_cycles))+" methods in total:")
    for cycle in minus_cycles:
        if len(cycle) == 3:
            print(
                currencies[cycle[0]] + " -> " + currencies[cycle[1]] + " via " +
                bank_names[int(floyd_matrix[cycle[0]][cycle[1]][LAST_EDGE])] + " , " +
                currencies[cycle[1]] + " -> " + currencies[cycle[0]] + " via " +
                bank_names[int(floyd_matrix[cycle[1]][cycle[0]][LAST_EDGE])] + " " +
                str(cycle[2])
            )
        if len(cycle) == 4:
            print(
                currencies[cycle[0]] + " -> " + currencies[cycle[1]] + " via " +
                bank_names[int(floyd_matrix[cycle[0]][cycle[1]][LAST_EDGE])] + " , " +
                currencies[cycle[1]] + " -> " + currencies[cycle[2]] + " via " +
                bank_names[int(floyd_matrix[cycle[1]][cycle[2]][LAST_EDGE])] + " , " +
                currencies[cycle[2]] + " -> " + currencies[cycle[0]] + " via " +
                bank_names[int(floyd_matrix[cycle[2]][cycle[0]][LAST_EDGE])] + " " +
                str(cycle[3])
            )


if __name__ == '__main__':
    run_iteration()
    run_algo()
