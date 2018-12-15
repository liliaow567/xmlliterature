import re
import pandas as pd
import xml.etree.ElementTree as ET

from multiprocessing import Pool

filedlist = ['PT', 'AU', 'AF', 'TI', 'SO', 'LA', 'DT', 'DE', 'ID', 'AB',
             'C1', 'RP', 'EM', 'FU', 'FX', 'CR', 'NR', 'TC', 'Z9', 'U1',
             'U2', 'PU', 'PI', 'PA', 'SN', 'EI', 'J9', 'JI', 'PD', 'PY',
             'VL', 'BP', 'EP', 'DI', 'PG', 'WC', 'SC', 'GA', 'UT', 'DA', 'ER']

dic = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j', 10: 'k', 11: 'l'}


def record_ext(content):
    result = re.findall("\n(PT .*?\nER)", content, re.S)
    return result


def filed_ext(filed, record):
    ext = re.findall('\n' + filed + ' ((.*\n)*?)' + filedlist[filedlist.index(filed) + 1], record)
    if ext:
        return ext[0][0]
    else:
        return ' '


def get_title(ti):
    return ti.replace('\n', '').replace('   ', ' ')


def get_author(c1, af):
    c1 = c1.replace('   ', '')
    c1 = [re.findall('\[(.*?)\]', c1), re.findall('] (.*)', c1)]
    for c in c1[0]:
        c = re.findall('.+', c.replace('; ', '\n'))
    af = re.findall('.+', af.replace('   ', ''))
    authors = [{au: []} for au in af]
    affiliations = [{dic[i]: c1[1][i]} for i in range(len(c1[1]))]
    for i in range(len(af)):
        for j in range(len(c1[0])):
            if af[i] in c1[0][j]:
                authors[i][af[i]].append(dic[j])
    return authors, affiliations


def get_doi(doi):
    base = "https://doi.org/"
    doi = doi.replace('\n', '')
    return base + doi


def get_abstract(abst):
    abst = re.findall('.+', abst.replace('   ', ''))
    if abst:
        abst[-1] = abst[-1].replace(' (C) 2018 Elsevier B.V. All rights reserved.', '').replace(
            ' (C) 2018 The Authors. Published by Elsevier B.V.', '').replace(' (C) 2018 Published by Elsevier B.V.',
                                                                             '').replace(
            ' (C) 2018 Elsevier B.V. All right reserved.', '')
        return abst
    else:
        return []


def get_abs_html(abst):
    abst = re.findall('.+', abst.replace('   ', ''))
    if abst:
        abst[-1] = abst[-1].replace(' (C) 2018 Elsevier B.V. All rights reserved.', '').replace(
            ' (C) 2018 The Authors. Published by Elsevier B.V.', '').replace(' (C) 2018 Published by Elsevier B.V.',
                                                                             '').replace(
            ' (C) 2018 Elsevier B.V. All right reserved.', '')
        return [[{"nomark": abst[i]}] for i in range(len(abst))]
    else:
        return []


# def get_img(doi):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
#     try:
#         html = requests.get(doi, headers=headers).text
#         art_id = re.findall(
#             "url='\/retrieve\/articleSelectSinglePerm\?Redirect=https\%3A\%2F\%2Fwww.sciencedirect.com\%2Fscience\%2Farticle\%2Fpii\%2F(.*?)\%3Fvia\%253Dihub&amp;key=.*?'",
#             html)[0]
#         src = "https://ars.els-cdn.com/content/image/1-s2.0-" + art_id + "-gr1_lrg.jpg"
#         return src
#     except:
#         return ' '


def get_js(result):
    doi_list = [get_doi(filed_ext("DI", result[i])) for i in range(len(result))]
    pool = Pool()
    src_list = pool.map(get_img, doi_list)
    # src_list = [get_img(doi_list[i]) for i in range(len(result))]

    with open("lite.js", 'w') as f:
        total = ""
        total += 'var data = [\n'
        for i in range(len(result)):
            title = get_title(filed_ext("TI", result[i]))
            authors, affiliations = get_author(filed_ext('C1', result[i]), filed_ext('AF', result[i]))
            abstracts = get_abs_html(filed_ext("AB", result[i]))
            doi = doi_list[i]
            if i == 0:
                one = '{\n"title":"' + title + '",\n"authors":' + str(authors) + ',\n"affiliations":' + str(
                    affiliations) + ',\n"abstract":' + str(abstracts) + ',\n"img":[\n{"src":"' + str(
                    src_list[i]) + '","desc":"FIND THAT","width":400}],\n"article-link":"' + str(
                    doi) + '"}'
            else:
                one = ',\n{\n"title":"' + title + '",\n"authors":' + str(authors) + ',\n"affiliations":' + str(
                    affiliations) + ',\n"abstract":' + str(abstracts) + ',\n"img":[\n{"src":"' + str(
                    src_list[i]) + '","desc":"FIND THAT","width":400}],\n"article-link":"' + str(
                    doi) + '"}'

            total += one
        total += '\n];'
        f.write(total)


def get_xml(result, source):
    doi_list = [get_doi(filed_ext("DI", result[i])) for i in range(len(result))]
    # pool = Pool()
    # src_list = pool.map(get_img, doi_list)

    with open("lite.xml", 'w') as f:
        total = ""
        total += '<?xml version="1.0" encoding="UTF-8"?>\n'
        # total += '<journal>\n<journalvolume>{}</journalvolume>\n'.format(source)
        total += '<journal>\n'
        for i in range(len(result)):
            title = get_title(filed_ext("TI", result[i]))
            title = title.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('>',
                                                                                                      '&gt;').replace(
                '<', '&lt;')
            authors, affiliations = get_author(filed_ext('C1', result[i]), filed_ext('AF', result[i]))
            abstracts = get_abstract(filed_ext("AB", result[i]))
            doi = doi_list[i]
            doi = doi.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('>', '&gt;').replace(
                '<', '&lt;')
            one = '<record prinumber="' + str(
                i) + '">\n\t<number>1</number>\n\t<abshow>1</abshow>\n\t<imagshow>0</imagshow>\n\t<title>' + title + '</title>\n\t<doi>' + doi + '</doi>\n\t<authors>\n'
            for author in authors:
                au_lab = ','.join(list(author.values())[0])
                au_lab = au_lab.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('>',
                                                                                                            '&gt;').replace(
                    '<', '&lt;')
                au_name = list(author.keys())[0]
                au_name = au_name.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('>',
                                                                                                              '&gt;').replace(
                    '<', '&lt;')
                one_au = '\t\t<author><aulab>{}</aulab><auname>{}</auname></author>\n'.format(au_lab, au_name)
                one += one_au
            one += '\t</authors>\n\t<affils>\n'
            for affil in affiliations:
                affil_lab = list(affil.keys())[0]
                affil_lab = affil_lab.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('>',
                                                                                                                  '&gt;').replace(
                    '<', '&lt;')
                affil_name = list(affil.values())[0]
                affil_name = affil_name.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('>',
                                                                                                                    '&gt;').replace(
                    '<', '&lt;')
                one_affil = '\t\t<affil><affillab>{}</affillab><affilname>{}</affilname></affil>\n'.format(affil_lab,
                                                                                                           affil_name)
                one += one_affil
            one += '\t</affils>\n\t<abstracts>\n'
            for abstract in abstracts:
                abstract = abstract.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('>',
                                                                                                                '&gt;').replace(
                    '<', '&lt;')
                one_ab = '\t\t<abstract>\n\t\t<abstractmark><mark>nomark</mark><content>{}</content></abstractmark>\n\t\t</abstract>\n'.format(
                    abstract)
                one += one_ab
            one += '\t</abstracts>\n\t<pics>\n\t\t<pic><iname>myimage</iname><isrc>dataimage/touxiang.jpg</isrc><width>20%</width></pic>\n\t</pics>\n<journalvolume>{}</journalvolume>\n</record>\n'.format(
                source)
            total += one
        total += '</journal>'
        f.write(total)


def get_zaiyao(result):
    all_title = [get_title(filed_ext("TI", result[i])) for i in range(len(result))]
    all_abstract = [get_abstract(filed_ext("AB", result[i])) for i in range(len(result))]

    with open('zaiyao.html', 'w', encoding='utf-8') as f:
        f.write('<DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('<title>abstract</title>\n')
        f.write('<style type="text/css">\n')
        f.write(' * {margin:0; padding:0; text-indent:0; }\n')
        f.write(
            ' h1 { color: black; font-family:Georgia, serif; font-style: normal; font-weight: bold; text-decoration: none; font-size: 14pt; }\n')
        f.write(
            ' p { color: black; font-family:Georgia, serif; font-style: normal; font-weight: normal; text-decoration: none; font-size: 10pt; margin:0pt; }\n')
        f.write(
            ' .s1 { color: black; font-family:宋体; font-style: normal; font-weight: normal; text-decoration: none; font-size: 10pt; }\n')
        f.write(
            ' .s2 { color: black; font-family:黑体, monospace; font-style: normal; font-weight: normal; text-decoration: none; font-size: 14pt; }\n')
        f.write(' li {display: block; }\n')
        f.write(' #l1 {padding-left: 0pt;counter-reset: c1 0; }\n')
        f.write(
            ' #l1> li:before {counter-increment: c1; content: counter(c1, decimal)" "; color: black; font-family:Georgia, serif; font-style: normal; font-weight: bold; text-decoration: none; font-size: 14pt; }\n')
        f.write('</style>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('<ol id="l1">\n')
        for i in range(len(all_title)):
            f.write(
                '<li style="padding-top: 4pt;padding-left: 5pt;text-indent: 0pt;line-height: 16pt;text-align: justify;">')
            f.write('<h1 style="display: inline;"><a name="bookmark0">')
            f.write(all_title[i])
            f.write('</a></h1>')
            for j in range(len(all_abstract[i])):
                f.write(
                    '<p style="padding-top: 7pt;padding-left: 5pt;text-indent: 19pt;line-height: 137%;text-align: justify;">')
                f.write(all_abstract[i][j])
                f.write('</p>')
            f.write('</li>\n')
        f.write('</ol>\n')
        f.write('</body>\n')
        f.write('</html>\n')


def initial(file, title):
    """
    得到初始的lite.xml和acess.xlsx文件
    :param file:
    :return:
    """
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    result = record_ext(content)

    get_xml(result, title)

    keyword = pd.DataFrame(
        [filed_ext('DE', result[i]).replace('\n', '').replace('   ', ' ') for i in range(len(result))],
        columns=['keyword'])
    title = pd.DataFrame([get_title(filed_ext("TI", one_result)) for one_result in result], columns=['title'])
    keyword_plus = pd.DataFrame(
        [filed_ext('ID', result[i]).replace('\n', '').replace('   ', ' ') for i in range(len(result))],
        columns=['keyword_plus'])
    acessment = pd.concat([title, keyword, keyword_plus], axis=1)
    index = pd.DataFrame([i for i in range(len(result))], columns=['index'])
    num = pd.DataFrame([1 for i in range(len(result))], columns=['num'])
    ab = pd.DataFrame([1 for i in range(len(result))], columns=['ab'])
    imag = pd.DataFrame([0 for i in range(len(result))], columns=['imag'])
    imagname = pd.DataFrame(columns=['imagname', 'imagfilename'])
    marker = pd.concat([index, num, ab, imag, imagname], axis=1)
    writer = pd.ExcelWriter('acess.xlsx')
    acessment.to_excel(writer, 'acessment')
    marker.to_excel(writer, 'marker', index=False)
    writer.save()


def change(file):
    """
    修改acess后，重新修改lite.xml,并生成相应的摘要文稿zaiyao.html
    确保该目录下存在lite.xml,acess.xlsx文件
    :param file:
    :return:
    """
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    result = record_ext(content)
    marker = pd.read_excel('acess.xlsx', sheet_name='marker')
    numbers = marker.num
    ab = marker.ab
    image = marker[['index', 'imag', 'imagname', 'imagfilename']]

    # 修改xml
    tree = ET.parse('lite.xml')
    root = tree.getroot()
    records = root.findall('record')
    for i in range(len(records)):
        number = records[i].find('./number')
        number.text = str(numbers[i])
        abshow = records[i].find('./abshow')
        abshow.text = str(ab[i])

        imgshow = records[i].find('./imagshow')
        imgshow.text = str(image.imag[i])
        if image.imag[i] > 0:
            imagname = image.imagname[i]
            imagfilename = image.imagfilename[i]
            imagname = imagname.split('; ')
            imagfilename = imagfilename.split('; ')
            # print(imagname)
            # print(imagfilename)
            pics = records[i].find('./pics')
            pics.clear()
            if len(imagname) != len(imagfilename):
                print('Check the imagname and imagfilename of {}'.format(i))
            for j in range(len(imagname)):
                pic = ET.Element('pic')
                iname = ET.SubElement(pic, 'iname')
                isrc = ET.SubElement(pic, 'isrc')
                width = ET.SubElement(pic, 'width')

                iname.text = imagname[j]
                isrc.text = 'dataimage/' + imagfilename[j]
                width.text = '20%'
                pics.append(pic)
    tree.write('lite.xml')

    # 生成html摘要
    numbers = marker[['index', 'num']]
    numbers = numbers[numbers.num > 0]
    numbers = numbers.sort_values(by=['num'], kind='mergesort')
    order = list(numbers['index'])
    order_result = [result[i] for i in order]
    get_zaiyao(order_result)
