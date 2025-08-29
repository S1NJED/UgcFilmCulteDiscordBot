import requests
import sqlite3
from bs4 import BeautifulSoup
from utils import connDb, calcul_avg_color, MONTHS, DAYS
from discord.ext.commands import Bot
import discord
import asyncio 
from random import randint
from datetime import datetime
import traceback

class UgcRegions:
    def __init__(self):
        self.PARIS = "1"
        self.REGION_PARISIENNE = "2"
        self.BORDEAUX = "3"
        self.CAEN = "4"
        self.LILLE_METROPOLE = "5"
        self.LYON = "6"
        self.NANCY = "7"
        self.NANTES = "8"
        # PAS DE ID 9 jsp pq
        self.STRASBOURG = "10"
        self.TOULOUSE = "11"

class UgcScrapper(UgcRegions):
    
    def __init__(self, bot: Bot = None):
        self.bot = bot

        super().__init__()
        
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        self.HEADERS = {
            "user-agent": self.UA
        }
        self.session = requests.Session()
        self.session.headers = self.HEADERS
        self.workerLoopState = True
    
    def getCinemasFromRegion(self, regionId):
        url = f"https://www.ugc.fr/cinemasAjaxAction!getCinemasList.action?id={regionId}"
        req = self.session.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        
        ''' type Cinema

        int id;
        string name;
        int movieAmount;
        string address;
        
        '''

        scrapped_cinemas = [cinema for cinema in soup.select("div.band") if not "cinema-empty" in cinema.attrs['class']]
        cinemas = []

        for cinema in scrapped_cinemas:
            base_path = "div > div > div > div > "
            obj = {
                "id": cinema.select_one(base_path + "div > ul > li").attrs.get("data-distance-id"),
                "name": cinema.select_one(base_path + "a").attrs.get("title"),
                "movieAmount": cinema.select_one(base_path + "div > p:nth-of-type(1)").text, # useless for now jsp qd je vais l'add mais on verra
                "address": cinema.select_one(base_path + "div > p:nth-of-type(2)").text
            }

            cinemas.append(obj)
        
        return cinemas
    
    def getCultMoviesFromCinema(self, cinemaId):
        url = f"https://www.ugc.fr/filmsAjaxAction!getFilmsAndFilters.action?filter=&page=30010&cinemaId={cinemaId}&reset=false&__multiselect_versions=&labels=UGC Culte&__multiselect_labels="
        req = self.session.get(url)
        soup = BeautifulSoup(req.text, "html.parser")

        '''type CultMovie

        string name;
        string url;
        '''

        scrapped_movies = soup.select("div#stillOnDisplay > div:nth-of-type(2) > div > div > div > div > div > div")
        movies = []

        for movie in scrapped_movies:
            path = "div > div:nth-of-type(2) > div > a"

            obj = {
                "name": movie.select_one(path).text.strip(),
                "id": movie.select_one(path).attrs.get("id").split('_')[1],
                "url": "https://www.ugc.fr/" + movie.select_one(path).attrs.get("href"),
                "poster": movie.select_one("div > div:nth-of-type(1) > div > a > img").attrs.get("data-src")
            }

            movies.append(obj)
        
        return movies

    # Il peut y en avoir plusieurs
    # currentTempCinemaId	"43" -- COokies
    #
    # https://www.ugc.fr/showingsFilmAjaxAction!getDaysByFilm.action
    # 
    '''
    https://www.ugc.fr/showingsFilmAjaxAction!getShowingsByFilm.action?filmId=13414&day=2024-11-02&regionId=3000&defaultRegionId=1&
    '''
    def getMovieSeances(self, movieId, cinemaId):
        url = f"https://www.ugc.fr/showingsFilmAjaxAction!getDaysByFilm.action?filmId={movieId}&regionId=3000"
        """
        filmId=15772
        regionId=3000
        defaultRegionId=1

        __multiselect_versions=
        """

        self.session.cookies['currentTempCinemaId'] = cinemaId

        req = self.session.post(url, data="", headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })

        print(req)

        self.session.cookies['currentTempCinemaId'] = None

        soup = BeautifulSoup(req.text, "html.parser")

        with open('./index.html', 'w') as file:
            file.write(req.text)

        try:
            dates = [date.attrs.get("id").removeprefix("nav_date_3000_") for date in soup.select("div[data-index]")] # YYYY-MM-DD
            print(dates)

            seanceDate = []
            for date in dates:
                weekDay = datetime.strptime(date, "%Y-%m-%d").weekday()
                year, month, day = date.split('-')
                seanceDate.append( f":calendar_spiral: {DAYS[int(weekDay)]} {day} {MONTHS[int(month)-1]} {year}" )

        except Exception as err:
            traceback.print_exc()
            seanceDate = [":calendar_spiral: Impossible d'avoir la date"]

        return seanceDate

    # must be executed in a different thread
    """
    flow:
    
    iterate over every cinemas in the db and check the cult movies
    and if the movies from THE cinema is not in the database we notify
    
    """
    async def worker(self):
        if not self.bot:
            raise Exception("bot instance is missing")
        
        while self.workerLoopState:
            
            conn = connDb()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM cinemas")
            notify_channel = cursor.fetchone()

            if not notify_channel:
                await asyncio.sleep(5)
                continue

            cursor.execute("SELECT * FROM cinemas")
            cinemas_ids = cursor.fetchall() # (id, name)

            for id, cinema_name in cinemas_ids:
<<<<<<< Updated upstream
                print(id, cinema_name)
=======
                print(id,  cinema_name)

>>>>>>> Stashed changes
                movies = self.getCultMoviesFromCinema(id)
                # We check if the movies are already in the database if not we send

                for movie in movies: # name, url, poster
                    
                    cursor.execute("SELECT * FROM movies WHERE cinema_id = ? AND title = ?", (id, movie['name']))
                    movieInDb = cursor.fetchone() # id, name

                    # We notify
                    if not movieInDb:
                        cursor.execute("SELECT channel_id, message FROM notify_channel")
                        notify_channel_id, message = cursor.fetchone()
                        
                        notify_channel_id = int(notify_channel_id)
                        notify_channel: discord.TextChannel = self.bot.get_channel(notify_channel_id)

                        embed = discord.Embed(
                            title="🎥 Nouveau film culte",
                            description=f"# [{movie['name']}]({movie['url']}?cinemaId={id})\n**📌 {cinema_name}**\n\n{'\n'.join(self.getMovieSeances(movie['id'], str(id)))}"
                        )
                        
                        embed.set_thumbnail(url=movie['poster'])

                        r,g,b = calcul_avg_color(movie['poster'])
                        embed.color = discord.Color.from_rgb(r,g,b)

                        await notify_channel.send(content=message, embed=embed) # TODO je reprends demain sah g la flemme de bz la 

                        # await send ..
                        cursor.execute("INSERT INTO movies VALUES(?, ?)", (id, movie['name']))

                        await asyncio.sleep(1.5)

                await asyncio.sleep(1)

            conn.commit()
            conn.close()

            await asyncio.sleep(randint(20*60, 45*60)) # check every 20 minutes et 45 minutes

