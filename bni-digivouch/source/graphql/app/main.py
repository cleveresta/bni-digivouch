from inspect import CO_ITERABLE_COROUTINE
import graphene, datetime
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from data import db, setup
import tinydb
import requests,json
from string import Template
from kafka import KafkaProducer

setup()

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
    
    
class Payment(graphene.ObjectType):
    inquiry_id = graphene.String()
    account_number = graphene.String()
    product_code = graphene.String()
    amount = graphene.String()
    ref_number = graphene.String()
    partner_id = graphene.String()
    buyer_email = graphene.String()
    public_buyer_id = graphene.String()
    callback_urls = graphene.String()
    success = graphene.String()
    response_code = graphene.String()
    message = graphene.Field(Message, ID=graphene.String(), EN=graphene.String())
    data = graphene.Field(Data)

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
            product_code=graphene.String(), amount=graphene.String(), ref_number=graphene.String(), 
            partner_id=graphene.String(), buyer_email=graphene.String(), public_buyer_id=graphene.String(), 
            callback_urls=graphene.String())
    brand_list_category = graphene.List(Brandlist, category=graphene.String(default_value="*"))
    status_ayopop = graphene.Field(Status, partner_id=graphene.String(), ref_number=graphene.String())
    
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
        
        r = requests.post('http://192.168.65.151:18082/v1/bill/check', json=data_payload)
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
    
    def resolve_payment_ayopop(self, info, inquiry_id, account_number, product_code, amount, ref_number, 
            partner_id, buyer_email, public_buyer_id, callback_urls):
        inq_id = inquiry_id
        acc_num = account_number
        prod_code = product_code
        amnt = amount
        rf_num = ref_number
        prtnr_id = partner_id
        byr_email = buyer_email
        pblc_byr_id = public_buyer_id
        cb_url = callback_urls
         
        payload = """{"inquiryId": ${inq_id},
                "accountNumber": "${acc_num}",
                "productCode": "${prod_code}",
                "amount": ${amnt},
                "refNumber": "${rf_num}",
                "partnerId": "${prtnr_id}",
                "buyerDetails": {
                    "buyerEmail": "${byr_email}",
                    "publicBuyerId": "${pblc_byr_id}"
                },
                "CallbackUrls": [
                    "${cb_url}"
                ]
            }"""
    
        t = Template(payload)
        p = t.substitute(inq_id=inq_id, acc_num=acc_num, prod_code=prod_code, amnt=amnt, rf_num=rf_num,
                    prtnr_id=prtnr_id, byr_email=byr_email, pblc_byr_id=pblc_byr_id, cb_url=cb_url)
        
        data_payload = json.loads(p)

        r = requests.post('http://192.168.65.151:18082/v1/bill/payment', json=data_payload)
        api_response = r.text
        print(r.text)
        
        respond = json.loads(api_response)
        x = respond["data"]
        y = Payment(response_code=respond["responseCode"],
                    success=respond["success"],
                    message=(Message(ID=respond["message"].get("ID"), EN=respond["message"].get("EN"))),
                    data=(Data(ref_number=x.get("refNumber"),
                    transaction_id = x.get("transactionId"),
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

        return y

    def resolve_status_ayopop(self, info, partner_id, ref_number):
        prtnr_id = partner_id
        rf_num = ref_number

        payload = """{
                "partnerId": "${prtnr_id}",
                "refNumber": "${rf_num}"
            }"""
        
        t = Template(payload)
        p = t.substitute(prtnr_id=prtnr_id, rf_num=rf_num,)
        
        data_payload = json.loads(p)

        r = requests.post('http://192.168.65.151:18082/v1/bill/status', json=data_payload)
        api_response = r.text
        print(r.text)
        
        respond = json.loads(api_response)
        x = respond["data"]
        y = Status(response_code=respond["responseCode"],
                    success=respond["success"],
                    message=(Message(ID=respond["message"].get("ID"), EN=respond["message"].get("EN"))),
                    data=(Data(ref_number=x.get("refNumber"),
                    transaction_id = x.get("transactionId"),
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

        return y

        
app = FastAPI()
app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query)))
