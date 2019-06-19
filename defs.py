# -*- coding: utf-8 -*-
import re
import qrcode
import sys,os 

import json
import requests
from requests.exceptions import (ConnectTimeout, ReadTimeout,
                                 ConnectionError as _ConnectionError)
from six.moves.urllib.parse import urlencode, urlparse
from .const import Const
TIMEOUT = 2

class COMPANYTYPE(Const):
    type1 =('1',u'合资')
    type2 =('2',u'独资')
    type3 =('3',u'国有')
    type4 =('4',u'私营')
    type5 =('5',u'全民所有制')
    type6 =('6',u'集体所有制')
    type7 =('7',u'股份制')
    type8 =('8',u'有限责任')
    type9 =('9',u'其他')

class CHARGETYPE(Const):
    type1 =('1',u'按月计费')
    type2 =('2',u'按次计费')

class POSTTYPE(Const):
    type1 =('1',u'HR岗')
    type2 =('2',u'财务会计岗')
    type3 =('3',u'管理岗')
    type4 =('4',u'行政岗')
    type5 =('5',u'通用岗')
    type6 =('6',u'销售岗')
    type7 =('7',u'客户服务')
    type8 =('8',u'美工设计')
    type9 =('9',u'市场策划')
    type9 =('10',u'销售管理')


class OrderStatus(Const):
    closed = ('closed', u'已关闭')
    unpaid = ('unpaid', u'待支付')
    pending = ('pending', u'待发货')
    unconfirmed = ('unconfirmed', u'待收货')
    unevaluated = ('unevaluated', u'待评价')
    completed = ('completed', u'已完成')

class OrderRequestStatus(Const):
    closed = (-1, 'closed')
    unpaid = (0, 'unpaid')
    pending = (1, 'pending')
    unconfirmed = (2, 'unconfirmed')
    unevaluated = (3, 'unevaluated')
    completed = (4, 'completed')

class OrderResponseStatus(Const):
    closed = ('closed', -1)
    unpaid = ('unpaid', 0)
    pending = ('pending', 1)
    unconfirmed = ('unconfirmed', 2)
    unevaluated = ('unevaluated', 3)
    completed = ('completed', 4)


class BannerStatus(Const):
    visible = (True, u'显示')
    invisible = (False, u'不显示')

class WechatUserRegisterType(Const):
    app = ('app', u'小程序')

class WechatUserStatus(Const):
    default = ('default', u'默认')

class PaymentStatus(Const):
    unpaid = ('unpaid', '未支付')
    success = ('success', '成功')
    fail = ('fail', '失败')



def hump2underline(hunp_str):
    '''
    驼峰形式字符串转成下划线形式
    :param hunp_str: 驼峰形式字符串
    :return: 字母全小写的下划线形式字符串
    '''
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub

def underline2hump(underline_str):
    '''
    下划线形式字符串转成驼峰形式
    :param underline_str: 下划线形式字符串
    :return: 驼峰形式字符串
    '''
    sub = re.sub(r'(_\w)',lambda x:x.group(1)[1].upper(),underline_str)
    return sub

def create_qrcode(Web_url,job_id,create_uid):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    data = Web_url+'/applicant/start/'+str(create_uid)+'/'+str(job_id)+"/phantom"
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    # 保存到的地址
    model_url = os.path.dirname(os.path.realpath(__file__))
    img.save(model_url+'/static/images/qrcode-'+str(job_id)+'.png')

class PrdRequest(object):

    def __init__(self, api):
        self.api = api
        self.host = 'http://39.108.182.91:8080/PRD/'

    def url_for_get(self, path, parameters):
        return self._full_url_with_params(path, parameters)

    def get_request(self, path, **kwargs):
        return self.make_request(self.prepare_request("GET", path, kwargs))

    def post_request(self, path, **kwargs):
        return self.make_request(self.prepare_request("POST", path, kwargs))

    def _full_url_with_params(self, path, params):
        base_query = urlparse(path).query
        other_query = self._query_with_params(params)
        if base_query and other_query:
            return '%s&%s' % (path, other_query)
        elif other_query:
            return '%s?%s' % (path, other_query)
        else:
            return path

    def _query_with_params(self, params):
        params = urlencode(params) if params else ""
        return params

    def _post_body(self, params):
        return urlencode(params)

    def perpare_and_make_request(self, method, path,
                                 params, include_secret=False):
        url, method, body, json_body,  headers = self.prepare_request(
            method, path, params, include_secret)
        return self.make_request(url, method, body, json_body, headers)

    def prepare_request(self, method, path, params=None):
        url = body = None
        headers = {}

        json_body = params.pop('json_body', None)
        if not params.get('files'):
            if method == 'POST':
                body = self._post_body(params)
                headers = {'Content-type': 'application/x-www-form-urlencoded'}
                url = path
            else:
                url = self._full_url_with_params(path, params)
        else:
            url = path

        return url, method, body, json_body, headers

    def make_request(self, url, method="GET"):
        return requests.request(method, url,timeout=TIMEOUT)
 
