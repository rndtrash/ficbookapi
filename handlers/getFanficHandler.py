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
ficSnippet = "https://{}/{}/{}"
ficPageSnippet = "https://{}/{}/{}/{}"

@route("/get/fanfic", method="GET")
def handler():
	with profiler.Profiler() as p:
		requestID = xd.requests + 1
		xd.requests += 1
		print("[{}] Working on {}'s request...".format(requestID, request.environ.get('REMOTE_ADDR')))

		response.content_type='application/json; charset=UTF-8'
		
		ficId = request.query.id
		if not ficId:
			return pretty({"error": {"message": "Cannot find fanfic ID!"}})
			
		pageId = request.query.page
		if not pageId:
			pageId = 0
		else:
			pageId = int(pageId)
		
		scopes = request.query.scope

		url = None
		if (pageId == 0):
			url = ficSnippet.format(xd.sitePath, xd.ficPath, ficId)
		else:
			url = ficPageSnippet.format(xd.sitePath, xd.ficPath, ficId, pageId)
		
		page = requests.get(url)

		print("[{}] Parsing '{}' page...".format(requestID, url))

		# Парсим страницу сайта
		soup = BeautifulSoup(page.text, "html.parser")

		print("[{}] Cheking for thread here...".format(requestID))

		if (soup.find_all(name="h1",text="404 — Страница не найдена")):
			print("[{}] Page is not found! Aborting...".format(requestID))
			return pretty({"error": {"message": "Fanfic or page is not found"}})
		
		if (soup.find_all(name="h1",text="500 — Ошибка на сервере")):
			print("[{}] Unknown error! Aborting...".format(requestID))
			return pretty({"error": {"message": "Unknown error"}})

		# Объект для ответа
		result = {}
		
		# Проверяем, состоит ли фанфик из одной страницы (или это страница, выбранная через "page")
		parsedTextBlock = soup.find(name="div", attrs={'id' : 'content'})
		if parsedTextBlock:
			# Фанфик состоит из одной страницы или это страница, выбранная через аргумент "page"
			result["text"] = parsedTextBlock.get_text()
			if "page_title" in scopes:
				result["page_title"] = soup.find(name="h2").get_text()
		else:
			pages = soup.find(name="ul", attrs={'class' : 'list-unstyled table-of-contents'}).find_all(name="a")
			result["pages"] = {}
			for i, page in enumerate(pages):
				result["pages"][i] = {"id": ''}
				result["pages"][i]["id"] = re.sub(r"#.+$", "", page['href'].replace("/readfic/{}/".format(ficId), ""))
				if "page_title" in scopes:
					result["pages"][i]["title"] = page.get_text()
		
		temp = soup.find(name="section", attrs={'class' : re.compile("fanfiction-hat")})
		if "title" in scopes:
			a = temp.find(name="h1")
			a.find("sup").extract()
			# Запихиваем информацию в JSON объект
			result["title"] = a.get_text().strip()
			
		if "author" in scopes:
			a = temp.find("a", attrs={'href' : re.compile("/authors/")})
			# Запихиваем информацию в JSON объект
			result["author"] = re.sub(r"\?.+$", "", a['href'].replace("/authors/", ""))
			
		if "description" in scopes:
			d = temp.find("div", attrs={'class' : re.compile("urlize")})
			# Запихиваем информацию в JSON объект
			result["description"] = d.get_text().strip()

		'''
		    Конечный ответ - JSON объект:
		        sort_keys=False - выключаем сортировку атрибутов по алфавиту,
		        indent=4 - отступ - 4 пробела,
		        separators - сепараторы,
		        ensure_ascii=False - очень важный параметр, правда.

		    Также этот объект кодируется в Юникоде.
		'''
		print("[{}] Api call succeed!".format(requestID))
		return pretty(result)