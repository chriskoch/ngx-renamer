#!/usr/bin/env python3

import os

from dotenv import load_dotenv

from modules.openai_titles import OpenAITitles

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

ai = OpenAITitles(openai_api_key, "/usr/src/ngx-renamer/settings.yaml")


def main():
    text = """
                Each of these had some immediate appeal to me. The responses from our
                distinguished panel of commentators have placed them in the proper
                perspective.
                I start the discussion with reason number 10, that almost no one
                understood the ULTA. I have taught the UCC courses in Sales and Sales
                Financing. In many law schools, Sales and Sales Financing are two separate
                courses, each getting three credit hours. That means each course meets a
                minimum of three hours per week over a fourteen-week semester for a total
                of eighty-four class hours. Some schools combine the two topics into one
                four-credit course for a minimum of fifty-six class hours. It is apparent that
                law school faculties believe that it takes upper level law students, under the
                skilled guidance of a law professor, at least fifty-six hours to understand
                these acts. Of course, a prior understanding of the UCC might make it
                easier for a lawyer or law student to figure out the parallel parts of the
                ULTA, but it also might lead to confusion because the provisions are not
                exactly the same. Besides, not every lawyer or law student understands
                Articles 2 and 9 of the UCC, not even if he or she has taken the course(s).
                So a significant obstacle to adoption would be the time and effort required
                for the critical parties (e.g., study committees, legislative staffs, legislators,
                and interested members of the public, such as, potential lobbyists) to figure
                out what these acts would do.
        """
    new_title = ai.generate_title_from_text(text)
    print(f"Generated Title: {new_title}")


if __name__ == "__main__":
    main()
