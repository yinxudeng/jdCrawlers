# coding=utf-8
import requests, time, xlrd, xlwt
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from xlutils.copy import copy
from urllib.parse import quote
from json.decoder import JSONDecodeError

startTime = time.time()

class Product:
	def __init__(self, productID, name, price, goodRate, commentCount, store, timeStamp, productURL):
		self.productID = productID
		self.name = name
		self.price = price
		self.goodRate = goodRate
		self.commentCount = commentCount
		self.store = store
		self.timeStamp = timeStamp
		self.productURL = productURL

	def print(self):
		print("*" * 204)
		print("".join(["PRODUCT ID: ", self.productID]))
		print("".join(["NAME: ", self.name]))
		print("".join(["PRICE: ¥", self.price]))
		print("".join(["GOOD RATE: ", self.goodRate]))
		print("".join(["NUMBER OF COMMENTS: ", self.commentCount]))
		print("".join(["STORE: ", self.store]))
		print("".join(["TIME STAMP: ", self.timeStamp]))
		print("".join(["PRODUCT URL: ", self.productURL]))
		print("*" * 204)

	def save(self):
		try:
			info = xlrd.open_workbook('ProductInfo.xls')
			numRows = info.sheets()[0].nrows
			newInfo = copy(info)
			sheet = newInfo.get_sheet(0)
			sheet.write(numRows, 0, self.productID)
			sheet.write(numRows, 1, self.name)
			sheet.write(numRows, 2, self.price)
			sheet.write(numRows, 3, self.goodRate)
			sheet.write(numRows, 4, self.commentCount)
			sheet.write(numRows, 5, self.store)
			sheet.write(numRows, 6, self.timeStamp)
			sheet.write(numRows, 7, self.productURL)
			newInfo.save('ProductInfo.xls')
		except FileNotFoundError:
			info = xlwt.Workbook()
			sheet = info.add_sheet("Sheet1")
			sheet.write(0, 0, self.productID)
			sheet.write(0, 1, self.name)
			sheet.write(0, 2, self.price)
			sheet.write(0, 3, self.goodRate)
			sheet.write(0, 4, self.commentCount)
			sheet.write(0, 5, self.store)
			sheet.write(0, 6, self.timeStamp)
			sheet.write(0, 7, self.productURL)
			info.save('ProductInfo.xls')
		

def getInformation(productURL):
	html = urlopen(productURL)
	bs = BeautifulSoup(html, "html.parser")
	productID = productURL[20:-5]
	name = bs.find("div", {"class": "sku-name"}).get_text().strip()
	try:
		price = requests.get("".join(["https://p.3.cn/prices/mgets?skuIds=J_", productID])).json()[0]["p"]
	except JSONDecodeError as e:
		print(e)
		print("Something went wrong when retrieving price")
		price = "N/A"
	try:	
		request = requests.get("".join(["https://club.jd.com/comment/productCommentSummaries.action?referenceIds=", productID])).json()["CommentsCount"][0]
		goodRate = "".join([str(request["GoodRateShow"]), "%"])
		commentCount = request["CommentCountStr"]
	except JSONDecodeError as e:
		print(e)
		print("Something went wrong when retrieving comments")
		goodRate = "N/A"
		commentCount = "N/A"
	try:
		store = bs.find("div", {"class": "J-hove-wrap EDropdown fr"}).find("a").get_text()
	except AttributeError as e: 
		store = "京东自营"
	productInstance = Product(productID, name, price, goodRate, commentCount, store,time.strftime("%m-%d-%Y %H:%M:%S", time.localtime()), productURL)
	productInstance.print()
	productInstance.save()

def getLinks(websiteUrl):
	global count
	links = []

	# first 30 products
	dataPids = []
	html = urlopen(websiteUrl)
	bs = BeautifulSoup(html, "html.parser", from_encoding="iso-8859-1")
	products = bs.find_all("li", {"class": "gl-item"})
	for product in products:
		dataPids.append(product.attrs["data-pid"])
		link = product.find("div", {"class": "p-img"}).find("a").attrs["href"]
		if link[0:6] != "https:":
			link = "".join(["https:", link])
		links.append(link)
	dataPids = ",".join(dataPids)

	# last 30 products
	headers = {"referer": websiteUrl}
	newRequestUrl = "".join(["https://search.jd.com/s_new.php?keyword=", item, "&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&page=", str(page + 1), "&scrolling=y&log_id=", logId, "&tpl=3_M&show_items=", dataPids])
	req = Request(newRequestUrl, headers = headers)
	html = urlopen(req)
	bs = BeautifulSoup(html, "html.parser")
	products = bs.find_all("li", {"class": "gl-item"})
	for product in products:
		link = product.find("div", {"class": "p-img"}).find("a").attrs["href"]
		if link[0:6] != "https:":
			link = "".join(["https:", link])
		links.append(link)

	return links

item = input("The item you want to know (in Chinese): ")
item = quote(item)
logId = "%.5f" %time.time()
originalLink = "".join(["https://search.jd.com/Search?keyword=", item, "&enc=utf-8&page="])
for i in range (100):
	page = 2 * i + 1
	websiteUrl = "".join([originalLink, str(page)])
	links = getLinks(websiteUrl)
	for link in links:
		getInformation(link)

endTime = time.time()
print("".join(["Time takes to collect data: ", str(endTime - startTime), "s"]))


