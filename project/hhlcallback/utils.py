# -*- coding: utf-8 -*-
import holviapi.utils

def get_nordea_payment_reference(member_id, number):
    base = member_id + 1000
    return holviapi.utils.int2fin_reference(int("%s%s" % (base, number)))
