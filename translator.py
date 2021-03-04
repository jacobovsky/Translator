import requests
from bs4 import BeautifulSoup
import os.path
import sys


class UserInterface:

    def __init__(self):
        self.languages = ['Arabic', 'German', 'English',
                          'Spanish', 'French', 'Hebrew',
                          'Japanese', 'Dutch', 'Polish',
                          'Portuguese', 'Romanian', 'Russian',
                          'Turkish']
        self.languages_menu = {i+1: self.languages[i] for i in range(len(self.languages))}
        self.languages_menu[0] = 'All'

    def show_opening_menu(self):
        print("Hello, you're welcome to the translator. Translator supports:")
        for i in range(len(self.languages)):
            print(f"{i+1}. {self.languages[i]}")

    def get_user_word(self, prompt):
        return input(prompt)

    def get_user_language(self, prompt):
        return self.languages_menu[int(input(prompt))]


class Translator:

    def __init__(self, src_language, trl_language, word):
        self.src_language = src_language.lower()
        self.trl_language = trl_language.lower()
        self.word = word
        self.url = f"https://context.reverso.net/translation/{self.src_language}-{self.trl_language}/{self.word}"

    def get_translated_tags(self, output_format='FORMATTED'):
        request = requests.get(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        website = BeautifulSoup(request.content, 'html.parser')
        translated_words = website.find_all('div', id='translations-content')
        if output_format == 'RAW':
            return translated_words
        elif output_format == 'FORMATTED':
            if not translated_words:
                return translated_words
            else:
                translated_words = translated_words[0].text.replace(10*' ', '').split('\n')
                translated_words = [item for item in translated_words if item]
                return translated_words

    def get_examples(self, output_format='FORMATTED'):
        request = requests.get(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        website = BeautifulSoup(request.content, 'html.parser')
        examples = website.find_all('div', class_='example')
        if output_format == 'RAW':
            return examples
        elif output_format == 'FORMATTED':
            formatted_examples = []
            for example in examples:
                formatted_examples.append(example.text.strip().replace('\n\n\n\n\n', '\n').replace(10*' ', ''))
            return formatted_examples

    def show_translated_tags(self, tags, language, amount_of_tags_to_display, write_to_file=False, file_path='translations.txt'):
        # I could move method from class UserInterfase to get rid of those parameters
        print(f'\n{language.capitalize()} Translations:')
        if len(tags) > amount_of_tags_to_display:
            tags = tags[:amount_of_tags_to_display]
            for tag in tags:
                print(tag)
        if write_to_file:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f'\n{language.capitalize()} Translations:\n')
                for tag in tags:
                    f.write(f'{tag}\n')
                f.write('\n')

    def show_translated_examples(self, examples, language, amount_of_examples_to_display, write_to_file=False, file_path='translations.txt'):
        print(f'\n{language.capitalize()} Examples:')
        if len(examples) > amount_of_examples_to_display:
            examples = examples[:amount_of_examples_to_display]
        # counter helps with managing newline breaks
        counter = 0
        for example in examples:
            if counter == 1:
                print()
                counter = 0
            print(example)
            counter += 1

        if write_to_file:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f'{language.capitalize()} Examples:\n')
                counter = 0
                for example in examples:
                    if counter == 1:
                        f.write('\n')
                        counter = 0
                    f.write(f'{example}\n')
                    counter += 1


def prepare_file_if_exist(word_as_file_name):
    if os.path.isfile(f'{word_as_file_name}.txt'):
        with open(f'{word_as_file_name}.txt', 'r+') as f:
            f.truncate(0)


def get_list_of_all_languages_form_web():
    lang_r = requests.get("https://www.loc.gov/standards/iso639-2/php/code_list.php", headers={'User-Agent': 'Mozilla/5.0'})
    lang_page = BeautifulSoup(lang_r.content, 'html.parser')
    table_content = lang_page.find_all('tr', valign='top')
    list_of_table_content = []
    for content in table_content:
        list_of_table_content.append(content.text)
    list_of_table_content = list_of_table_content[1:]
    names_of_languages = []
    for content in list_of_table_content:
        row = content.split('\n')
        names_of_languages.append(row[3])
    return names_of_languages


if __name__ == "__main__":
    interface = UserInterface()
    args = sys.argv
    src_lang, trl_lang, word_to_translate = [arg for arg in args[1:]]
    list_of_languages = []
    try:
        list_of_languages = get_list_of_all_languages_form_web()
    except ConnectionError:
        print("Something wrong with your internet connection")
    finally:
        # check if selected language exists and if so, it checks if is supported
        if src_lang.capitalize() not in interface.languages:
            if src_lang.capitalize() in list_of_languages:
                print("Sorry, the program doesn't support {}".format(src_lang))
                sys.exit()
        elif trl_lang.capitalize() not in interface.languages:
            if trl_lang.capitalize() in list_of_languages:
                print("Sorry, the program doesn't support {}".format(trl_lang))
                sys.exit()
        # check if word is translatable
        translator = Translator(src_lang, trl_lang, word_to_translate)
        if not translator.get_translated_tags():
            print("Sorry, unable to find {}".format(word_to_translate))

    # if user chooses to translate word in all available languages
    if trl_lang == 'all':
        prepare_file_if_exist(word_to_translate)
        amount_to_show = 1
        interface.languages.remove(src_lang.capitalize())
        for language in interface.languages:
            translator = Translator(src_lang, language, word_to_translate)
            translated_tags = translator.get_translated_tags()
            translator.show_translated_tags(translated_tags, language, amount_to_show, True, f'{word_to_translate}.txt')
            translated_examples = translator.get_examples()
            translator.show_translated_examples(translated_examples, language, amount_to_show, True, f'{word_to_translate}.txt')
    else:
        prepare_file_if_exist(word_to_translate)
        amount_to_show = 5
        translator = Translator(src_lang, trl_lang, word_to_translate)
        # redundant parameters. It could be avoided by moving 'get_user_word()' and 'get_user_lang()' to class Translator
        translated_tags = translator.get_translated_tags()
        translator.show_translated_tags(translated_tags, trl_lang, amount_to_show, True, f'{word_to_translate}.txt')
        translated_examples = translator.get_examples()
        translator.show_translated_examples(translated_examples, trl_lang, amount_to_show, True, f'{word_to_translate}.txt')
