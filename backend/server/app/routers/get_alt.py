import requests
import pandas
from lxml import etree
from pathlib import Path
import os


class GetAlt(object):
    def __init__(self):
        self._parent_dir = Path(__file__).parent
        self._alt_output_dir = os.path.join(
            self._parent_dir,
            "alts"
        )
        os.makedirs(self._alt_output_dir, exist_ok=True)
        self._total_page = 0
        self._base_url = ""
        self._cls = ""

    def get_response(self, url, cls_path):
        response = requests.get(url)
        response.encoding = 'utf-8'
        content = response.text
        tree = etree.HTML(content)
        alt_list = tree.xpath("//div/div[contains(@class, 'tupian-list')]/div[contains(@class, 'item')]/img/@alt")
        for alt in alt_list:
            with open(cls_path + "/" + f"{alt}.txt", "wt", encoding="utf-8") as f:
                f.write(alt)
                print(f"'{self._cls}'类型的文本已经写入: {cls_path}/{alt}.txt")
        return None

    def main(self):
        cls_path = os.path.join(
            self._alt_output_dir,
            self._cls
        )
        os.makedirs(cls_path, exist_ok=True)
        count = 0
        for i in range(1, self._total_page + 1):
            print(f"正在爬取第{i}页的图片文本标签:\n" + "+" + "-" * 70)
            if i == 1:
                url = self._base_url
                self.get_response(url=url, cls_path=cls_path)
            if i > 1:
                url = self._base_url[:-5] + "_" + str(i) + ".atc_html"
                self.get_response(url=url, cls_path=cls_path)
            count += 1
        print(f"'{self._cls}'类型，总计保存文本数量：{count * 40}个！")
        return None

    @property
    def total_page(self):
        return self._total_page

    @property
    def cls(self):
        return self._cls

    @property
    def base_url(self):
        return self._base_url

    @total_page.setter
    def total_page(self, value):
        self._total_page = value

    @cls.setter
    def cls(self, value):
        self._cls = value

    @base_url.setter
    def base_url(self, value):
        self._base_url = value


get_alt = GetAlt()
get_alt.cls = "风景"
get_alt.base_url = "https://sc.chinaz.com/tupian/fengjing.html"
get_alt.total_page = 200
get_alt.main()
