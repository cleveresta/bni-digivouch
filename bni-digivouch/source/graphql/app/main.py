import graphene, datetime, os
import tinydb
import requests,json
import random
import humps
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from data import db, setup
from string import Template
from collections import OrderedDict

setup()

AYOPOP_CALLBACK_URL = os.getenv("AYOPOP_CALLBACK_URL", "https://93m5f6zo3c.execute-api.ap-southeast-2.amazonaws.com/dev")

class Product(graphene.ObjectType):
    category = graphene.String(default_value="")
    brand = graphene.String(default_value="")
    product_name = graphene.String()
    product_code = graphene.String()
    paid_price_by_customer = graphene.String()
    status = graphene.String()
    host_partner = graphene.String()
    biller_code = graphene.String()
    region_code = graphene.String()
    fee = graphene.String()
    
    def resolve_category(parent, info):
        return parent.category
        

class Message(graphene.ObjectType):
    ID = graphene.String()
    EN = graphene.String()
    
class Data(graphene.ObjectType):
    inquiry_id = graphene.String()
    account_number = graphene.String()
    customer_name = graphene.String()
    product_name = graphene.String()
    product_code = graphene.String()
    category = graphene.String()
    amount = graphene.String()
    total_admin = graphene.String()
    processing_fee = graphene.String()
    denom = graphene.String()
    validity = graphene.String()
    customer_detail = graphene.String()
    bill_details = graphene.String()
    product_details = graphene.String()
    extra_fields = graphene.String()
    ref_number = graphene.String()
    transaction_id = graphene.String()
    token = graphene.String()

class Inquiry(graphene.ObjectType):
    partner_id = graphene.String(default_value="")
    account_number = graphene.String()
    zone_id = graphene.String()
    product_code = graphene.String()
    success = graphene.String()
    response_code = graphene.String()
    message = graphene.Field(Message, ID=graphene.String(), EN=graphene.String())
    data = graphene.Field(Data)
    
class Core(graphene.ObjectType):
    class Meta:
        default_resolver= graphene.types.resolver.dict_resolver
    core_response_code = graphene.String()
    core_response = graphene.String()
    core_message = graphene.String()
    core_journal = graphene.String()

class AyopopPayment(graphene.ObjectType):
    response_code = graphene.String()
    success = graphene.String()
    message = graphene.Field(Message, ID=graphene.String(), EN=graphene.String())
    data = graphene.Field(Data)

class Payment(graphene.ObjectType):
    channel = graphene.String()
    core = graphene.Field(Core)
    host = graphene.Field(AyopopPayment)

class Brandlist(graphene.ObjectType):
    category = graphene.String(default_value="")
    brand = graphene.String(default_value="")

class Status(graphene.ObjectType):
    partner_id = graphene.String()
    ref_number = graphene.String()
    success = graphene.String()
    response_code = graphene.String()
    message = graphene.Field(Message, ID=graphene.String(), EN=graphene.String())
    data = graphene.Field(Data)    

async def reverse_payment(post_data_payment):
    post_data_payment["journalNum"] = post_data_payment["systemJournal"]
    post_data_payment.pop("systemJournal")
    
    reversal_request = requests.post("http://core-payment:8000/reversal", json=post_data_payment)
    print(reversal_request.json())

async def save_payment(post_data_payment):
    save_request = requests.post("http://database-write:8000/db/transaction", json=post_data_payment)
    print(save_request.json())

class Query(graphene.ObjectType):
    digital_product_list = graphene.List(Product, category=graphene.String(default_value="*"), 
    		startIndex=graphene.Int(default_value=0), endIndex=graphene.Int(default_value=1000) )
    digital_product = graphene.Field(Product, productCode=graphene.String())
    total_count = graphene.Int()
    inquiry_ayopop = graphene.Field(Inquiry, partner_id=graphene.String(default_value="*"),
            account_number=graphene.String(), zone_id=graphene.String(),
            product_code=graphene.String())
    product_list_brand = graphene.List(Product, brand=graphene.String(default_value="*"),
            startIndex=graphene.Int(default_value=0), endIndex=graphene.Int(default_value=1000))
    payment_ayopop = graphene.Field(Payment, inquiry_id=graphene.String(), account_number=graphene.String(), 
            product_code=graphene.String(), amount=graphene.String(),  
            partner_id=graphene.String(), buyer_email=graphene.String(), public_buyer_id=graphene.String(), 
            core_account_number=graphene.String(), core_naration=graphene.String(), channel=graphene.String())
    brand_list_category = graphene.List(Brandlist, category=graphene.String(default_value="*"))
    status_ayopop = graphene.Field(Status, partner_id=graphene.String(), ref_number=graphene.String(),
            inquiry_id=graphene.String(), core_account_number=graphene.String(), core_naration=graphene.String(), channel=graphene.String())

    
    def resolve_total_count(self, info):
    	return len(db)
    def resolve_digital_product_list(self, info, category, startIndex, endIndex):
    	produk = tinydb.Query()
    	list_product = []
    	cari = db.all()[startIndex: endIndex] if category=="*" else db.search(produk.Category == category)[startIndex: endIndex]
    	
    	for i in cari:
    		list_product.append(Product(category=i.get("Category"),
    								brand=i.get("Brand"),
    								product_name=i.get("ProductName"),
    								product_code=i.get("ProductCode"),
    								paid_price_by_customer=i.get("PaidPriceByCustomer"),
    								status=i.get("Status"),
                                    host_partner=i.get("HostPartner"),
                                    biller_code=i.get("BillerCode"),
                                    region_code=i.get("RegionCode"),
                                    fee=i.get("Fee")
    								))
    	return list_product
    def resolve_digital_product(self, info, productCode):
    	produk = tinydb.Query()
    	cari = db.search(produk.ProductCode==productCode)
    	if len(cari)==0: return None
    	p = Product(category=cari[0].get("Category"),
    				brand=cari[0].get("Brand"),
    				product_name=cari[0].get("ProductName"),
    				product_code=cari[0].get("ProductCode"),
    				paid_price_by_customer=cari[0].get("PaidPriceByCustomer"),
    				status=cari[0].get("Status"),
                    host_partner=cari[0].get("HostPartner"),
                    biller_code=cari[0].get("BillerCode"),
                    region_code=cari[0].get("RegionCode"),
                    fee=cari[0].get("Fee"))
    	return p
    def resolve_product_list_brand(self, info, brand, startIndex, endIndex):
        produk = tinydb.Query()
        list_product = []
        cari = db.all()[startIndex: endIndex] if brand=="*" else db.search(produk.Brand == brand)[startIndex: endIndex]
        
        for i in cari:
            list_product.append(Product(category=i.get("Category"),
                                    brand=i.get("Brand"),
    								product_name=i.get("ProductName"),
    								product_code=i.get("ProductCode"),
    								paid_price_by_customer=i.get("PaidPriceByCustomer"),
    								status=i.get("Status"),
                                    host_partner=i.get("HostPartner"),
                                    biller_code=i.get("BillerCode"),
                                    region_code=i.get("RegionCode"),
                                    fee=i.get("Fee")
    								))
        return list_product

    def resolve_brand_list_category(self, info, category):
        produk = tinydb.Query()
        list_product =[]
        list_brand =[]
        cari = db.all() if category=="*" else db.search(produk.Category == category)
        
        for i in cari:
            list_product.append(i.get("Brand"))
            
        # import pdb; pdb.set_trace()
        x = list(dict.fromkeys(list_product))
        # y = Brandlist(brand=x)
        for y in x:
            list_brand.append(Brandlist(brand=y))
        return list_brand

    def resolve_inquiry_ayopop(self, info, partner_id, account_number, zone_id, product_code):
        partner = partner_id
        account = account_number
        zone = zone_id
        product = product_code
        payload = """{"partnerId": "${partner}", 
            "accountNumber": "${account}", 
            "zoneId": "${zone}",
            "productCode": "${product}" }"""

        t = Template(payload)
        p = t.substitute(partner=partner, account=account, zone=zone, product=product)
        
        data_payload = json.loads(p)
        
        r = requests.post('http://ayopop-proxy:8080/v1/bill/check', json=data_payload)
        api_response = r.text
        print(r.text)
        
        respond = json.loads(api_response)
        x = respond["data"]
        y = Inquiry(partner_id=partner,
                    account_number=account,
                    zone_id=zone,
                    product_code=product,
                    response_code=respond["responseCode"],
                    success=respond["success"],
                    message=(Message(ID=respond["message"].get("ID"), EN=respond["message"].get("EN"))),
                    data=(Data(inquiry_id=x.get("inquiryId"),
                    account_number=x.get("accountNumber"),
                    customer_name=x.get("customerName"),
                    product_name=x.get("productName"),
                    product_code =x.get("productCode"),
                    category=x.get("category"),
                    amount=x.get("amount"),
                    total_admin=x.get("total_admin"),
                    processing_fee=x.get("processingFee"),
                    denom=x.get("denom"),
                    validity=x.get("validity"),
                    customer_detail=x.get("customerDetail"),
                    bill_details=x.get("billDetails"),
                    product_details=x.get("productDetails"),
                    extra_fields=x.get("extraFields"))))
                    
        return y
    
    def resolve_payment_ayopop(self, info, inquiry_id, account_number, product_code, amount,  
            partner_id, buyer_email, public_buyer_id, core_account_number, core_naration, channel):
        background = info.context["background"]
        systemJournal = random.randint(900000, 999999)
        host_payload = {"inquiryId": int(inquiry_id),
            "accountNumber": account_number,
            "productCode": product_code,
            "amount": int(amount),
            "refNumber": str(systemJournal),
            "partnerId": partner_id,
            "buyerDetails": {
                "buyerEmail": buyer_email,
                "publicBuyerId": public_buyer_id
            },
            "CallbackUrls": [
                AYOPOP_CALLBACK_URL
            ]
        }
        
        core_payload = { 
          "channel": channel,
          "billerCode": "0124",
          "regionCode": "0001",
          "cardNum": account_number,
          "billerName": "AYOPOP",
          "paymentMethod": "2",
          "accountNum": core_account_number,
          "trxAmount": amount,
          "feeAmount": 0,
          "naration": core_naration,
          "invoiceNum": inquiry_id,
          "sign": "1",
          "refNo": "",
          "flag": "Y",
          "amount1": 0,
          "amount2": 0,
          "amount3": 0,
          "amount4": 0,
          "amount5": 0,
          "systemJournal": str(systemJournal),
          "journalNum": ""
        }

        construct_response = { "channel": channel }
        
        core_request = requests.post('http://core-payment:8000/payment', json=core_payload)
        fault_json = core_request.json()
        fault_indicator = fault_json["soapenv:Envelope"]["soapenv:Body"]
        #print (fault_indicator)
        if fault_indicator == {'soapenv:Fault': {'@xmlns:m': 'http://service.bni.co.id/core', 'faultcode': 'm:AppFault', 'faultstring': '0398', 'detail': {'@encodingStyle': '', 'core:transaction_appFault': {'@xmlns:core': 'http://service.bni.co.id/core', 'errorNum': '0398', 'errorDescription': 'DANA TIDAK CUKUP'}}}} :
            print(core_request.json())
            core_response = { "core_response_code": "0266", "core_response": "NG", "core_message": "Dana Tidak Cukup", "core_journal": systemJournal }
            construct_response.update({'core': core_response})
            construct_response = humps.decamelize(construct_response)
            return Payment(**construct_response)
        host_request = requests.post('http://ayopop-proxy:8080/v1/bill/payment', json=host_payload)
        
        
        core_response = { "core_response_code": "", "core_response": "OK", "core_message": "OK", "core_journal": systemJournal }
        
        print(core_request.json())
        host_response = host_request.json()
        construct_response.update({'core': core_response})
        construct_response.update({'host': host_response})
        
        # if host_response["success"] == False:
        #     background.add_task(reverse_payment, post_data_payment=core_payload)

        save_to_db = {
            "inquiry_id": inquiry_id,
            "trx_date": "2021-09-08T00:46:47.129Z",
            "account_num_voucher": account_number,
            "product_code": product_code,
            "transaction_id": host_response["data"]["transactionId"],
            "amount": int(amount),
            "account_num": core_account_number,
            "journal_num": systemJournal,
            "response_code": host_response["responseCode"],
            "response_message": host_response["message"]["ID"]
            }
        
        dbsave = json.dumps(save_to_db)

        background.add_task(save_payment, post_data_payment=json.loads(dbsave))

        construct_response = humps.decamelize(construct_response)
        return Payment(**construct_response)
    
    def resolve_status_ayopop(self, info, partner_id, ref_number, inquiry_id, core_account_number, core_naration, channel):
        prtnr_id = partner_id
        rf_num = ref_number
        response_message = ""
        transaction_id= ""

        payload = """{
                "partnerId": "${prtnr_id}",
                "refNumber": "${rf_num}"
            }"""

        t = Template(payload)
        p = t.substitute(prtnr_id=prtnr_id, rf_num=rf_num,)
        
        data_payload = json.loads(p)

        r = requests.post('http://ayopop-proxy:8080/v1/bill/status', json=data_payload)
        api_response = r.text
        print(r.text)
        
        respond = json.loads(api_response)
        x = respond["data"]
        response_message = respond["message"].get("ID")
        transaction_id= x.get("transactionId")
        y = Status(response_code=respond["responseCode"],
                    success=respond["success"],
                    message=(Message(ID=response_message, EN=respond["message"].get("EN"))),
                    data=(Data(ref_number=x.get("refNumber"),
                    transaction_id = transaction_id,
                    account_number=x.get("accountNumber"),
                    product_name=x.get("productName"),
                    product_code =x.get("productCode"),
                    category=x.get("category"),
                    amount=x.get("amount"),
                    total_admin=x.get("total_admin"),
                    token = x.get("token"),
                    processing_fee=x.get("processingFee"),
                    customer_detail=x.get("customerDetail"),
                    bill_details=x.get("billDetails"),
                    product_details=x.get("productDetails"),
                    extra_fields=x.get("extraFields"))))
        
        core_payload = { 
          "channel": channel,
          "billerCode": "0124",
          "regionCode": "0001",
          "cardNum": x.get("accountNumber"),
          "billerName": "AYOPOP",
          "paymentMethod": "2",
          "accountNum": core_account_number,
          "trxAmount": x.get("amount"),
          "feeAmount": 0,
          "naration": core_naration,
          "invoiceNum": inquiry_id,
          "sign": "1",
          "refNo": "",
          "flag": "Y",
          "amount1": 0,
          "amount2": 0,
          "amount3": 0,
          "amount4": 0,
          "amount5": 0,
          "systemJournal": str(ref_number),
          "journalNum": ""
        }

        if respond["success"] == False:
            core_payload["journalNum"] = core_payload["systemJournal"]
            core_payload.pop("systemJournal")
    
            reversal_request = requests.post("http://core-payment:8000/reversal", json=core_payload)
            print(reversal_request.json())

        update_db = {"response_message": response_message,
            "transaction_id": transaction_id
            }

        save_request = requests.post("http://database-write:8000/db/statusupdate", json=update_db)
        print(save_request.json())

        return y

        
app = FastAPI()
app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query)))
