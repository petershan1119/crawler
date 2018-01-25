def get_tag_attribute(attribute_name, tag_string):
    a_name = attribute_name
    reg = '{}=.*?"(.*?)">'.format(a_name)
    result = re.findall(r'{}'.format(reg), tag_string)
    result2 = list(filter(None, result))
    return result2


def get_tag_attribute(attribute_name, tag_string):
    p_first_tag = re.compile(r'^.*?<.*?>', re.DOTALL)
    first_tag = re.search(p_first_tag, tag_string).group()

    p = re.compile(r'^.*?{attribute_name}="(?P<value>.*?)".*?>'.format(attribute_name=attribute_name), re.DOTALL)
    m = re.search(p, first_tag)
    if m:
        return m.group('value')
    return ''


def get_tag_content(tag_name, tag_string):
    t_name = tag_name
    reg = '<{}\s.*?>(.*?)<'.format(t_name)
    result = re.findall(r'{}'.format(reg), tag_string)
    result2 = list(filter(None, result))
    return result2


source = '''
<div class="first-div">
    <div class="second-div">   
        <span class="span-content">ABCD</span>
    </div>
</div>
'''



def get_tag_content(tag_string):
    p = re.compile(r' ', re.DOTALL)
    m = re.search(p, tag_string)

    if m:
        return get_