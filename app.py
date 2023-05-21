from flask import Flask, render_template, request, redirect, session,jsonify
from zenora import APIClient
from discord_webhook import DiscordWebhook
import json
import os




#############設定#############
ADMIN = [851062442330816522,733920687751823372,549056425943629825,914474252688846878] #管理員id

BOT_TOKEN="" #discord機器人token
CLIENT_SECRET="" #discord oautch2 clinet secret
CLIENT_ID=1082619932841345035 #discord app id
APP_URL="https://cb.mycard.lol/" #架設網址

LOGIN_LOG="" #登入通知 discord webhook網址
ADD_LOG="" #發布文章通知 discord webhook網址
#############設定#############



app = Flask(__name__)
client = APIClient(BOT_TOKEN, client_secret=CLIENT_SECRET)
app.config["SECRET_KEY"] = "mysecret"



@app.route("/api")
def api():
    with open(f"bot.json", mode="r", encoding="utf-8") as filt:
        data = json.load(filt)
    c=[]
    for i in data:
        c.append(i)
    allpost=0
    for i in data:
        allpost+=data[i][0]
    okpost=0
    for i in data:
        okpost+=data[i][1]
    d={
        "所有類別":c,
        "全部投稿數":allpost,
        "已發布投稿數":okpost
    }
    response = jsonify(d)
    return response

@app.route("/api/list")
def apilist():
    yourPath = './data'
    all = os.listdir(yourPath)
    d={}
    for i in all:
        with open(f"data/{i}", mode="r", encoding="utf-8") as filt:
            data = json.load(filt)
        if data["look"] == True:
            name=data["menu"]+str(data["id"])
            da={"id":data["id"],"text":data["text"],"menu":data["menu"]}
            d[name]=da
    response = jsonify(d)
    return response

@app.route("/")
def home():
    access_token = session.get("access_token")
    with open(f"bot.json", mode="r", encoding="utf-8") as filt:
        ndata = json.load(filt)

    if not access_token:
        return render_template("index.html",menu=ndata)

    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    if not current_user.id in ADMIN:
        return render_template("index.html",menu=ndata)
        
    return render_template("index.html", user=current_user,menu=ndata)

@app.route("/add",methods=["POST"])
def info():
    text = request.form["text"]
    if len(text) < 10:
        return redirect(f"/#add")
    menu=request.form["menu"]
    with open(f"bot.json", mode="r", encoding="utf-8") as filt:
        ndata = json.load(filt)
    if not menu in ndata:
        return redirect(f"/#add")
    num=ndata[menu][0]
    ndata[menu][0]+=1
    data={"look":False,"num":num,"menu":menu,"id":None,"text":text}
    with open(f"bot.json", mode="w", encoding="utf-8") as filt:
        json.dump(ndata,filt)
    with open(f"data/{menu}{num}.json", mode="w+", encoding="utf-8") as filt:
        json.dump(data,filt)
    webhook = DiscordWebhook(url=ADD_LOG, content=text,username=menu+str(num))
    response = webhook.execute()
    return redirect(f"/#ok")


@app.route("/ok")
def ok():
    if not request.values.get("num") == None:
        num=request.values.get("num")
        return render_template("ok.html", num=num)
    else:
        return redirect("/add")
    

@app.route("/list/<mu>")
def list(mu):
    yourPath = './data'
    all = os.listdir(yourPath)
    l=[]
    for i in all:
        with open(f"data/{i}", mode="r", encoding="utf-8") as filt:
            data = json.load(filt)
        if data["look"] == True:
            if data["menu"] == mu:
                text=data["text"]
                id=data["id"]
                menu=data["menu"]
                t=[f"{menu}#{str(id)}",""]
                for q in text.split("\n"):
                    t.append(q)
                l.append(t)
    return render_template("list.html", l=l, menu=mu)

@app.route("/admin/list")
def adminlist():
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/login")

    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    if not current_user.id in ADMIN:
        return redirect("/login")
    yourPath = './data'
    all = os.listdir(yourPath)
    l=[]
    for i in all:
        with open(f"data/{i}", mode="r", encoding="utf-8") as filt:
            data = json.load(filt)
        if data["look"] == False:
            text=data["text"]
            num=data["num"]
            menu=data["menu"]
            t=[f"{menu}",str(num),""]
            for q in text.split("\n"):
                t.append(q)
            t.append("")
            t.append("==============")
            l.append(t)
    return render_template("adminlist.html", l=l,user="a")


@app.route("/admin/ok/<menu>/<num>")
def adminok(menu,num):
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/")

    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    if not current_user.id in ADMIN:
        return redirect("/")
    with open(f"bot.json", mode="r", encoding="utf-8") as filt:
        ndata = json.load(filt)
    try:
        with open(f"data/{menu}{num}.json", mode="r", encoding="utf-8") as filt:
            data = json.load(filt)
    except:
        return "no"
    if data["look"] == True:
        return "ed"
        
    id=ndata[menu][1]
    ndata[menu][1]+=1
    data["look"]=True
    data["id"]=id
    with open(f"data/{menu}{num}.json", mode="w", encoding="utf-8") as filt:
        json.dump(data,filt)
    with open(f"bot.json", mode="w", encoding="utf-8") as filt:
        json.dump(ndata,filt)
    url=ndata[menu][2]
    text=data["text"]
    name=f"{menu}#{id}"
    webhook = DiscordWebhook(url=url, content=text,username=name,avatar_url="https://media.discordapp.net/attachments/1082677335511273472/1084854042443923547/icon.png?width=640&height=640")
    response = webhook.execute()
    return redirect("/admin/list")


@app.route("/admin/no/<menu>/<num>")
def adminno(menu,num):
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/")

    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    if not current_user.id in ADMIN:
        return redirect("/")
    os.remove(f"data/{menu}{num}.json")
    return redirect("/admin/list")


@app.route("/login")
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={APP_URL}oauth%2Fcallback&response_type=code&scope=identify%20email")


@app.route("/logout")
def logout():
    session.pop("access_token")
    return redirect("/")


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args["code"]
    access_token = client.oauth.get_access_token(
        code, redirect_uri=f"{APP_URL}oauth/callback"
    ).access_token
    session["access_token"] = access_token
    return redirect("/log")

@app.route("/log")
def log():
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/")

    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    webhook = DiscordWebhook(url=LOGIN_LOG, content=f"用戶: {current_user.username} ({current_user.id})")
    response = webhook.execute()
    return redirect("/")

app.run(host="0.0.0.0",port=25571,debug=True)