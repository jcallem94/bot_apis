import discord
from discord.ext import commands
import os, random
from bot_logic import get_duck_image_url
import aiohttp  

imagenes = os.listdir('images')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hola, soy un bot {bot.user}!')

@bot.command()
async def heh(ctx, count_heh = 5):
    await ctx.send("he" * count_heh)

@bot.command()
async def meme(ctx):
    imagen = random.choice(imagenes)
    with open(f'images/{imagen}', 'rb') as f:
        # ¡Vamos a almacenar el archivo de la biblioteca Discord convertido en esta variable!
        picture = discord.File(f)
    # A continuación, podemos enviar este archivo como parámetro.
    await ctx.send(file=picture)

@bot.command('duck')
async def duck(ctx):
    '''Una vez que llamamos al comando duck, 
    el programa llama a la función get_duck_image_url'''
    image_url = get_duck_image_url()
    await ctx.send(image_url)
 
@bot.command(name='pokemon')  
async def pokemon_info(ctx, pokemon_name: str = None):  
    # Verificar si el usuario no proporcionó un nombre de Pokémon  
    if not pokemon_name:  
        await ctx.send("❓ **Uso del comando:** `!pokemon <nombre_del_pokemon>`\n"  
                       "Por ejemplo: `!pokemon pikachu`")  
        return  

    # Convertir el nombre a minúsculas para evitar errores  
    pokemon_name = pokemon_name.lower()  

    # URL de la PokeAPI  
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}'  

    try:  
        async with aiohttp.ClientSession() as session:  
            async with session.get(url) as response:  
                if response.status == 200:  
                    data = await response.json()  

                    # Crear un embed con la información del Pokémon  
                    embed = discord.Embed(  
                        title=f"#{data['id']} {pokemon_name.capitalize()}",  
                        color=discord.Color.green()  
                    )  

                    # Añadir la imagen del Pokémon  
                    embed.set_thumbnail(url=data['sprites']['front_default'])  

                    # Tipos del Pokémon  
                    types = [t['type']['name'] for t in data['types']]  
                    embed.add_field(name="Tipos", value=', '.join(types), inline=False)  

                    # Estadísticas base  
                    stats = []  
                    for stat in data['stats']:  
                        stats.append(f"{stat['stat']['name']}: {stat['base_stat']}")  
                    embed.add_field(name="Estadísticas", value='\n'.join(stats), inline=False)  

                    # Altura y peso  
                    height = data['height'] / 10  # Convertir a metros  
                    weight = data['weight'] / 10  # Convertir a kilogramos  
                    embed.add_field(name="Altura", value=f"{height}m", inline=True)  
                    embed.add_field(name="Peso", value=f"{weight}kg", inline=True)  

                    # Habilidades  
                    abilities = [ability['ability']['name'].replace('-', ' ').title()   
                               for ability in data['abilities']]  
                    embed.add_field(name="Habilidades",   
                                  value='\n'.join(abilities),   
                                  inline=False)  

                    await ctx.send(embed=embed)  
                else:  
                    await ctx.send(f"❌ No se encontró el Pokémon '{pokemon_name}'. Por favor, verifica el nombre e inténtalo de nuevo.")  

    except Exception as e:  
        await ctx.send(f"⚠️ Ocurrió un error: {str(e)}")  

@bot.command(name='anime')  
async def anime_search(ctx, *, search_term: str = None):  
    if not search_term:  
        embed = discord.Embed(  
            title="❓ Ayuda del Comando Anime",  
            description="Busca información detallada sobre un anime",  
            color=discord.Color.blue()  
        )  
        embed.add_field(  
            name="Uso",  
            value="`!anime <nombre del anime>`\nPor ejemplo: `!anime naruto`",  
            inline=False  
        )  
        await ctx.send(embed=embed)  
        return  
  
    # URL de la API de Kitsu  
    url = f'https://kitsu.io/api/edge/anime?filter[text]={search_term}'  
  
    async with aiohttp.ClientSession() as session:  
        try:  
            async with session.get(url) as response:  
                if response.status == 200:  
                    data = await response.json()  
  
                    if not data['data']:  
                        await ctx.send(f"❌ No se encontraron resultados para '{search_term}'")  
                        return  
  
                    # Tomamos el primer resultado como el más relevante  
                    anime = data['data'][0]['attributes']  
  
                    # Crear un embed con la información detallada  
                    embed = discord.Embed(  
                        title=anime.get('canonicalTitle', 'Sin título'),  
                        description=anime.get('synopsis', 'Sin descripción disponible')[:2048],  
                        color=discord.Color.purple()  
                    )  
  
                    # Añadir imagen de portada si está disponible  
                    if anime.get('posterImage') and anime['posterImage'].get('original'):  
                        embed.set_thumbnail(url=anime['posterImage']['original'])  
  
                    # Títulos alternativos  
                    titles = []  
                    if anime.get('titles'):  
                        if anime['titles'].get('en'): titles.append(f"🇺🇸 {anime['titles']['en']}")  
                        if anime['titles'].get('ja_jp'): titles.append(f"🇯🇵 {anime['titles']['ja_jp']}")  
                    if titles:  
                        embed.add_field(  
                            name="Títulos Alternativos",  
                            value="\n".join(titles),  
                            inline=False  
                        )  
  
                    # Información general  
                    info_general = []  
                    if anime.get('status'):  
                        status_map = {  
                            'finished': '✅ Finalizado',  
                            'current': '🟢 En emisión',  
                            'upcoming': '⏳ Próximamente',  
                            'tba': '❓ Por anunciar'  
                        }  
                        info_general.append(f"Estado: {status_map.get(anime['status'], anime['status'])}")  
                      
                    if anime.get('episodeCount'):  
                        info_general.append(f"Episodios: {anime['episodeCount']}")  
                      
                    if anime.get('averageRating'):  
                        rating = float(anime['averageRating']) / 10  
                        info_general.append(f"Puntuación: ⭐ {rating}/10")  
                      
                    if anime.get('ageRating'):  
                        info_general.append(f"Clasificación: {anime['ageRating']}")  
                      
                    if anime.get('startDate'):  
                        info_general.append(f"Fecha de inicio: {anime['startDate']}")  
                      
                    if info_general:  
                        embed.add_field(  
                            name="Información General",  
                            value="\n".join(info_general),  
                            inline=False  
                        )  
  
                    # Géneros si están disponibles  
                    if anime.get('genres'):  
                        genres = [genre['name'] for genre in anime['genres']]  
                        embed.add_field(  
                            name="Géneros",  
                            value=", ".join(genres) if genres else "No disponible",  
                            inline=False  
                        )  
  
                    # Estadísticas  
                    stats = []  
                    if anime.get('popularityRank'):  
                        stats.append(f"Ranking de Popularidad: #{anime['popularityRank']}")  
                    if anime.get('ratingRank'):  
                        stats.append(f"Ranking de Calificación: #{anime['ratingRank']}")  
                    if stats:  
                        embed.add_field(  
                            name="Estadísticas",  
                            value="\n".join(stats),  
                            inline=False  
                        )  
  
                    # Footer con información adicional  
                    embed.set_footer(text="Datos proporcionados por Kitsu.io")  
  
                    await ctx.send(embed=embed)  
                else:  
                    await ctx.send("⚠️ Error al conectar con la API de Kitsu")  
  
        except Exception as e:  
            await ctx.send(f"⚠️ Ocurrió un error: {str(e)}")  
  

bot.run("MTI0NTgzODQ2Mjg1MTA4ODQxNQ.GfRRBY.Gs1o0U4YWXVLMPN8Fzg8hDID121VyG64Gczsgs")
