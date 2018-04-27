from urllib import request
from csv import writer
import pandas as pd
import qtpy.QtCore
from gui import ScraperWindow
from tkinter.filedialog import *
from PyQt5 import QtWidgets
from bs4 import BeautifulSoup
from qtpy.QtWidgets import QApplication
from WebRender import render
from typing import List


def start_scraping(filename, window):
    if filename != '':
        try:
            with open(filename) as f:

                """"
                we don't want the first row as it contains the link to the google search
                """
                reader = pd.read_csv(f, skiprows=[0], encoding='utf-8')

                """ Declaration of our variables that will contain our text """
                links = reader['result link']

                abstract = []
                description = []
                pdf_link = []
                claims = []

                index = 1  # counter for our displayed patent counter ( ex : [1/3] )

                """ 2 dictionaries which will contain our citations """
                given_citations = {'SOURCE': 'TARGET'}
                received_citations = {'SOURCE': 'TARGET'}

                """
                    In order to scrap information from Google Patents, we need to render the page in a web engine
                    because Google fills the page with JavaScripts scripts, which makes it impossible to scrap from the
                    source code directly.
                    
                    To render the page we use PyQt and their WebEngine (cf WebRender.py)
                
                """

                for i in links:

                    # if i[-3:-2] == '/':
                    # i = i[0:-3]

                    """
                    Fancy console printing
                    """
                    window.set_max_progress_bar(
                        links.size)     # sets our progress bar maximum to the number of links to scrap
                    window.addText(
                        '[' + (str(index) if index >= 10 else '0' + str(index)) + '/'
                        + (str(links.size) if links.size >= 10 else '0' + str(links.size)) + '], link: \t' + i
                    )

                    """ 
                    necessary global instance to avoid garbage collection
                    of the navigator and raising a segmentation error 
                    """

                    global app
                    app = qtpy.QtWidgets.QApplication.instance()

                    if app is None:
                        app = qtpy.QtWidgets.QApplication(sys.argv)

                    r = render(i, app)  # call to our class in WebRender.py
                    app.quit()

                    #############
                    # SCRAPPING #
                    #############

                    soup = BeautifulSoup(r, 'html.parser')

                    ############################
                    # DOWNLOADING THE PDF FILE #
                    ############################

                    found_pdf_link = False  # boolean is true if the pdf has been found
                    """
                        The PDF link is under the class 'style-scope patent-result',
                        and just looks for any link inside these classes
                    """
                    for x in soup.find_all(href=re.compile('https://patentimages.'),
                                           class_='style-scope patent-result'):
                        pdf_link.append(x['href'])
                        url = pdf_link[-1]

                        path = '/home/guillaume/PycharmProjects/Scrapper1.0/PDF/'
                        os.makedirs(os.path.dirname(path), exist_ok=True)  # creates our destination folder

                        window.addText('Downloading pdf ...')
                        request.urlretrieve(url, path + re.split('/', url)[-1])  # downloads our pdf

                        found_pdf_link = True

                    if found_pdf_link is False:
                        pdf_link.append("")

                    #####################
                    # FETCHING ABSTRACT #
                    #####################

                    """
                    IF ABSTRACT IN ENGLISH :
                    
                    Fetching the abstract is easy (if the original text is in english)
                    the class containing it is called 'abstract style-scope patent-text'
                    we just need to scrap the text from it
                    We need to concatenate the different strings to prevent any rupture in the
                    abstract array and causing problems when saving our files.
                    
                    IF TRANSLATED ABSTRACT :
                    
                    The translated boolean indicates if the text has been automatically translated by Google
                    which create 2 <span> as follows:
                    
                        <span class="notranslate style-scope patent-text">
                            <span class="google-src-text style-scope patent-text">
                                ORIGINAL TEXT
                            </span>
                            TRANSLATED TEXT
                        </span>
                        
                    We only want the translated text, the original text is indicated by the google-src-text class
                    which in this case we decided to ignore
                    
                    The same principle has been applied to the other parts of the text (claims and description)
                    
                    """

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
                        abstract.append("")
                    else:
                        abstract.append(out_abstract)

                    ########################
                    # FETCHING DESCRIPTION #
                    ########################

                    """
                    The description is contained into the class named 'description style-scope patent-text'
                    """

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
                        description.append("")
                    else:
                        description.append(out_description)

                    ###################
                    # FETCHING CLAIMS #
                    ###################

                    """
                    class named 'claims style-scope patent-text'
                    """

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
                        claims.append("")
                    else:
                        claims.append(out_claims)

                    ############################
                    # FETCHING GIVEN CITATIONS #
                    ############################

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

                            current_id = reader['id'][index - 1]  # gets the id of the current patent

                            # storing the result into the dictionary
                            given_citations.update({current_id: out_givencitations})

                    except AttributeError:  # if there is no citations it will raise an AttributeError exception
                        pass

                    ###############################
                    # FETCHING RECEIVED CITATIONS #
                    ###############################

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

                            current_id = reader['id'][index - 1]  # gets the id of the current patent

                            # storing the result into the dictionary
                            received_citations.update({current_id: out_receivedcitations})
                    except AttributeError:
                        pass

                    index = index + 1
                    window.iterate_progress_bar()  # increase the percentage of the ui progress bar

            f.close()

            ##########################
            # SAVING GIVEN CITATIONS #
            ##########################

            if len(given_citations) != 0:
                with open('given_citations.csv', 'w') as citation_file:

                    write = writer(citation_file)
                    iter_citations = given_citations.items()

                    for citing, value in iter_citations:
                        if citing != 'SOURCE':
                            for cited in value:
                                write.writerow([citing, cited])  # the citing patent is the scraped patent
                        else:
                            write.writerow([citing, value])
                citation_file.close()

            #############################
            # SAVING RECEIVED CITATIONS #
            #############################

            """ The 'SOURCE' column contains the citing patent, the 'TARGET' column the cited patent """
            if len(received_citations) != 0:
                with open('received_citations.csv', 'w') as citation_file:

                    write = writer(citation_file)
                    iter_citations = received_citations.items()

                    for cited, value in iter_citations:
                        if cited != 'SOURCE':
                            for citing in value:
                                write.writerow([citing, cited])  # the cited patent is the scraped patent
                        else:
                            write.writerow([cited, value])
                citation_file.close()

            ###############
            # SAVING DATA #
            ###############

            dataframe = {
                'id': reader['id'],
                'title': reader['title'],
                'assignee': reader['assignee'],
                'inventor/author': reader['inventor/author'],
                'priority date': reader['priority date'],
                'filing/creation date': reader['filing/creation date'],
                'publication date': reader['publication date'],
                'grant date': reader['grant date'],
                # 'representative figure link': reader['representative figure link'],
                'link': links,
                'pdf_link': pdf_link
            }

            """
                saving text in patents into a txt file
                1st : Creating a DataFrame containing all the text from all the patents
                2nd : Creating a folder if it does not already exist
                3rd : Saving the data into txt files, each named with the patent ID
            """

            text = {
                'id': reader['id'],
                'abstract': abstract,
                'description': description,
                'claims': claims
            }

            """
                The line below creates a dataFrame structured as follows :
                
                    abstract / claims / descriptions / id
                0   abstract1 claims1 description1 id1
                1
                2
                ...
            """
            corpus_dataframe = pd.DataFrame(text)

            def save_txt_file(array: List[str], concatenated: bool):
                """
                array is a row in a dataFrame
                concatenated is true if you want all the text in one single file,
                false if you want separate files
                """
                file_names = {
                    0: 'ABSTRACT',
                    1: 'CLAIMS',
                    2: 'DESCRIPTION'
                }

                if concatenated is False:
                    for idx, folder_name in file_names.items():
                        if len(array[idx]) != 0:
                            path_txt = '/home/guillaume/PycharmProjects/Scrapper1.0/TXT/' + folder_name + '/'
                            os.makedirs(os.path.dirname(path_txt), exist_ok=True)

                            with open(path_txt + folder_name + '_' + array[3] + '.txt', 'a') as txt_file:
                                txt_file.write(folder_name + '\n' + array[idx])
                            txt_file.close()
                else:
                    path_txt = '/home/guillaume/PycharmProjects/Scrapper1.0/TXT/'
                    os.makedirs(os.path.dirname(path_txt), exist_ok=True)

                    with open(path_txt + array[3] + '.txt', 'a') as txt_file:
                        for idx, folder_name in file_names.items():
                            if len(array[idx]) != 0:
                                txt_file.write(folder_name + '\n' + array[idx])
                    txt_file.close()

            for row in corpus_dataframe.values:
                save_txt_file(row, True)
                save_txt_file(row, False)

            """ 
                Saving the remaining data to a csv file :
                Structure of the DataFrame :
                
                    assignee ; filing/creation date ; grand date ; id ; inventor/author ; 
                    link ; pdf_link ; priority date ; publication date ; representative figure link ;  title
                0
                1
                2
                ...
            """
            df = pd.DataFrame(data=dataframe)
            df.to_csv('dataFrame.csv', encoding='utf-8', index=False)
            window.job_done()

        except FileNotFoundError:  # if the user chose a non existent file
            window._file_not_found_err()

        except IsADirectoryError:  # if the user chose a directory instead of a file
            window.is_directory_err()
    else:
        window._empty_path_err()  # handles an empty path


if __name__ == "__main__":
    ui = ScraperWindow()
    ui.show()