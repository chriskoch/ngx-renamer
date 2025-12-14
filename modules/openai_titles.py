from datetime import datetime

from openai import OpenAI
import yaml


class OpenAITitles:
    def __init__(self, openai_api_key, settings_file="settings.yaml") -> None:
        self.__openai = OpenAI(api_key=openai_api_key)
        self.settings = self.__load_settings(settings_file)


    def __load_settings(self, settings_file):
        try:
            with open(settings_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading settings file: {e}")
            return None


    def __ask_chat_gpt(self, content, role="user"):
        try:
            res = self.__openai.chat.completions.create(
                messages=[
                    {
                        "role": role,
                        "content": content,
                    },
                ],
                model= self.settings.get("openai_model", "gpt-4o-mini")
            )
            return res
        except Exception as e:
            print(f"Error generating title from GPT: {e}")
            return None


    def generate_title_from_text(self, text):
        with_date = self.settings.get("with_date", False)
        setting_prompt = self.settings.get("prompt", None)
        if setting_prompt:
            prompt = setting_prompt.get("main", "")

            if with_date:
                current_date = datetime.today().strftime("%Y-%m-%d")
                with_date_prompt = setting_prompt.get("with_date", "")
                with_date_prompt = with_date_prompt.replace("{current_date}", current_date)
                prompt += with_date_prompt
            else:
                prompt += setting_prompt.get("no_date", "")

            prompt += setting_prompt.get("pre_content", "") + text

            prompt += setting_prompt.get("post_content", "")

            result = self.__ask_chat_gpt(prompt)
            return result.choices[0].message.content
        else:
            print("Prompt settings not found.")
            return None
    
