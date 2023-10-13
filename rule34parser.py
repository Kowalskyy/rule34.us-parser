import aiohttp
import asyncio
import aiofiles
import shutil
import os
from bs4 import BeautifulSoup

def clear():
	shutil.rmtree('media')
	os.mkdir('media')

urls = []
downloads = []

async def download(url):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as request:
			filename = os.path.basename(url) # getting image name to name downloads
			download = await request.read()
			async with aiofiles.open(f'media/{filename}', 'wb') as f: # using aiofiles cuz why not
				await f.write(download)
				print(f'downloaded {url}')
				await f.close()

async def get_urls(url):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as request:
			code = await request.text()
			soup = BeautifulSoup(code, 'html.parser')
			title = soup.find('div', class_='content_push') # finding container with images
			img = title.find('img').get('src') # very smartly
			vid = title.find('video') # made separation
			if vid is None: # of images and videos
				downloads.append(asyncio.create_task(download(img)))
			else:
				source = vid.find('source').get('src')
				downloads.append(asyncio.create_task(download(source)))
		await asyncio.gather(*downloads)


async def load(url):
	base_url = 'https://rule34.us/index.php?r=posts/index&q=' + '+'.join(url.split(', '))
	async with aiohttp.ClientSession() as session:
		async with session.get(url if 'https://rule34.us' in url else base_url) as request:
			code = await request.text()
			soup = BeautifulSoup(code, 'html.parser')
			try:
				posts = soup.find('div', class_= 'thumbail-container') # find posts container
				post_click = posts.find_all('a')
				for post_url in post_click:
					post = post_url.get('href')
					urls.append(asyncio.create_task(get_urls(post)))
				await asyncio.gather(*urls)
			except Exception as e:
				print('probably wrong tag/no posts')
				return

who = input('input url or tags: ')
asyncio.run(load(who))