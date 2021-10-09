import os
import requests
import xmltodict
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from enum import Enum
from string import Template

CORESERVICE_URL = os.getenv("CORESERVICE_URL", "http://192.168.151.220:57004/CoreService")

class ChannelConfig(Enum):
    NEWIBANK      = {"id": "", "branch":"0996", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    SMS           = {"id": "", "branch":"0992", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    BNIDIRECT     = {"id": "", "branch":"0989", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    ATM           = {"id": "", "branch":"0997", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    MINI_ATM      = {"id": "", "branch":"0997", "teller":"00004", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    AGENT		  = {"id": "", "branch":"0985", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    MOBILE    	  = {"id": "", "branch":"0996", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    NEWMOBILE     = {"id": "", "branch":"0991", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }
    API		      = {"id": "", "branch":"0986", "teller":"00001", "terminal": "1", "overrideFlag":"I", "tandemFlag":"0" }

class XSIType(Enum):
    PAYMENT = 1
    REVERSAL = 2

class PaymentBase(BaseModel):
    channel:    str = Query(None, regex="^NEWIBANK|SMS|BNIDIRECT|ATM|MINI_ATM|AGENT|MOBILE|NEWMOBILE|API$")
    billerCode: str
    regionCode: str
    cardNum:    str
    billerName: str
    cardNum:    str
    paymentMethod: Optional[str] = "2"
    accountNum: str
    trxAmount: int = 0
    feeAmount: Optional[int] = 0
    naration: str
    invoiceNum: str
    sign: Optional[str] = "1"
    refNo: Optional[str] = ""
    flag: Optional[str] = "Y"
    amount1: Optional[int] = 0
    amount2: Optional[int] = 0
    amount3: Optional[int] = 0
    amount4: Optional[int] = 0
    amount5: Optional[int] = 0

class BillingPayment(PaymentBase):
    systemJournal: Optional[str] = ""
    journalNum: Optional[str] = ""
    
class BillingReversal(PaymentBase):
    journalNum: str

post_data_template = """<soapenv:Envelope xmlns:q0="http://service.bni.co.id/core" xmlns:bo="http://service.bni.co.id/core/bo" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soapenv:Body>
        <q0:transaction>
            <request>
                <systemId>MHP</systemId>
                <customHeader>
                    <branch>${branch}</branch>
                    <terminal>${terminal}</terminal>
                    <teller>${teller}</teller>
                    <overrideFlag>I</overrideFlag>
                    <supervisorId/>
                    <systemJournal>${systemJournal}</systemJournal>                                  
                </customHeader>
                <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="bo:BillingPaymentReq">
                    <billerCode>${billerCode}</billerCode>
                    <regionCode>${regionCode}</regionCode>
                    <billerName>${billerName}</billerName>
                    <cardNum>${cardNum}</cardNum>
                    <cardName>${billerName}</cardName>
                    <paymentMethod>${paymentMethod}</paymentMethod>
                    <accountNum>${accountNum}</accountNum>
                    <trxAmount>${trxAmount}</trxAmount>
                    <feeAmount>${feeAmount}</feeAmount>
                    <naration>${naration}</naration>
                    <invoiceNum>${invoiceNum}</invoiceNum>
                    <journalNum>${journalNum}</journalNum>
                    <sign>${sign}</sign>
                    <refNo>${refNo}</refNo>
                    <flag>${flag}</flag>
                    <amount1>${amount1}</amount1>
                    <amount2>${amount2}</amount2>
                    <amount3>${amount3}</amount3>
                    <amount4>${amount4}</amount4>
                    <amount5>${amount5}</amount5>                                  
                </content>                          
            </request>                  
        </q0:transaction>          
    </soapenv:Body>  
</soapenv:Envelope>
"""

post_data_reversal_template = """<soapenv:Envelope xmlns:q0="http://service.bni.co.id/core" xmlns:bo="http://service.bni.co.id/core/bo" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soapenv:Body>
        <q0:transaction>
            <request>
                <systemId>MHP</systemId>
                <customHeader>
                    <branch>${branch}</branch>
                    <terminal>${terminal}</terminal>
                    <teller>${teller}</teller>
                    <overrideFlag>I</overrideFlag>
                </customHeader>
                <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="bo:BillingPaymentReversalReq">
                    <billerCode>${billerCode}</billerCode>
                    <regionCode>${regionCode}</regionCode>
                    <billerName>${billerName}</billerName>
                    <cardNum>${cardNum}</cardNum>
                    <cardName>${billerName}</cardName>
                    <paymentMethod>${paymentMethod}</paymentMethod>
                    <accountNum>${accountNum}</accountNum>
                    <trxAmount>${trxAmount}</trxAmount>
                    <feeAmount>${feeAmount}</feeAmount>
                    <naration>${naration}</naration>
                    <invoiceNum>${invoiceNum}</invoiceNum>
                    <journalNum>${journalNum}</journalNum>
                    <sign>${sign}</sign>
                    <refNo>${refNo}</refNo>
                    <flag>${flag}</flag>
                    <amount1>${amount1}</amount1>
                    <amount2>${amount2}</amount2>
                    <amount3>${amount3}</amount3>
                    <amount4>${amount4}</amount4>
                    <amount5>${amount5}</amount5>                                  
                </content>                          
            </request>                  
        </q0:transaction>          
    </soapenv:Body>  
</soapenv:Envelope>
"""

def construct_request(xsitype, billing):
    if xsitype is XSIType.PAYMENT:
        t = Template(post_data_template)
        replacement = ChannelConfig[billing.channel].value
        replacement.update(dict(billing))
        return t.safe_substitute(**replacement)
    elif xsitype is XSIType.REVERSAL:
        t = Template(post_data_reversal_template)
        replacement = ChannelConfig[billing.channel].value
        replacement.update(dict(billing))
        return t.safe_substitute(**replacement)
    else:
        return None

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
    
@app.post("/payment")
def payment(billing: BillingPayment):
    post_data = construct_request(XSIType.PAYMENT, billing)
    print(post_data)
    req = requests.post(CORESERVICE_URL, data=post_data, headers={'Content-Type': 'application/xml'})
    assert req.status_code == 200
    return xmltodict.parse(req.text)

@app.post("/reversal")
def reversal(reverse: BillingReversal):
    post_data = construct_request(XSIType.REVERSAL, reverse)
    req = requests.post(CORESERVICE_URL, data=post_data, headers={'Content-Type': 'application/xml'})
    assert req.status_code == 200
    return xmltodict.parse(req.text)
