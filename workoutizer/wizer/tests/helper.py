
def get_body(response):
    return response._container[0].decode('UTF-8')
