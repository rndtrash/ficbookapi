from helpers import profiler
from helpers.responseHelper import pretty
from objects import xd
from bs4 import BeautifulSoup
import requests
import re
from bottle import route, request, response
import json
import time

ficFindPageSnipper = "http://{}/{}?p={}&fandom_filter={}{}{}&filterDirection={}&rating={}&size={}&find=Найти!"

@route("/get/fanfics", method="GET")
def handler():
	with profiler.Profiler() as p:
		requestID = xd.requests + 1
		xd.requests += 1
		print("[{}] Working on {}'s request...".format(requestID, request.environ.get('REMOTE_ADDR')))

		response.content_type='application/json; charset=UTF-8'
		
		fandom_filter = request.query.fandom_filter
		
		fandomIds = request.query.fandoms
		
		tagIds = request.query.tags
			
		pageId = request.query.page
		if not pageId:
			pageId = 1
		else:
			pageId = int(pageId)
			if pageId < 1:
				pageId = 1
		
		direction = request.query.direction
		if not direction:
			direction = ""
		
		rating = request.query.rating
		if not rating:
			rating = ""
		else:
			rating = int(rating)
		
		size = request.query.size
		if not size:
			size = ""
		else:
			size = int(size)
		
		limit = request.query.limit
		if not limit:
			limit = 0
		else:
			limit = int(limit)
			if limit < 0:
				limit = 0
			elif limit > 20:
				limit = 20
		
		scopes = request.query.scope
		
		if (not fandom_filter and not tagIds and not fandomIds):
			return pretty({"error": {"message": "Please set fandom filter, fandoms or tags"}})
		
		fandomsString = ""
		if (len(fandomIds) != 0):
			for x in fandomIds.split(','):
				fandomsString += "&fandom_ids[]={}".format(x)

		tagsString = ""
		if (len(tagIds) != 0):
			for x in tagIds.split(','):
				tagsString += "&tags_include[]={}".format(x)
		
		url = ficFindPageSnipper.format(xd.sitePath, xd.ficFindPath, pageId, fandom_filter, fandomsString, tagsString, direction, rating, size)
		
		page = requests.get(url)

		print("[{}] Parsing '{}' page...".format(requestID, url))

		# Парсим страницу сайта
		soup = BeautifulSoup(page.text, "html.parser")

		print("[{}] Cheking for thread here...".format(requestID))

		if (soup.find_all(name="h1",text="404 — Страница не найдена")):
			print("[{}] Page is not found! Aborting...".format(requestID))
			return pretty({"error": {"message": "Category or fandom is not found"}})
		
		if (soup.find_all(name="h1",text="500 — Ошибка на сервере")):
			print("[{}] Unknown error! Aborting...".format(requestID))
			return pretty({"error": {"message": "Unknown error"}})

		# Отсеиваем блоки фанфиков
		parsedFic = soup.find_all(name="article")

		# Ограничиваем лимит и номер фанфика до 20
		# Если лимит не указан, то парсим все сообщения на странице
		if not limit:
		    limit = len(parsedFic)

		# Счетчик и объект для ответа
		i = 0
		result = {}

		# Цикл для обработки всех фанфиков
		while (i < limit):
			# Временная переменная всех сообщений
			temp = parsedFic

			# Предопределяем атрибут "title" заранее, в противном случае получим KeyError
			result[i] = {"title": {}}
			
			result[i]["id"] = re.sub(r"\?.+$", "", temp[int(i)].find("a", attrs={'href' : re.compile("/readfic/")})['href'].replace("/readfic/", ""))
			
			if "title" in scopes:
				a = temp[int(i)].find("a", attrs={'href' : re.compile("/readfic/")})
				# Запихиваем информацию в JSON объект
				result[i]["title"] = a.get_text().strip()
			else: del result[i]["title"]
			
			if "author" in scopes:
				a = temp[int(i)].find("a", attrs={'href' : re.compile("/authors/")})
				# Запихиваем информацию в JSON объект
				result[i]["author"] = re.sub(r"\?.+$", "", a['href'].replace("/authors/", ""))
			
			if "description" in scopes:
				d = temp[int(i)].find("div", attrs={'class' : "wrap word-break urlize fanfic-description-text"})
				# Запихиваем информацию в JSON объект
				result[i]["description"] = d.get_text().strip()
			
			i += 1

		'''
		    Конечный ответ - JSON объект:
		        sort_keys=False - выключаем сортировку атрибутов по алфавиту,
		        indent=4 - отступ - 4 пробела,
		        separators - сепараторы,
		        ensure_ascii=False - очень важный параметр, правда.

		    Также этот объект кодируется в Юникоде.
		'''
		print("[{}] Api call succeed!".format(requestID))
		return pretty({"fanfics": result})