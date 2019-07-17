import smtplib, ssl, time, requests

smtpServer = "smtp.gmail.com"
port = 587
context = ssl.create_default_context()

senderEmail = input("Type sender email address: ")
receiverEmail = input("Type receiver email address: ")
password = input("".join(["Type password for ", senderEmail, ": "]))
productID = input("Type product ID here: ")

productUrl = "".join(["https://item.jd.com/", productID, ".html"])
originalPrice = requests.get("".join(["https://p.3.cn/prices/mgets?skuIds=J_", productID])).json()[0]["p"]
currentPrice = originalPrice

while float(currentPrice) >= float(originalPrice):
	print("The price has not dropped yet")
	time.sleep(3600)
	currentPrice = requests.get("".join(["https://p.3.cn/prices/mgets?skuIds=J_", productID])).json()[0]["p"]

message = """\
Subject: PRODUCT ON SALE!!!

Product url: %s
Original price:	RMB %s
Current price: RMB %s

GO GET IT NOW""" %(productUrl, originalPrice, currentPrice)

try:
	server = smtplib.SMTP(smtpServer, port)
	server.ehlo()
	server.starttls(context = context)
	server.ehlo()
	server.login(senderEmail, password)
	server.sendmail(senderEmail, receiverEmail, message)
except Exception as e:
	print(e)
finally:
	server.quit()