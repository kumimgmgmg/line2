from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import passw, requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():

    if request.method == 'POST':
        ci  = request.form['commutein']   # 定期の出発駅
        cm1 = request.form['commutemid1'] # 定期の経由駅1
        cm2 = request.form['commutemid2'] # 定期の経由駅2
        cm3 = request.form['commutemid3'] # 定期の経由駅3
        cm4 = request.form['commutemid4'] # 定期の経由駅4
        co  = request.form['commuteout']  # 定期の到着駅
        ai  = request.form['actualin']    # 実際の出発駅
        ao  = request.form['actualout']   # 実際の目的駅
        comlist = []
        actlist = []

        comlist = commute(ci,co,cm1,cm2,cm3,cm4) # 通る駅の2次元配列を返す関数(下で定義)
     #  actlist = actroute(ai, ao)               # 実際に通るであろうルートを返す関数(下で定義)

    #   処理1: actlistの1次元配列(ルートリスト)からとcomlistを比較して、共通する数を点数化。
    #   処理2: 共通する数が高い順に表示。か、一番高いのを表示
    # tru & except忘れずに！
        return render_template('index.html', comlist)
    else:
        return render_template('index.html')

def commute(ci, co, *cms): # ci, cm1,2,3, coの駅から、1つの経路を固有の駅idで返す
    list1 = [] # 入力駅リスト
    ste = []  # 路線リスト[[路線1,路線2,..],[路線A,路線B,..],[路線a, 路線b],..]
    kekka = []
    list1.append(ci); list1.append(co) # listにci,coを追加
    try:
        for i in cms:
            list1.append(i)
    except:
        cms = ""
    stidlist1 = stid(list1) # 下で定義したstid()で駅idを取得、リスト化
    for j in stidlist1: # [[路線1,路線2,..],[路線A,路線B,..],[路線a, 路線b],..]を作る
        url = "http://www.ekidata.jp/api/g/" + str(j) + ".xml"
        r = requests.get(url)
        soup = BeautifulSoup(r.text.encode(r.encoding), "lxml") # htmlparser or lxml
        linelist = soup.find_all('line_cd')
        naihou = [y.string for innerlist in linelist for y in innerlist]
        ste.append(naihou)
    if len(cms) == 0: # ci,coのみ - ste[0]とste[1]から一数する路線をピックアップ, その路線から、間の駅を全てピックアップ(駅固有id)
        set0 = set(ste[0]); set1 = set(ste[1])
        li1 = list(set0 & set1)
        url1 = "http://www.ekidata.jp/api/l/" + str(li1[0]) + ".xml"
        r1 = requests.get(url1)
        soup1 = BeautifulSoup(r1.text.encode(r1.encoding), "lxml")
        sid1 = soup1.find_all('station_cd'); sname1 = soup1.find_all('station_name')
        snnai1 = [y.string for innerlist in sname1 for y in innerlist]
        sidnai1 = [y.string for innerlist in sid1 for y in innerlist]
        idx0 = snnai1.index(ci); idx1 = snnai1.index(co)
        kekka = [i for i in sidnai1[idx1:idx0]] or [i for i in sidnai1[idx0:idx1]]
        return kekka
    elif len(cms) == 1: # cm1がある - ste[0]とste[1]から一数する路線をピックアップ, その路線から、間の駅を全てピックアップ(駅固有id)
        set0 = set(ste[0]); set1 = set(ste[1]); set2 = set(ste[2])
        li02 = list(set0 & set2); li12 = list(set1 & set2)
        url02 = "http://www.ekidata.jp/api/l/" + str(li02[0]) + ".xml"
        url12 = "http://www.ekidata.jp/api/l/" + str(li12[0]) + ".xml"
        r02 = requests.get(url02); r12 = requests.get(url12)
        soup02 = BeautifulSoup(r02.text.encode(r02.encoding), "lxml")
        soup12 = BeautifulSoup(r12.text.encode(r12.encoding), "lxml")
        sid02 = soup02.find_all('station_cd'); sname02 = soup02.find_all('station_name')
        sid12 = soup12.find_all('station_cd'); sname12 = soup12.find_all('station_name')
        sidnai02 = [y.string for innerlist in sid02 for y in innerlist]; snnai02 = [y.string for innerlist in sname02 for y in innerlist]
        sidnai12 = [y.string for innerlist in sid12 for y in innerlist]; snnai12 = [y.string for innerlist in sname12 for y in innerlist]
        idx0 = snnai02.index(ci); idx1 = snnai02.index(cms[0]); idx2 = snnai12.index(cms[0]); idx3 = snnai12.index(co)
        kekka = [i for i in sidnai02[idx1:idx0]] or [i for i in sidnai02[idx0:idx1]]
        if sidnai12[idx2:idx3] == []:
            for ias in sidnai12[idx3:idx2]: kekka.append(ias)
        else:
            for ias in sidnai12[idx2:idx3]: kekka.append(ias)
        return kekka
    elif len(cms) == 2: # cm1,cm2がある - ste[0]とste[1]から一数する路線をピックアップ, その路線から、間の駅を全てピックアップ(駅固有id)
        set0 = set(ste[0]); set1 = set(ste[1]); set2 = set(ste[2]); set3 = set(ste[3])
        li02 = list(set0 & set2); li23 = list(set2 & set3); li31 = list(set1 & set3)
        url02 = "http://www.ekidata.jp/api/l/" + str(li02[0]) + ".xml"; url23 = "http://www.ekidata.jp/api/l/" + str(li23[0]) + ".xml"
        url31 = "http://www.ekidata.jp/api/l/" + str(li31[0]) + ".xml"
        r02 = requests.get(url02); r23 = requests.get(url23); r31 = requests.get(url31);
        soup02 = BeautifulSoup(r02.text.encode(r02.encoding), "lxml"); soup23 = BeautifulSoup(r23.text.encode(r23.encoding), "lxml")
        soup31 = BeautifulSoup(r31.text.encode(r31.encoding), "lxml")
        sid02 = soup02.find_all('station_cd'); sname02 = soup02.find_all('station_name')
        sid23 = soup23.find_all('station_cd'); sname23 = soup23.find_all('station_name')
        sid31 = soup31.find_all('station_cd'); sname31 = soup31.find_all('station_name')
        sidnai02 = [y.string for innerlist in sid02 for y in innerlist]; snnai02 = [y.string for innerlist in sname02 for y in innerlist]
        sidnai23 = [y.string for innerlist in sid23 for y in innerlist]; snnai23 = [y.string for innerlist in sname23 for y in innerlist]
        sidnai31 = [y.string for innerlist in sid31 for y in innerlist]; snnai31 = [y.string for innerlist in sname31 for y in innerlist]
        idx0 = snnai02.index(ci); idx1 = snnai02.index(cms[0]); idx2 = snnai23.index(cms[0]);
        idx3 = snnai23.index(cms[1]); idx4 = snnai31.index(cms[1]); idx5 = snnai31.index(co);
        kekka = [i for i in sidnai02[idx1:idx0]] or [i for i in sidnai02[idx0:idx1]]
        if sidnai23[idx2:idx3] == []:
            for ias in sidnai23[idx3:idx2]: kekka.append(ias)
        else:
            for ias in sidnai23[idx2:idx3]: kekka.append(ias)
        if sidnai31[idx4:idx5] == []:
            for ian in sidnai31[idx5:idx4]: kekka.append(ian)
        else:
            for ian in sidnai31[idx4:idx5]: kekka.append(ian)
        return kekka
    elif len(cms) == 3: # cm1,cm2,cm3がある - ste[0]とste[1]から一数する路線をピックアップ, その路線から、間の駅を全てピックアップ(駅固有id)
        kekka = ["error"]
        return kekka
    else:
        kekka = ["error"]
        return kekka
    # steにて[0]-[2],(3以降があれば続く[2,3..]),[2]-[1]で共通の路線をピックアップ。
    # その路線内で、駅同士の間の駅をすべてピックアップし、一つのリストにまとめる。
# (ちなみに、駅idは路線&駅で固有のidが割り振られている。つまり、駅id = "駅名&路線名" = ○○線△駅)
    return "定期で通る○○線△△駅の配列のリストを返す" # 通る駅のリストを返す [駅id1, 駅id2...]

def stid(list):
    stidlist = []
    conn = passw.connectdb()
    cur = conn.cursor()
    for j in list:
        cur.execute("SELECT stid FROM station where stname='" + j + "';") # 引数すべての駅idを引っ張ってくる
        stidlist.append(cur.fetchone())
    stidlist1 = [e for inner_list in stidlist for e in inner_list]
    return stidlist1



def actroute(ai, ao):
    # ai, ao の経路を複数把握(パターン化/配列)

    # return [[駅id1,駅id2,..] , [駅id21 , 駅id22]]
    #        [[            ルート1              ] , [              ルート2          ]]
    return "実際に通るであろうルートのパターンを2次元配列のリストで返す"

"""
   もともとは...
  駅の料金が一番安いルートというコンセプトから、駅の料金データを利用,比較して、最安のルートを探すプログラムを作る

   できなかったこと
 1 まず、無料の駅の料金データ,もしくはそれに準ずる無料のAPIがない。(かなり探しこんだので、これは確か。)
 2 で、第2案として、他のサービスの検索フォームにプログラムから駅データを入力し、その結果をこちらに返すプログラムにする。
    -> 正直かなりリスキー & 邪道 & DDosにつながらないよう対策。
    -> 複雑, 重すぎる, 検索サイトの仕様変更で動かなくリスクもあり却下。

   結局..
  定期圏内に最も多く入ったルートを最安ルートとしてとるアルゴリズム。(新幹線は例外)

   必要なもの
  定期のルートデータ(運賃はいらない), 実際のルート全通り
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)