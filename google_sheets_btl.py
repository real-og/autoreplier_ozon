import gspread
import os
import re
import config_io


link = str(config_io.get_value('SHEET_LINK'))

def strip_leading_digits(s: str) -> str:
    return re.sub(r'^\d+', '', s)


def split_by_semicolon(s: str) -> list[str]:
    parts = s.split(";")
    return parts if len(parts) > 1 else [s]



class WorkSheet:
    def __init__(self, link: str):
        self.link = link
        self.account = gspread.service_account(filename='key.json')
        self.sheet = self.account.open_by_url(self.link).get_worksheet(1)

    def get_data(self):
        return self.sheet.get_all_values()
    
sheet = WorkSheet(link)


def get_recommendations(article):
    data = sheet.get_data()
    recommendations = []
    for row in data:
        if strip_leading_digits(str(article).lower().strip()) == str(row[0]).lower().strip():
            recommendations = row[4].split(";")
            break
    return recommendations