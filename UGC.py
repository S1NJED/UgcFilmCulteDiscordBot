import requests
from bs4 import BeautifulSoup
from utils import connDb, calcul_avg_color
from discord.ext.commands import Bot
import discord
import asyncio 
from random import randint

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
                "name": movie.select_one(path).text,
                "url": "https://www.ugc.fr/" + movie.select_one(path).attrs.get("href"),
                "poster": movie.select_one("div > div:nth-of-type(1) > div > a > img").attrs.get("data-src")
            }

            movies.append(obj)
        
        return movies

    # TODO: plus tard sah j'ia la flemme
    def getSeanceMovieFromCinema(self, movieName, cinemaId):
        url = "https://www.ugc.fr/showingsFilmAjaxAction!getShowingsByFilm.action"
        """
        
        filmId=15772
        day=2024-09-22
        regionId=3000
        defaultRegionId=1

        __multiselect_versions=
        """
        data = {
            ""
        }

        req = self.session.post(url, data="")
        print(req)

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
            cinemas_ids = cursor.fetchall() # (id, name)

            for id, cinema_name in cinemas_ids:
                movies = self.getCultMoviesFromCinema(id)
                # We check if the movies are already in the database if not we send

                for movie in movies: # name, url, poster

                    cursor.execute("SELECT * FROM movies WHERE cinema_id = ? AND title = ?", (id, movie['name']))
                    movieInDb = cursor.fetchone() # id, name

                    # We notify
                    if not movieInDb:
                        cursor.execute("SELECT channel_id FROM notify_channel")
                        notify_channel_id = cursor.fetchone()

                        if not notify_channel_id:
                            conn.close()
                            return
                        
                        notify_channel_id = int(notify_channel_id[0])
                        notify_channel: discord.TextChannel = self.bot.get_channel(notify_channel_id)

                        embed = discord.Embed(
                            title="🎥 Nouveau film culte",
                            description=f"# [{movie['name']}]({movie['url']})\n**📌 {cinema_name}**"
                        )
                        
                        embed.set_thumbnail(url=movie['poster'])

                        r,g,b = calcul_avg_color(movie['poster'])
                        embed.color = discord.Color.from_rgb(r,g,b)

                        await notify_channel.send(embed=embed) # TODO je reprends demain sah g la flemme de bz la 

                        # await send ..
                        cursor.execute("INSERT INTO movies VALUES(?, ?)", (id, movie['name']))

                        await asyncio.sleep(1.5)

                await asyncio.sleep(1)

            conn.commit()
            conn.close()

            await asyncio.sleep(randint(20*60, 45*60)) # check every 20 minutes et 45 minutes


if __name__ == '__main__':

    scrapper = UgcScrapper()
    
    movies = scrapper.getCultMoviesFromCinema("43")
    
    for movie in movies:
        print(movie)


