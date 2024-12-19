from googletrans import Translator as trans
import os, json


translator = trans()

class Translator:
    def translate(self, text, dest, cache: bool = True):
        try:
            lang_path = os.path.join(os.getcwd(), "database", "languages.json")
            os.makedirs(os.path.dirname(lang_path), exist_ok=True)
            with open(lang_path, "r") as f:
                languages = json.load(f)
            return languages[text][dest]
        except KeyError:
            if cache:

                languages[text] = {}
                languages[text][dest] = translator.translate(text, dest=dest).text
                with open(lang_path, "w") as f:
                    json.dump(languages, f, indent=4)
                return languages[text][dest]
            else:
                return translator.translate(text, dest=dest).text