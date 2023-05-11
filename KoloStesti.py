# importy
import random
import time
import PySimpleGUI as grafika
from datetime import date
import discord_bot
from Hra import Hra

# absultni cesta k logum
CESTA_LOGY_DK = r"REPLACED_PATH\KoloStesti\LogsDK.txt"
CESTA_LOGY_DF = r"REPLACED_PATH\KoloStesti\LogsDF.txt"
CESTA_LOGY_DFK = r"REPLACED_PATH\KoloStesti\LogsDFK.txt"
CESTA_LOGY_DKM = r"REPLACED_PATH\KoloStesti\LogsDKM.txt"
CESTA_LOGY_D = r"REPLACED_PATH\KoloStesti\LogsD.txt"
CESTA_LOGY_DFKM = r"REPLACED_PATH\KoloStesti\LogsDFKM.txt"
CESTA_KDO_BYL_TOCEN_NAPOSLED = r"REPLACED_PATH\KoloStesti\KdoBylTocenNaposled.txt"

def ZjistiKohoJsmeTociliNaposled():
    try:
        soubor = open(CESTA_KDO_BYL_TOCEN_NAPOSLED, "rt")
        return soubor.read()
    except:
        print("Soubor KdoBylTocenNaposled nenelezen nebo poškozen.")
        exit()

def ZapisKdoBylTocen(koho_jsme_tocili):
    try:
        soubor = open(CESTA_KDO_BYL_TOCEN_NAPOSLED, "wt")
        soubor.write(koho_jsme_tocili)
    except:
        print("Soubor KdoBylTocenNaposled nenelezen nebo poškozen.")
        exit()

def NajdiLogy(koho_jsme_tocili):
    if koho_jsme_tocili == "DK":
        return CESTA_LOGY_DK
    elif koho_jsme_tocili == "DFK":
        return CESTA_LOGY_DFK
    elif koho_jsme_tocili == "D":
        return CESTA_LOGY_D
    elif koho_jsme_tocili == "DFKM":
        return CESTA_LOGY_DFKM
    elif koho_jsme_tocili == "DKM":
        return CESTA_LOGY_DKM
    elif koho_jsme_tocili == "DF":
        return CESTA_LOGY_DF

def ZapisDoDatabaze(koho_jsme_tocili, text):
    # databaze
    umisteni_logu = NajdiLogy(koho_jsme_tocili)
    try:
        databaze = open(umisteni_logu, "at")
        databaze.write(text)
        databaze.close()
    except:
        print("Soubor s logy nenalezen nebo poškozen.")
        exit()


def RemoveUnwantedGames(list_her_grafika, list_her, window, kdo_chce_hrat):
    wanted_games = []

    for index in range(0,len(list_her_grafika)):
        if kdo_chce_hrat in list_her[index].list_chticu:
            window[list_her_grafika[index].key].Update(visible = True)
            wanted_games.append(list_her_grafika[index])
            if (kdo_chce_hrat == "DKM" and list_her_grafika[index].key == "League of Legends"):
                for i in range(0,9):
                    wanted_games.append(list_her_grafika[index])
        else:
            window[list_her_grafika[index].key].Update(visible = False)

    window.refresh()
    return wanted_games

def MakeAllVisible(list_konkretni, window):
    for hra in list_konkretni:
        window[hra.Get()].Update(visible = True)

def Vybel(list_konkretni):
    for hra_bila in list_konkretni:
        hra_bila.update(text_color='White')

def Toceni(list_konkretni, kc):

    Vybel(list_konkretni)

    interval = 0.01
    konecny_cas = kc
    vyherni_hra = random.choice(list(list_konkretni))
    hra_bila = list_konkretni[0]
    koncime = False

    while not koncime:
        for hra_zelena in list_konkretni:
            hra_zelena.update(text_color='Lime')
            if hra_bila.key != hra_zelena.key:
                hra_bila.update(text_color='White')
            hra_bila = hra_zelena
            window.refresh()
            time.sleep(interval)
            if interval > konecny_cas and hra_bila == vyherni_hra:
                koncime = True
                break

            interval+=0.02    

    # vybrani viteze
    output.update("\nUžijte si " + vyherni_hra.Get())
    window.refresh()

    return vyherni_hra

# list her, ktere pripadaji v uvahu
apex = Hra("Apex Legends", ["DK", "D", "K", "DKM"], 1)
pubg = Hra("PUBG: Battlegrounds", ["DK", "K", "DKM"], 1)
csgo = Hra("Counter Strike: Global Offensive", ["DK", "D", "DKM"], 1)
fortnite = Hra("Fortnite", ["DK", "D", "DKM"], 1)
programovani = Hra("Programovani kola stesti", ["DK"], 1)
lost_ark = Hra("Lost Ark", ["DK", "D", "K", "DKM"], 1)
payday2 = Hra("Payday 2", ["DFK", "DK", "FK", "F", "K", "DKM"], 1)
lolko = Hra("League of Legends", ["DM", "D", "M", "DKM", "DF"], 1)
fall_guys = Hra("Fall Guys", ["DFK", "DK", "DF", "FK", "D", "K", "F", "DKM"], 1)
overwatch = Hra("Overwatch", ["DFK", "DK", "DF", "FK", "D", "K", "F", "DKM"], 1)
gta = Hra("Grant Treft Auto V", ["DFK", "F", "DK", "DF"], 1)
keep_talking = Hra("Keep Talking and Nobody Explodes", ["DK", "DF"], 1)
orcs = Hra("Orcs Must Die", ["DK", "K"], 1)
deceive = Hra("Deceive", ["DFK", "DK", "DF"], 1)

list_her = [apex, pubg, csgo, fortnite, programovani, lost_ark, payday2, lolko, fall_guys, overwatch, gta, keep_talking, orcs, deceive]

# barvy
back = "Black"
front = "White"

# font
nas_font = ("Arial", 18)

# texty
output = grafika.Text("", text_color=front, background_color=back, font = nas_font)
minula_hra = grafika.Text("\nJak dopadla minulá hra?", text_color=front, background_color=back, font = nas_font)
winlose = grafika.Text("", text_color=front, background_color=back, font = nas_font)

list_her_grafika = []

# vytvor list textu z listu her
for hra in list_her:
    list_her_grafika.append(grafika.Text(hra.nazev, text_color=front, font = nas_font, background_color=back, key=hra.nazev))

# buttony
dk_button = grafika.Button("DK", button_color = 'Green', font = nas_font , mouseover_colors='DarkGreen', size = (7,0))
df_button = grafika.Button("DF", button_color = 'Green', font = nas_font, mouseover_colors='DarkGreen', size = (7,0))
dfk_button = grafika.Button("DFK", button_color = 'Green', font = nas_font, mouseover_colors='DarkGreen', size = (7,0))
dkm_button = grafika.Button("DKM", button_color = 'Green', font = nas_font, mouseover_colors='DarkGreen', size = (7,0))
d_button = grafika.Button("D", button_color = 'Green', font = nas_font, mouseover_colors='DarkGreen', size = (7,0))
dfkm_button = grafika.Button("DFKM", button_color = 'Green', font = nas_font, mouseover_colors='DarkGreen', size = (7,0))
w = grafika.Button("W", button_color = 'Green', font = nas_font, mouseover_colors='DarkGreen', size = (7,0))
l = grafika.Button("L", button_color = 'Green', font = nas_font, mouseover_colors='DarkGreen', size = (7,0))


# vytvor layout z danych her
layout = []

for hra in list_her_grafika:
    layout.append([hra])

# pridej buttony
layout.append([output])
layout.append([dk_button, dfk_button, dkm_button, d_button, dfkm_button, df_button])
layout.append([minula_hra])
layout.append([w,l])
layout.append([winlose])

# vlastnosti okna
window = grafika.Window(title="Gamerský kolo", layout=layout, background_color="Black", use_default_focus=False)

# vyherce
konecna_vyherni_hra = list_her_grafika[0]

koho_jsme_tocili = ""

# beh kola
while True:
    # precteni okna
    event, values = window.read()

    # zmacknuti tlacitka ZATOC
    if event == "DK":
        konecna_vyherni_hra = Toceni(RemoveUnwantedGames(list_her_grafika, list_her , window, "DK"), random.uniform(0.3, 0.8))
        koho_jsme_tocili = "DK"
    elif event == "DFK":
        konecna_vyherni_hra = Toceni(RemoveUnwantedGames(list_her_grafika, list_her , window, "DFK"), random.uniform(0.3, 0.8))
        koho_jsme_tocili = "DFK"
    elif event == "DF":
        konecna_vyherni_hra = Toceni(RemoveUnwantedGames(list_her_grafika, list_her , window, "DF"), random.uniform(0.3, 0.8))
        koho_jsme_tocili = "DF"
    elif event == "DKM":
        konecna_vyherni_hra = Toceni(RemoveUnwantedGames(list_her_grafika, list_her , window, "DKM"), random.uniform(0.3, 0.8))
        koho_jsme_tocili = "DKM"
    elif event == "D":
        konecna_vyherni_hra = Toceni(RemoveUnwantedGames(list_her_grafika, list_her , window, "D"), random.uniform(0.3, 0.8))
        koho_jsme_tocili = "D"
    elif event == "DFKM":
        konecna_vyherni_hra = Toceni(RemoveUnwantedGames(list_her_grafika, list_her , window, "DFKM"), random.uniform(0.3, 0.8))
        koho_jsme_tocili = "DFKM"
    elif event == "W":
        koho_jsme_tocili = ZjistiKohoJsmeTociliNaposled()
        ZapisDoDatabaze(koho_jsme_tocili, "W\n")
        winlose.update("\n YOU ARE THE BEST" )
    elif event == "L":
        koho_jsme_tocili = ZjistiKohoJsmeTociliNaposled()
        ZapisDoDatabaze(koho_jsme_tocili, "L\n")
        winlose.update("\n YOU SUCK" )
    # zavreni okna
    elif event == grafika.WIN_CLOSED:
        ZapisDoDatabaze(koho_jsme_tocili, date.today().strftime("%d.%m.%Y") + " " + konecna_vyherni_hra.Get() + " ")
        ZapisKdoBylTocen(koho_jsme_tocili)
        discord_bot.StartBot(konecna_vyherni_hra.Get())
        break

