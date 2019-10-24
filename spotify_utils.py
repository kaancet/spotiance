import spotipy
import spotipy.util as util
import pandas as pd
import numpy as np
import dateutil.parser as dp

## TODO LOOK AT SCOPES 
def get_token(username,scope):
    # how to not leave them inside source code??
    client_id='491a6bacf0324a5f9fae53586ed2d985'
    client_secret='74f7c2bc50c54d86b8ba69e25ec638c5'
    redirect_url='http://localhost/'
    token=util.prompt_for_user_token(username,
                               scope,
                               client_id=client_id,
                               client_secret=client_secret,
                               redirect_uri=redirect_url)
    return token

class User:

    def __init__(self,username):
        self.username = username
        self.get_user_info()
        self.playlists = self.get_playlists()
        self.top_tracks = self.get_top_list(tolist='tracks')
        self.top_artists = self.get_top_list(tolist='artists')

    '''
    Methods to get user info with spotipy module 
    and parse to class attributes
    '''
    def get_user_info(self):
        user = sp.me()
        self.display_name = user['display_name']
        self.profimg_irl = user['images'][0]['url']

    def get_playlists(self):
        pl_dict = {}
        try:
            playlists = sp.user_playlists(self.username)
        except:
            scope = 'user-library-read'
            token = get_token(self.username,scope)
            sp=spotipy.Spotify(auth=token)
            playlists = sp.user_playlists(self.username)
            
        for item in playlists['items']:
            pl_dict[item.get('name')] = Playlist(self.username,item.get('id'))
        return pl_dict

    def get_top_list(self,limit=10,time_range='medium_term',tolist='tracks'):
        top_list ={}
        try:
            _ = sp.current_user_top_tracks(limit=limit,time_range=time_range)
        except:
            scope = 'user-top-read'
            token = get_token(self.username,scope)
            sp=spotipy.Spotify(auth=token)
            _ = sp.current_user_top_tracks(limit=limit,time_range=time_range)
        

        if tolist=='tracks':
            tops=sp.current_user_top_tracks(limit=limit,time_range=time_range)
            for i,top in enumerate(tops['items']):
                top_list[str(i+1)]=Track(top.get('id'))
        elif tolist=='artists':
            tops=sp.current_user_top_artists(limit=limit,time_range=time_range)
            for i,top in enumerate(tops['items']):
                top_list[str(i+1)]=Artist(top.get('id'),artistname=top.get('name'))
        else:
            pass
        return top_list


    #TO DO:
    #user music taste as an attribute extracted from playlist data
       #can be top 5 genres
    # user recently played
    # user top artists

class Playlist:
    
    def __init__(self,username,plid):
        self.username = username
        self.plid = plid
        self.get_pl_info()
    '''
    Methods to get track info with spotipy module 
    and parse to class attributes
    '''
    def get_pl_info(self):
        p=sp.user_playlist(self.username,self.plid)
        self.name = p['name']
        self.isPublic = p['public']
        self.isCollab = p['collaborative']
        self.trackCount = p['tracks']['total']
    
    def read_tracks(self):
        p=sp.user_playlist(self.username,self.plid)
        for t in p['tracks']['items']:
            # convert date string to datetime object
            # read the tracks to somewhere
            pass
#             print(t['track']['id'],t['added_at'])
    '''
    Visualization methods
    '''
    def extract_features(self):
        pass
        # music taste change through time(what is taste here?)

class Track:
    def __init__(self, trackid, **kwargs):
        self.trackid = trackid
        self.date_added = kwargs.get('date_added','')
        self.get_track_info()
    
    '''
    Methods to get track info with spotipy module 
    and parse to class attributes
    '''
    def get_track_info(self):
        t=sp.track(self.trackid)
        self.name = t['name']
        self.artist = [x['name'] for x in t['artists']]
        self.artist_id = [x['id'] for x in t['artists']]
        self.album = t['album']['name']
        self.duration = t['duration_ms']
        self.popularity = t['popularity']
        self.preview_url = t['preview_url']
        self.audio_features=sp.audio_features(self.trackid)[0]
        self.track_genre=self.get_genre(self.artist_id)
        
    
    def get_genre(self,artist_id):
        genre=[]
        if not type(artist_id) is list:
            artist_id=[artist_id]
        for i in artist_id:
            a=sp.artist(i)
            genre += a['genres']
        return list(set(genre))

    '''
    Display Methods
    '''
    def display_track_info(self):
        df_info = pd.DataFrame(data=[vars(self)],index=[0])
        pd.set_option('display.max_rows', len(df_info))
        print(df_info)
    
    def display_track_features(self):
        df_feature = pd.DataFrame(data=self.audio_features,index=[0])
        pd.set_option('display.max_rows', len(df_feature))
        print(df_feature)

class Artist:
        def __init__(self, artistid,**kwargs):
            self.artistid = artistid
            self.atistname = kwargs.get('artistname','')
            self.top_tracks = self.get_top_tracks()

        def get_top_tracks(self):
            pass

        def display_artist(self):
            print(self.artistname)




