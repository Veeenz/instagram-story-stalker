def success(msg, data=''):
    return {'success': True, 'message':msg, 'data':data}

def fail(msg):
    return {'success': False, 'message': msg}