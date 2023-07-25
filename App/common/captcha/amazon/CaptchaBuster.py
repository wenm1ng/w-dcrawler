import urllib
import os
import requests
from io import BytesIO
from scrapy import Request
from PIL import Image
from collections import defaultdict
from urllib import request as req
from Configs import defaultApp
import urllib.parse

# This way when using the lib for only requests, then it wont raise an error when loading the module.
try:
    from scrapy.exceptions import IgnoreRequest
    from scrapy.http.response.html import HtmlResponse
except ImportError:
    pass

# BeautifulSoup isnt necessary to use the captchabuster class.
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        pass
ROOT = os.path.dirname(os.path.abspath(__file__))
iconset_dir = os.path.dirname(os.path.dirname(ROOT))
import platform
ICON_LOC = defaultApp.rootDir+'/App/common/captcha/amazon/iconset/'
# if platform.system() == 'Windows':

class CaptchaBuster(object):

    def __init__(self, captcha_loc):
        self.original = Image.open(captcha_loc).convert('P')
        self.temp_file = BytesIO()
        self.image_segment_files = [BytesIO() for n in range(6)]
        self.image_segments = []
        self.processed_captcha = Image.new('P', self.original.size, 255)

    @property
    def guess(self):
        self._pre_process_captcha()
        self._crop_partitions()
        return ''.join(self._guess_characters())

    @classmethod
    def from_url(cls, url, session=None):
        """
        Create a CaptchaBuster object from the url of a captcha.
        :param url: URL location of the captcha image
        :param session: requests.Session object. Use if you have an
            already generated session that you want to use instead of
            a default session.
        :type url: str
        :type session: requests.Session
        :return:
        :rtype: CaptchaBuster
        """
        if not session:
            session = requests.Session()
        h = requests.utils.default_headers()
        h['User-Agent'] = session.headers['User-Agent']
        h['Host'] = 'images-na.ssl-images-amazon.com'
        h['Referer'] = 'https://www.amazon.com/errors/validateCaptcha'
        if 'https://' not in url:
            url = url.replace('http', 'https')
        io = BytesIO(session.get(url, headers=h).content)
        return CaptchaBuster(io)

    def _pre_process_captcha(self):
        """
        Scan the original image from top to bottom moving left to right and
            check if the pixel at location is below color value 10. If the pixel
            at location is within the threshold, write the pixel to the temp file.
        """
        for y in range(self.original.size[1]):
            for x in range(self.original.size[0]):
                pixel = self.original.getpixel((x, y))
                if pixel < 10:
                    self.processed_captcha.putpixel((x, y), 0)
        self.processed_captcha.save(self.temp_file, 'gif')

    def _crop_partitions(self):
        """
        Find discrete partitions within the preprocessed captcha
        to find regions containing individual characters. Returns an accumulated
        list of (start, end) coordinates for this region. Partitions are
        calculated based on the existence of characters within the image, as
        determined by surrounding white space.
        :return:
        """
        letters = []
        in_letter = False
        found_letter = False
        start, end = 0, 0

        for y in range(self.processed_captcha.size[0]):
            for x in range(self.processed_captcha.size[1]):
                pixel = self.processed_captcha.getpixel((y, x))
                if not pixel:
                    in_letter = True

            if not found_letter and in_letter:
                found_letter = True
                start = y

            if found_letter and not in_letter:
                found_letter = False
                end = y
                letters.append((start, end))

            in_letter = False

        count = 0
        for start, end in letters:
            crop_box = (start, 0, end, self.processed_captcha.size[1])
            part = self.processed_captcha.crop(crop_box)

            # If the segment of the image is too small to be a letter, ignore
            # the segment
            if part.size[0] < 15:
                pass
            else:
                part.save(self.image_segment_files[count], 'gif')
                self.image_segments.append(part)
                count += 1

    def _guess_characters(self):
        images = self.load_images()
        captcha = []
        for segment in self.image_segments:
            guess = []
            for letter, img_data_list in images.items():
                guess.extend(map(
                    lambda x: (self.relation(x['data'], segment.resize(x['image'].size).getdata()), letter), img_data_list))
            guess = max(guess)
            captcha.append(guess[1])
        return captcha

    @classmethod
    def relation(cls, concordance1, concordance2):
        """

        """
        r = 0
        l = len(concordance1)
        for i in range(l):
            if (not concordance1[i]) and (concordance1[i] == concordance2[i]):
                r += 5
        return r / float(l)


    def load_images(self):
        # logging.getLogger('captchabuster').info('preprocessing images...')
        d = defaultdict(list)
        # for letter in 'abcdefghijklmnopqrstuvwxyz':
        for letter in 'abcefghjklmnprtuxy':
            letter_dir = os.path.join(ICON_LOC, letter)
            for img in os.listdir(letter_dir):
                if img != 'Thumbs.db' and img != '.gitignore':
                    i = Image.open(os.path.join(letter_dir, img))
                    v = i.getdata()
                    d[letter].append({'image': i, 'data': v})
        return d


def crack_from_requests(htmlText,headers,proxies):
    session = requests.Session()
    soup = BeautifulSoup(htmlText)
    form = soup.find('form')

    action = 'https://www.amazon.com' + form.get('action')
    params = {x.get('name'): x.get('value') for x in form.findAll('input')}

    url = form.find('img').get('src')
    cb = CaptchaBuster.from_url(url, session)
    params['field-keywords'] = cb.guess
    url = action + '?' + urllib.parse.urlencode(params)
    resultHtmlText = session.get(url, headers=headers, proxies=proxies)
    print('-------------破解验证码start---------------')
    print(cb.guess)
    print(url)
    print('--------------破解验证码end--------------')
    import random

    with open("D:\www\dcrawler\Logs" + os.sep + str(random.randint(1, 99999999))+"aaaaa2az2222.html", 'w', encoding='utf8') as f:
        f.write(resultHtmlText.text)
    return resultHtmlText.text
