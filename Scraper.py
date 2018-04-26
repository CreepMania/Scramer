from urllib import request
import pandas as pd
from tkinter.filedialog import *
from bs4 import BeautifulSoup
from WebRender import render
from csv import writer


class Scraper(object):
    index = 0
    patent_list = []

    def __init__(self, sys_app, main_window):
        self.app = sys_app
        self.ui_window = main_window

        try:
            self.csv_file = ReadFile(self.ui_window.get_filepath()).dataframe()
            self.links = self.csv_file['result link']
            self.ui_window.setMaxProgressBar(self.links.size)
        except FileNotFoundError:
            self.ui_window.fileNotFoundErr()
        except IsADirectoryError:
            self.ui_window.isADirectoryErr()

    def _get_next_soup(self):
        if self.index == self.links.size:
            return None
        self.ui_window.add_text(
            '[' + (str(self.index + 1) if self.index >= 10 else '0' + str(self.index + 1)) + '/'
            + (str(self.links.size) if self.links.size >= 10 else '0' + str(self.links.size))
            + '], link: \t' + self.links[self.index]
        )
        soup = BeautifulSoup(render(self.links[self.index], self.app), 'html.parser')
        self.index += 1
        return soup

    def show(self):
        self.ui_window.show()
        while self.ui_window.isVisible():
            self.app.exec_()

    def _get_all_data(self):
        data = pd.DataFrame()
        for patent in self.patent_list:
            data = data.append(patent.get_dataframe())
        return data

    def _write_csv_file(self):
        dataframe = self._get_all_data()
        df = pd.DataFrame(data=dataframe)
        df.to_csv('dataFrame.csv', encoding='utf-8', index=False)

    def scrape(self):
        soup = self._get_next_soup()
        while soup is not None:
            data = {}
            temp = self.csv_file.to_dict()
            for key, value in temp.items():
                value = str(value.get(self.index - 1))
                data[key] = value
            # print(data)
            data['pdf link'] = self.get_pdf_link(soup)
            data['abstract'] = self._get_abstract(soup)
            data['claims'] = self._get_claims(soup)
            data['description'] = self._get_description(soup)
            patent = Patent(data)
            patent.given_citations.get_given_citations(soup)
            patent.received_citations.get_received_citations(soup)
            self.patent_list.append(patent)
            self.ui_window.iterateProgressBar()
            soup = self._get_next_soup()

        for patent in self.patent_list:
            patent.write_txt_files('/home/guillaume/PycharmProjects/Scraper_OOP/TXT/', True)
            patent.write_txt_files('/home/guillaume/PycharmProjects/Scraper_OOP/TXT/', False)
            patent.write_citations('/home/guillaume/PycharmProjects/Scraper_OOP/')

        self._write_csv_file()
        self.ui_window.jobDone()

    def _download_pdf(self, url):
        self.ui_window.add_text('Downloading pdf ...')
        path = '/home/guillaume/PycharmProjects/Scraper_OOP/PDF/'
        os.makedirs(os.path.dirname(path), exist_ok=True)  # creates our destination folder
        request.urlretrieve(url, path + re.split('/', url)[-1])  # downloads our pdf

    def get_pdf_link(self, soup):
        pdf_link = []

        for x in soup.find_all(href=re.compile('https://patentimages.'),
                               class_='style-scope patent-result'):
            pdf_link.append(x['href'])
            url = pdf_link[-1]
            # self._download_pdf(url)
            return url

    @staticmethod
    def _get_abstract(soup):
        found_abstract = False  # boolean is true if an 'abstract' class has been detected
        translated = False  # boolean is true if the text has been translated by Google
        out_abstract = ''  # buffer string to concatenate our scraped strings

        for x in soup.find_all(class_='abstract style-scope patent-text'):
            for y in x.find_all(class_='notranslate style-scope patent-text'):
                for txt in y.find_all(text=True):

                    parent_class = txt.parent['class']

                    if parent_class[0] != 'google-src-text':
                        out_abstract += txt
                        found_abstract = True
                        translated = True

            if translated is False:  # if our text has not been translated we can concatenate
                out_abstract += x.get_text()
                found_abstract = True
        if found_abstract is False:
            return ""
        else:
            return out_abstract

    @staticmethod
    def _get_description(soup):
        translated = False
        found_description = False
        out_description = ''
        for x in soup.find_all(class_='description style-scope patent-text'):
            for y in x.find_all(class_='notranslate style-scope patent-text'):
                for txt in y.find_all(text=True):

                    parent_class = txt.parent['class']

                    if parent_class[0] != 'google-src-text':
                        out_description += txt
                        found_description = True
                        translated = True

            if translated is False:
                out_description += x.get_text()
                found_description = True

        if found_description is False:
            return ""
        else:
            return out_description

    @staticmethod
    def _get_claims(soup):
        """
        class named 'claims style-scope patent-text'
        """
        translated = False
        found_claims = False
        out_claims = ''
        for x in soup.find_all(class_='claims style-scope patent-text'):
            for y in x.find_all(class_='notranslate style-scope patent-text'):
                for txt in y.find_all(text=True):

                    parent_class = txt.parent['class']

                    if parent_class[0] != 'google-src-text':
                        out_claims += txt
                        found_claims = True
                        translated = True

            if translated is False:
                out_claims += x.get_text()
                found_claims = True

        if found_claims is False:
            return ""
        else:
            return out_claims


class Citations:

    def __init__(self, patent_id):
        self.text = {'SOURCE': 'TARGET'}
        self.patent_id = patent_id

    def get_given_citations(self, soup):
        try:
            out_givencitations = []  # buffer array that contains the given citations
            """
            all of them are contained under a title named patentCitations
            here we use a sibling of sibling because the first one is the '\n',
            while the next one is the one we are interested in
            """
            cit = soup.find('h3', id='patentCitations').next_sibling.next_sibling

            if len(cit) != 0:
                # looking for the specific rows that store the ID of the patent

                for x in cit.find_all(attrs={'data-result': re.compile('patent/')}):
                    out_givencitations.append(x.get_text())

                # storing the result into the dictionary
                self.text.update({self.patent_id: out_givencitations})

        except AttributeError:  # if there is no citations it will raise an AttributeError exception
            return None

    def get_received_citations(self, soup):
        try:
            out_receivedcitations = []  # buffer array that contains the received citations

            """
            all of them are contained under a title named citedBy
            here we use a sibling of sibling because the first sibling is the '\n',
            while the next one is the one we are interested in
            """
            cit = soup.find('h3', id='citedBy').next_sibling.next_sibling
            if len(cit) != 0:
                for x in cit.find_all(attrs={'data-result': re.compile('patent/')}):
                    out_receivedcitations.append(x.get_text())

                self.text.update({self.patent_id: out_receivedcitations})

        except AttributeError:
            return None

    def items(self):
        return self.text.items()


class Patent:

    def __init__(self, data):
        self.patent_id = data['id']
        self.link = data['result link']
        self.assignee = data['assignee']
        self.title = data['title']
        self.inventor = data['inventor/author']
        self.priority_date = data['priority date']
        self.publication_date = data['publication date']
        self.creation_date = data['filing/creation date'],
        self.grant_date = data['grant date']
        self.pdf_link = data['pdf link']
        self.abstract = data['abstract']
        self.description = data['description']
        self.claims = data['claims']
        self.given_citations = Citations(self.patent_id)
        self.received_citations = Citations(self.patent_id)

    def claims(self):
        return self.claims

    def description(self):
        return self.description

    def abstract(self):
        return self.abstract

    def all_text(self):
        return {
            'CLAIMS': self.claims,
            'DESCRIPTION': self.description,
            'ABSTRACT': self.abstract
        }

    def get_dataframe(self):
        return pd.DataFrame(
            {
                'id': self.patent_id,
                'title': self.title,
                'assignee': self.assignee,
                'inventor/author': self.inventor,
                'priority date': self.priority_date,
                'filing/creation date': self.creation_date,
                'publication date': self.publication_date,
                'grant date': self.grant_date,
                'link': self.link,
                'pdf link': self.pdf_link
            }
        )

    def write_txt_files(self, path, concatenated):
        text = self.all_text()
        if concatenated is False:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(str(path) + str(self.patent_id) + '.txt', 'a') as txt_file:
                for name, content in text.items():
                    if content:
                        txt_file.write(name + '\n' + content + '\n')
                txt_file.close()
        else:
            for name, content in text.items():
                if content:
                    os.makedirs(os.path.dirname(path + name + '/'), exist_ok=True)
                    with open(str(path) + '/' + str(name) + '/' + str(name) + '_' + str(self.patent_id) + '.txt',
                              'a') as txt_file:
                        txt_file.write(name + '\n' + content + '\n')
                        txt_file.close()

    def write_given_citations(self, path):

        exists = os.path.isfile(path + 'given_citations.csv')
        with open(path + 'given_citations.csv', 'a') as citation_file:

            write = writer(citation_file)
            iter_citations = self.given_citations.items()

            if not exists:
                write.writerow(['SOURCE', 'TARGET'])

            for citing, value in iter_citations:
                if citing != 'SOURCE':
                    for cited in value:
                        write.writerow([citing, cited])  # the citing patent is the scraped patent
        citation_file.close()

    def write_received_citations(self, path):

        exists = os.path.isfile(path + 'received_citations.csv')
        with open(path + 'received_citations.csv', 'a') as citation_file:

            write = writer(citation_file)
            iter_citations = self.received_citations.items()

            if not exists:
                write.writerow(['SOURCE', 'TARGET'])

            for cited, value in iter_citations:
                if cited != 'SOURCE':
                    for citing in value:
                        write.writerow([citing, cited])  # the cited patent is the scraped patent
        citation_file.close()

    def write_citations(self, path):
        self.write_given_citations(path)
        self.write_received_citations(path)


class ReadFile:
    def __init__(self, file_name):
        self.f = open(file_name)
        self.data_frame = pd.read_csv(self.f, skiprows=[0], encoding='utf-8')
        self.f.close()

    def dataframe(self):
        return self.data_frame
