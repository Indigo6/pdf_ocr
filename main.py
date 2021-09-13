from PIL import Image
import pytesseract
import fitz
import time
import re
import os
import requests
import base64
import docx
from docx.oxml.ns import qn
from io import BytesIO

if_image_to_pdf_or_hocr = False


# 用于对输出任务进度中的时间进行格式化
def fmt_time(dtime):
    if dtime <= 0:
        return '0:00.000'
    elif dtime < 60:
        return '0:%02d.%03d' % (int(dtime), int(dtime * 1000) % 1000)
    elif dtime < 3600:
        return '%d:%02d.%03d' % (int(dtime / 60), int(dtime) % 60, int(dtime * 1000) % 1000)
    else:
        return '%d:%02d:%02d.%03d' % (int(dtime / 3600), int((dtime % 3600) / 60), int(dtime) % 60,
                                      int(dtime * 1000) % 1000)


def ocr_baidu(image, words_per_line, access_token):
    img = base64.b64encode(image)
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    params = {"image": img}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        # print(response.json())
        temp_para = ""
        paras = []
        after_para = True
        length = len(response.json()['words_result'])
        for i, tmp in enumerate(response.json()['words_result']):
            words = tmp['words']
            # 排除页码
            if i == length-1 and words.isdigit():
                if temp_para != '':
                    paras.append(temp_para)
                continue
            temp_para = temp_para+words
            # after_para标志解决首行缩进问题
            if after_para:
                if len(words) >= (words_per_line-2):
                    after_para = False
                else:
                    paras.append(temp_para)
                    temp_para = ""
                    after_para = True
            else:
                # 一般段落以句号结束，宁可多分了句号非段位，也不能少分段尾长句
                if len(words) < words_per_line or words.endswith("。"):
                    paras.append(temp_para)
                    temp_para = ""
                    after_para = True
                else:
                    continue
        # print(paras)
        return after_para, paras
        # return response.json
    else:
        return ""


def ocr_tesseract(image, words_per_line):
    byte_stream = BytesIO(image)  # 把请求到的数据转换为Bytes字节流(这样解释不知道对不对，可以参照[廖雪峰](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001431918785710e86a1a120ce04925bae155012c7fc71e000)的教程看一下)
    img = Image.open(byte_stream)
    # boxes = pytesseract.image_to_boxes(img, lang='chi_sim')
    # data = pytesseract.image_to_data(img, lang='chi_sim')
    if if_image_to_pdf_or_hocr:
        pdf = pytesseract.image_to_pdf_or_hocr(img, lang='chi_sim')
        ''' Tesseract 如果 extension 指定为 pdf, 则会将结果存入一个暂时的、路径类似
            "C:\\Users\\14013\\AppData\\Local\\Temp\\tess_q2mhaewx.pdf" 的 pdf
            然后以 'rb' 模式读入'''
        ''' 但是这个 pdf 是双层 pdf， 会同时保留 image 和 识别出来的文字， 不好利用'''
        doc = fitz.open('pdf', pdf)
        # page = doc[0]
        # text_page = page.getTextPage()
        # text = page.getText()
        # links = page.getImageList()
        # print(doc.embeddedFileNames())
        # 返回的是一个 fitz PDF 对象
        return doc
    else:
        string = pytesseract.image_to_string(img, lang='chi_sim')
        paras = []
        temp_para = ""
        after_para = True
        sentences = string.split('\n')
        final_para_ended = True
        length = len(sentences)
        for i, sentence in enumerate(sentences):
            if i == length-1 and sentence.isdigit():
                continue
            temp_para += sentence
            if len(sentence) >= words_per_line:
                if sentence.endswith("。"):
                    paras.append(temp_para)
                    temp_para = ""
                    after_para = True
                else:
                    if i == len(sentences):
                        final_para_ended = False
                    after_para = False
                    continue
            else:
                if after_para and (len(sentence) >= (words_per_line - 2)):
                    if i == len(sentences):
                        final_para_ended = False
                    after_para = False
                    continue
                else:
                    paras.append(temp_para)
                    temp_para = ""
                    after_para = True
        return final_para_ended, paras


def paras2doc(paras, output_doc, doc_name, last_para,
              final_para_ended, last_para_ended):
    for i, para in enumerate(paras):
        if i == 0 and (not last_para_ended):
            para = last_para + para
        if i == (len(paras) - 1):
            if not final_para_ended:
                last_para_ended = False
                last_para = para
                continue
            else:
                last_para_ended = True
        output_doc.add_paragraph(para)
    output_doc.save(doc_name)
    return last_para, last_para_ended


def pdf_ocr(pdf_name, path, method_get_image, words_per_line,
            ocr_method, client_id, client_secret):
    # 打开pdf
    doc = fitz.open(path)
    access_token = None
    if ocr_method == "online":
        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(client_id, client_secret)
        response = requests.get(host)
        if response:
            access_token = response.json()["access_token"]
            print(access_token)
    if if_image_to_pdf_or_hocr:
        doc_name = 'output/'+pdf_name[:-4] + "_output.pdf"
    else:
        doc_name = 'output/'+pdf_name[:-4] + ".docx"

    # 正则式提取图片法
    if method_get_image == '正则式':
        # 使用正则表达式来查找图片
        checkXO = r"/Type(?= */XObject)"
        checkIM = r"/Subtype(?= */Image)"
        # 图片计数
        imgcount = 0
        lenXREF = doc._getXrefLength()

        # 打印PDF的信息
        print("文件名:{}, 页数: {}, 对象: {}".format(path, len(doc), lenXREF - 1))
        # 遍历每一个对象
        for i in range(1, lenXREF):
            # 定义对象字符串
            text = doc._getXrefString(i)
            isXObject = re.search(checkXO, text)
            # 使用正则表达式查看是否是图片
            isImage = re.search(checkIM, text)
            # 如果不是对象也不是图片，则continue
            if not isXObject or not isImage:
                continue
            imgcount += 1
            # 根据索引生成图像
            pix = fitz.Pixmap(doc, i)

        # 根据pdf的路径生成图片的名称
        # new_name = path.replace('\\', '_') + "_img{}.png".format(imgcount)
        # new_name = new_name.replace(':', '')
        # out_image_path = os.path.join(pic_path, new_name)
        # # 如果pix.n<5,可以直接存为PNG
        # if pix.n < 5:
        #     pix.writePNG(out_image_path)
        # # 否则先转换CMYK
        # else:
        #     pix0 = fitz.Pixmap(fitz.csRGB, pix)
        #     pix0.writePNG(out_image_path)
        #     pix0 = None

        image = pix.getImageData()
        ocr_tesseract(image)
        # page = ocr_baidu(image)
        # time.sleep(1)
        # 释放资源
        pix = None
    else:
        if if_image_to_pdf_or_hocr:
            if ocr_method == "online":
                raise ValueError('Unsupported filetype for online\
                                  API: {}'.format('pdf'))
                return
            output_doc = fitz.open()
        else:
            output_doc = docx.Document()
            output_doc.styles['Normal'].font.name = u'等线'
            output_doc.styles['Normal']._element.rPr.rFonts\
                      .set(qn('w:eastAsia'), u'等线')
        time_start = time.time()
        page_count = doc.pageCount
        for pg in range(doc.pageCount):
            elapsed = time.time() - time_start
            eta = (page_count - pg) * elapsed / pg if pg > 0 else 0
            print('[%d/%d] Elapsed: %s, ETA: %s' % (pg+1, page_count,
                                                    fmt_time(elapsed),
                                                    fmt_time(eta)))
            page = doc[pg]
            rotate = int(0)
            # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高4倍的图像。
            zoom_x = 2
            zoom_y = 2
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pix = page.getPixmap(matrix=trans, alpha=False)
            image = pix.getImageData()

            # 这两个标志位解决 pdf 换页有可能不换段的问题
            last_para = ""  # 上一页的最后一段
            last_para_ended = True  # 上一页最后一段是否已结束，还是被分页了

            if ocr_method == "local":
                if if_image_to_pdf_or_hocr:
                    temp_doc = ocr_tesseract(image)
                    output_doc.insertPDF(temp_doc, 0, 0)
                    # output_doc.save(doc_name, incremental=True)
                    output_doc.save(doc_name)
                else:
                    final_para_ended, paras = ocr_tesseract(image,
                                                            words_per_line)
                    args = [paras, output_doc, doc_name, last_para,
                            final_para_ended, last_para_ended]
                    last_para, last_para_ended = paras2doc(*args)
            else:
                final_para_ended, paras = ocr_baidu(image, words_per_line,
                                                    access_token)
                args = [paras, output_doc, doc_name, last_para,
                        final_para_ended, last_para_ended]
                last_para, last_para_ended = paras2doc(*args)
                time.sleep(1)
            # 释放资源
            pix = None


# 测试对于 b'', BytesIO 和 Image.open()的理解
def test_format():
    res = requests.get('http://p1.pstatp.com/list/300x196/pgc-image/152923179745640a81b1fdc.webp', stream=True)  # 获取字节流最好加stream这个参数,原因见requests官方文档

    byte_stream = BytesIO(res.content)  # 把请求到的数据转换为Bytes字节流(这样解释不知道对不对，可以参照[廖雪峰](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001431918785710e86a1a120ce04925bae155012c7fc71e000)的教程看一下)

    roiImg = Image.open(byte_stream)   # Image打开Byte字节流数据
    # roiImg.show()   #  弹出 显示图片
    imgByteArr = BytesIO()     # 创建一个空的Bytes对象

    roiImg.save(imgByteArr, format='PNG') # PNG就是图片格式，我试过换成JPG/jpg都不行

    imgByteArr = imgByteArr.getvalue()   # 这个就是保存的图片字节流

    # 下面这一步只是本地测试， 可以直接把imgByteArr，当成参数上传到七牛云
    with open("./abc.png", "wb") as f:
        f.write(imgByteArr)


if __name__ == '__main__':
    # test_format()
    # pdf所在文件夹路径
    dir_path = "input/"
    # 获取 pdf 中 image 的方法：每一页 还是 正则式检查每一个对象
    image_method = "页面"
    # pdf 中每一行的文字个数，我取的是非段结尾行的文字个数(如36\37\38)的最小值
    words_per_line = 28
    # ocr API：本地的Tesseract 还是 在线的百度
    ocr_method = "local"
    # ocr_method = "online"
    # 百度 API 的 API key 和 Secret key
    client_id = ""
    client_secret = ""
    with open('baidu_keys.txt', mode='r') as f:
        client_id = f.readline().strip()
        client_secret = f.readline().strip()

    g = os.walk(dir_path)
    for path, dir_list, file_list in g:
        for file_name in file_list:
            pdf_path = os.path.join(path, file_name)
            if not pdf_path.endswith('.pdf'):
                continue
            # pic_path = r'./测试/' + file_name
            # # 创建保存图片的文件夹
            # if not os.path.exists('./测试'):
            #     os.mkdir('./测试')
            # if os.path.exists(pic_path):
            #     print("文件夹已存在，请重新创建新文件夹！")
            # else:
            #     os.mkdir(pic_path)
            m = pdf_ocr(file_name, pdf_path, image_method, words_per_line,
                        ocr_method, client_id, client_secret)
