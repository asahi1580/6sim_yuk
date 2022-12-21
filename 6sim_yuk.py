#入力した６曲の平均とプレイリスト内の曲のユークリッド距離をとり、類似度を計算
#使用ファイル import.txt    第一引数に指定する出力ファイル(.txt)
#import.txtから入力、output_text_folder内に第一引数で指定したファイルを保存
#tempoの正規化を実装済

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import numpy
import math
import sys
import datetime
import pytz

client_id = '52daefbfe55b4f14baf2ca49a6ee745a'
client_secret = '5329ddcdb1624154bf94c8c230390867'
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

idl = {}
with open('import.txt') as i:
    for line in i:
        (k,v) = line.split()
        idl[k] = v

file = open("output_text_folder/" + sys.argv[1], 'w')
dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
file.write(dt_now.strftime('%Y年%m月%d日 %H:%M:%S')+'\n')



#プレイリストのURLからIDのみを取り出す
playlist_list = [idl['playlist1'],idl['playlist2'],idl['playlist3'] ]
playlist_id_list = []                 

target = '?'
for i in playlist_list:   
  pl = i[34:]
  pl_idx = pl.find(target)
  pl = pl[:pl_idx]
  playlist_id_list.append(pl)
  playlist_name = sp.playlist(pl)
  file.write('検索先プレイリスト:'+playlist_name['name']+'\n')
#曲のURLからIDのみを取り出す
music_list = [idl['m1'],idl['m2'],idl['m3'],idl['m4'],idl['m5'],idl['m6']]
music_id_list = []
m_list = []                       #make_important_elementに曲の情報を渡すためのリスト
for i in music_list:   
  pl = i[31:]
  #pl_idx = pl.find(target)
  pl = pl[:pl_idx]                #plにIDが入っている
  music_id_list.append(pl)
  result = sp.audio_features(pl)
  x = sp.track(pl)
  file.write(x['name']+'\n')      #曲名の表示
  #pprint.pprint(result)
  m = result[0]
  m_list.append(m)
  m_str = json.dumps(m)           #ファイルに書き込むためにdictからstringに変換
  file.write(m_str)               #曲のパラメーターの表示
  file.write('\n')
D = 'danceability'
E = 'energy'
Lo = 'loudness'
S = 'speechiness'
A = 'acousticness'
Li = 'liveness'
V = 'valence'
T = 'tempo'
element_list = [D,E,S,A,Li,V,T]
avg_dict = {}

def t_normal(a):
  i = (a-30.0)/(250.0-30.0)
  return i

def make_average_element(msc1,msc2,msc3,msc4,msc5,msc6):   
  for element in element_list:
    if (element == T):
      element_data = [t_normal(msc1[element]),t_normal(msc2[element]),t_normal(msc3[element]),t_normal(msc4[element]),t_normal(msc5[element]),t_normal(msc6[element])]
    else:
      element_data = [msc1[element], msc2[element],msc3[element],msc4[element],msc5[element],msc6[element]]
    avg = numpy.mean(element_data)
    avg = round(avg,3)
    avg_dict[element] = avg
make_average_element(m_list[0],m_list[1],m_list[2],m_list[3],m_list[4],m_list[5])
str_dict = json.dumps(avg_dict)
file.write(str_dict+'\n')        #入力した６曲の平均の辞書リスト

def sim_distance(avg,music):     #ユークリッド距離を計算する関数
  si = {D,E,S,A,Li,V,T}
  squares = [(avg[item] - music[item]) ** 2 for item in si]
  sum_of_sqrt = math.sqrt(sum(squares))
  return 1/(1 + sum_of_sqrt)
  
features = []
id_list = []
match_id_list = []      #要素を満たす曲のIDリスト このリストを更新していき、曲を絞っていく
for a in range(3):
  file.write('-----------------------------------------------\n')
  playlist_num = str(a+1)
  file.write('検索先プレイリスト'+playlist_num+'\n')
  playlist_data = sp.user_playlist('31ljsv2irs6y7cgnfg737awxg2fe',playlist_id_list[a])     ##引数１：自分のユーザーID　引数２：プレイリストID
  features.clear()
  id_list.clear()
  match_id_list.clear()
  for track in playlist_data['tracks']['items']:
   try:
    id = track['track']['id']
   except TypeError:
     file.write('プレイリスト内に曲ではないものが含まれている可能性があります')
     continue
   id_list.append(id)
  features.extend(sp.audio_features(id_list))
 
  for feature in features:
   feature[T] = t_normal(feature[T])
   print(sim_distance(avg_dict,feature))
   if(sim_distance(avg_dict,feature)) > 0.83:              #6曲の平均とプレイリスト内の曲のユークリッド距離が0.8以上のものを探す
       # 条件に合致した曲を取得
       match = sp.track(feature['id'])
       match_id_list.append(match['id'])    
  features.clear()
  if len(features) == 1:
    break
  
  for mm in match_id_list:
    final_match = sp.track(mm)
    file.write('name: '+final_match['name']+'('+final_match['artists'][0]['name']+')'+'https://open.spotify.com/track/'+final_match['id']+'\n')   #最終的にマッチした曲名を表示
  file.write('処理が終了しました。\n')
file.close()