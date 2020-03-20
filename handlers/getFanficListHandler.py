from helpers import profiler
from helpers.responseHelper import pretty
from objects import xd
from bs4 import BeautifulSoup
import requests
import re
from bottle import route, request, response
import json
import time

ficCategoryPageSnippet = "http://{}/{}/{}/{}?p={}&filterDirection={}&rating={}&size={}"
ficTagPageSnippet = "http://{}/{}/{}?p={}&filterDirection={}&rating={}&size={}"
#TODO: лучше это сделать через /find?...

@route("/get/fanfics", method="GET")
def handler():
	with profiler.Profiler() as p:
		requestID = xd.requests + 1
		xd.requests += 1
		print("[{}] Working on {}'s request...".format(requestID, request.environ.get('REMOTE_ADDR')))
		
		categoryId = request.query.category
		if not categoryId:
			categoryId = ""
			
		fandomId = request.query.fandom
		if not fandomId:
			fandomId = ""
		
		tagId = request.query.tag
		if not tagId:
			tagId = 0
			
		pageId = request.query.page
		if not pageId:
			pageId = 1
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
		
		scopes = request.query.scope
		
		if (tagId == 0 and categoryId == "" and fandomId == ""):
			return pretty({"error": {"message": "Please set either category and fandom or tag ID"}})

		url = None
		if (tagId == 0):
			url = ficCategoryPageSnippet.format(xd.sitePath, xd.ficListByCategoryPath, categoryId, fandomId, pageId, direction, rating, size)
		elif (categoryId == "" and fandomId == ""):
			url = ficTagPageSnippet.format(xd.sitePath, xd.ficListByTagPath, tagId, pageId, direction, rating, size)
		
		page = requests.get(url)

		print("[{}] Parsing '{}' page...".format(requestID, url))

		# Парсим страницу сайта
		soup = BeautifulSoup(page.text, "html.parser")

		print("[{}] Cheking for thread here...".format(requestID))

		response.content_type='application/json; charset=UTF-8'

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
		if (limit > 20):
		    self.write("Too big limit, biggest is 20")
		    return
		elif not limit:
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