import sys, os, requests, re, json, urllib.request, urllib.error, hashlib, hmac, traceback, logging, shutil
from pytablewriter import MarkdownTableWriter

# key for tdmb link generation (from ps3, ps4)
tmdb_key = bytearray.fromhex('F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0')

title_ids = [
    'CUSA07022_00', # Fortnite
    'CUSA11100_00', # Black Ops 4
    'CUSA05969_00', # WWII
    'CUSA04762_00', # Infinite Warfare
    'CUSA03522_00', # Modern Warfare Remastered
    'CUSA00314_00', # Wolfenstein®: The New Order
    'CUSA00004_00', # inFAMOUS™: Second Son
    'CUSA00511_00', # BEYOND: Two Souls™
    'CUSA07694_00', # Patapon™2 Remastered
    'CUSA10211_00', # Horizon Zero Dawn™ Complete Edition
    'CUSA17714_00', # Fall Guys: Ultimate Knockout
    'CUSA01615_00', # FINAL FANTASY XV
    'CUSA01836_00', # Deus Ex: Mankind Divided
    'CUSA01433_00', # Rocket League®
    'CUSA03468_00', # Vampyr
    'CUSA04301_00', # Dreams™
    'CUSA11993_00', # Marvel’s Spider-Man
    'CUSA04294_00', # WATCH_DOGS®2
    'CUSA00717_00', # Detroit: Become Human™
    'CUSA05716_00', # Rise of the Tomb Raider
    'CUSA17776_00'  # Marvel's Spider-Man: Miles Morales
]

image_dir = 'ps4'

def create_url(title_id):
    hash = hmac.new(tmdb_key, bytes(title_id, 'utf-8'), hashlib.sha1)
    return f'https://tmdb.np.dl.playstation.net/tmdb2/{title_id}_{hash.hexdigest().upper()}/{title_id}.json'


if __name__ == '__main__':
    log = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    handler.setLevel(logging.INFO)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    discord_title_ids = []

    done = {"ps4": []}
    table_writer = None

    if os.path.isfile('README.template'):
        table_writer = MarkdownTableWriter()
        table_writer.headers = ["Icon", "Title"]
        table_writer.value_matrix = []
    else:
         print('missing README.template. wont update README.md file.')

    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)

    # added all the titleIds... now get their images
    for title_id in title_ids:
        url = create_url(title_id)
        content = requests.get(url)
        print(url)

        if content.status_code != 200:
            print('skipping', title_id)
            continue

        content = content.json()
        
        game_name = content['names'][0]['name']
        
        print(game_name)

        if not content['icons'] or len(content['icons']) == 0:
            print('\tno icons')
            continue

        game_icon = None

        for icon in content['icons']:
            if icon['type'] == '512x512':
                game_icon = icon['icon']
                break
        
        if game_icon == None:
            print('\tno 512x512 icon')
            continue

        done["ps4"].append({
            "name": game_name,
            "titleId": title_id
        })

        discord_title_ids.append(title_id.lower())

        if not os.path.exists(image_dir):
            os.mkdir(image_dir)

        icon_file = f'{image_dir}/{title_id}.png'

        if table_writer != None:
            table_writer.value_matrix.append([
                f'<img src="{icon_file}?raw=true" width="100" height="100">',
                game_name
            ])

        if os.path.exists(icon_file):
            print('\ticon file exists')
            continue

        urllib.request.urlretrieve(game_icon, icon_file)
        
        print('\tsaved')
    
    if table_writer != None:
        with open("README.template", "rt") as template:
            with open('README.md', 'wt', encoding='utf-8') as readme:
                for line in template:
                    readme.write(line.replace('!!games!!', table_writer.dumps()))
    
    with open('games.json', 'w') as games_file:
       json.dump(done, games_file)
