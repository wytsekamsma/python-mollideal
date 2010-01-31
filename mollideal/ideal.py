from urllib import urlopen, urlencode
from urlparse import urljoin
from xml.dom.minidom import parse
from exceptions import Exception

class iDealError(Exception): pass

class iDealAPI:
	def __init__(self, partner_id=None, testmode='false'):
		self.partner_id = partner_id
		self.testmode = testmode

 	def request(self, params):
		url = "https://secure.mollie.nl/xml/ideal?" + urlencode(params)
		data = parse(urlopen(url))
		if data.firstChild.childNodes[1].attributes.has_key('type'):
			if data.firstChild.childNodes[1].attributes['type'].value == "error":
				errorcode = data.firstChild.childNodes[1].getElementsByTagName('errorcode')[0].firstChild.data
				message = data.firstChild.childNodes[1].getElementsByTagName('message')[0].firstChild.data
				raise iDealError, "[Error %s] %s" % (errorcode, message)
		return data
	
	def get_banklist(self):
		raw_banklist = self.request({
			'a':'banklist', 
			'testmode':self.testmode
		})
		banklist = []
		
		for raw_bank in raw_banklist.firstChild.getElementsByTagName("bank"):
			bank_id		= raw_bank.getElementsByTagName("bank_id")[0].firstChild.data
			bank_name 	= raw_bank.getElementsByTagName("bank_name")[0].firstChild.data
			
			bank = (bank_id, bank_name)
			
			banklist.append(bank)
			
		return tuple(bank for bank in banklist)
		
	def request_payment(self, bank_id, description, reporturl, returnurl, amount):
		raw_payment = self.request({
			'a':'fetch', 
			'partnerid':self.partner_id, 
			'description':description, 
			'reporturl':reporturl, 
			'returnurl':returnurl, 
			'amount':amount, 
			'bank_id':bank_id, 
			'testmode':self.testmode
		})
		payment = {}
		
		order = raw_payment.firstChild.getElementsByTagName("order")[0]

		transaction_id 	= order.getElementsByTagName("transaction_id")[0].firstChild.data
		amount 			= order.getElementsByTagName("amount")[0].firstChild.data
		currency		= order.getElementsByTagName("currency")[0].firstChild.data
		url				= order.getElementsByTagName("URL")[0].firstChild.data
		
		payment = {
			'transaction_id':transaction_id,
			'amount':amount,
			'currency':currency,
			'url':url
		}
		
		return payment
	
	def check_payment(self, transaction_id):
		raw_payment = self.request({
			'a':'check', 
			'partnerid':self.partner_id, 
			'testmode':self.testmode, 
			'transaction_id':transaction_id
		})
		
		order = raw_payment.firstChild.getElementsByTagName("order")[0]
		
		transaction_id 	= order.getElementsByTagName("transaction_id")[0].firstChild.data
		amount 			= order.getElementsByTagName("amount")[0].firstChild.data
		currency		= order.getElementsByTagName("currency")[0].firstChild.data
		payed			= order.getElementsByTagName("payed")[0].firstChild.data
		
		if payed == 'true':
			consumer_name	= order.getElementsByTagName("consumer")[0].getElementsByTagName("consumerName")[0].firstChild.data
			consumer_account= order.getElementsByTagName("consumer")[0].getElementsByTagName("consumerAccount")[0].firstChild.data
			consumer_city	= order.getElementsByTagName("consumer")[0].getElementsByTagName("consumerCity")[0].firstChild.data
		else:
			consumer_name 	= None
			consumer_account= None
			consumer_city	= None
		
		transaction = {
			'transaction_id':transaction_id,
			'amount':amount,
			'currency':currency,
			'payed':payed,
			'consumer_name':consumer_name,
			'consumer_account':consumer_account,
			'consumer_city':consumer_city
		}
		
		return transaction
