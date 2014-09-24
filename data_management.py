from data_models import cache

politicians = cache.Politicians()
votes = cache.Votes()
legislation = cache.Legislation()
debates = cache.Debates()
agendas = cache.PolicyAgenda()


def delete_all_data():
    politicians.delete_data()
    votes.delete_data()
    legislation.delete_data()
    debates.delete_data()
    agendas.delete_data()

delete_all_data()