import markdown2


def md_translate(raw_content):
    '''
    Translate markdown string to html
    '''
    return markdown2.markdown(raw_content)