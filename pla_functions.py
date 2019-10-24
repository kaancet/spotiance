# import plotly
# import plotly.graph_objs as go

#%%
import pandas as pd
import numpy as np
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.request import urlretrieve
# import librosa

#%%
def authSpotify():
    username='kaan3'
    client_id='491a6bacf0324a5f9fae53586ed2d985'
    client_secret='74f7c2bc50c54d86b8ba69e25ec638c5'
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id,client_secret=client_secret)
    sp=spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

#%%
# get playlist and put it in a dataframe\n"
def add_tracks(track_df,tracks):
    for item in tracks['items']:
        track = item['track']
        if track['preview_url'] is None:
            preview=''
        else:    
            preview=track['preview_url']
        track_row=pd.Series([track['id'],
                            track['artists'][0]['name'],
                            track['name'],
                            track['duration_ms']/float(60000),
                            preview],
                        index=track_df.columns)
        track_df=track_df.append(track_row,ignore_index=True)
    return track_df
#%%
#get a single song  
def get_song(artist,song,token=token):
    df_columns=['Artist','Song','Duration','preview_url'] 
    try:
        sp=spotipy.Spotify(auth=token) 
    except:
        token=authSpotify()
        sp=spotipy.Spotify(auth=token) 
    
    results=sp.search(q='artist:'+artist+' track:'+song,limit=1) 
    try: 
        print('Preview URL found!') 
        track_row=pd.Series([results['tracks']['items'][0]['artists'][0]['name'],
                             results['tracks']['items'][0]['name'],
                             results['tracks']['items'][0]['duration_ms']/float(60000),
                             results['tracks']['items'][0]['preview_url']],index=df_columns)
        return track_row 
    except: 
        print('There is no preview URL') 
        return [] 

# Get rid of tracks w/o preview URLS's
def clean_nonePreview(track_df):
    clean_df=track_df[track_df['preview_url'] != '']
    clean_df.reset_index(inplace=True,drop=True)
    return clean_df

#%%
def get_playlist(username='kaan3',playlist_name='Puis danse',sp=sp):
    
    #create empty track dataframe with column names
    df_columns=['id','Artist','Song','Duration','preview_url']
    track_df = pd.DataFrame(columns=df_columns)
    playlists=sp.user_playlists(username)
    selected_pl=[item for item in playlists['items'] if item.get('name')==playlist_name][0]

    results = sp.user_playlist(username, selected_pl['id'],fields="tracks,next")
    tracks = results['tracks']
    track_df=add_tracks(track_df,tracks)
    no_prew=sum(x=='' for x in track_df['preview_url'])
    print('%d / %d of tracks lack a preview URL' %(no_prew,tracks['total']))
    track_df=clean_nonePreview(track_df)
    return (track_df,playlist_name),no_prew
#%%
## Retrieve the previews and get desire features in a dataset
# tempo(from percussive)
# spectral bandwith difference (from harmonic) []
# average spectral flatness*100 [How much noise like a sound is]
# octave based spectral contrast** [represents the relative spectral distribution]
def analyze_track(row,analyze_columns=['tempo','band_diff','spec_flat']):
    url=row['preview_url']
    urlretrieve(url,'temp_song.wav')
    print('Preview of %s-%s successfully retrieved!' %(row['Artist'],row['Song']))
    print('Extracting Features...')
    
    y,sr = librosa.core.load('temp_song.wav')
    y_harmonic,y_percussive = librosa.effects.hpss(y)
    #tempo
    tempo,_ = librosa.beat.beat_track(y_percussive,sr)
    #spectral bandwidth difference
    harmonic_band = librosa.feature.spectral_bandwidth(y=y_harmonic,sr=sr)
    band_diff = np.max(harmonic_band)-np.min(harmonic_band)
    #average specral flatness
    harmonic_flatness = librosa.feature.spectral_flatness(y=y_harmonic)
    spec_flat = np.mean(harmonic_flatness)*100
    #average spectral contrast
#     harmonic_contrast = librosa.feature.spectral_contrast(y=y_harmonic,sr=sr)
#     spec_contrast = np.mean(harmonic_contrast)
    print('Done')
    analyze_res=[tempo,band_diff,spec_flat]
#     for i,key in enumerate(analyze_dict):
#         analyze_dict[key]=analyze_res[i]
#     return analyze_dict
    analyze_series=pd.Series(analyze_res,index=analyze_columns)
    analyze_row=pd.concat([row,analyze_series],axis=0)
    return analyze_row

def analyze_playlist(playlist_tuple,analyze_columns=['tempo','band_diff','spec_flat']):
    playlist_df=playlist_tuple[0]
    playlist_df.reset_index(inplace=True,drop=True)
    analyze_df=pd.DataFrame(columns=list(playlist_df.columns)+analyze_columns)
    for row in playlist_df.iterrows():
        try:
            row_result = analyze_track(row[1],analyze_columns)
            analyze_df = analyze_df.append(row_result,ignore_index=True)
        except:
            print('Preview of %s-%s does not exist, moving on...' %(row[1]['Artist'],row[1]['Song']))
            pass
    return (analyze_df,playlist_tuple[1])

#%%
