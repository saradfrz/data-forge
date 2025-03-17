import requests

# Parameters
url = "https://servicodados.ibge.gov.br/api/v1/pesquisas"


class APIPlayground():
    def __init__(self, url) -> None:
        self.url = url
        
    def get_data(self):
        response = requests.get(self.url)
        self.response = response
        return response
    
    def save_list_to_txt(self, list):
        with open('list.txt', 'w') as f:
            for item in list:
                f.write("%s\n" % item)




if __name__ == "__main__":
    
    api_playground = APIPlayground(url)
    response = api_playground.get_data()
    data = response.json()
    surveys = [survey['nome'] for survey in data]
    api_playground.save_list_to_txt(surveys)
    
    ipca_survey = [survey for survey in data if survey['nome'] == 'Índice Nacional de Preços ao Consumidor Amplo'] 
    print(7)