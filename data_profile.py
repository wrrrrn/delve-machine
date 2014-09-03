from time import strftime
from data_profile import node_summary as nodes
from data_profile import network_centrality
from data_profile import central_nodes
from data_profile import sentence_summary
from data_profile import document_summary
from data_profile import np_summary
from data_profile import term_summary

current_time = strftime("%Y-%m-%d %H:%M:%S")
print "\nData Profile"
print current_time
print "---"


def get_profile():
    node_count = nodes.NodeCount()
    node_count.show_counts()
    #terms = term_summary.TermSummary(verbose=True)
    #terms.get_term_stats()
    #names = np_summary.NounPhraseSummary(verbose=True)
    #names.get_np_stats()
    #documents = document_summary.DocumentsSummary(verbose=False)
    #documents.get_document_stats()
    #structure = network_centrality.InOutDegree()
    #structure.show_degrees()
    #centre = central_nodes.CentralNodes()
    #centre.show_nodes()
    #sentence_summary = sentence.SentenceNodes()
    #sentence_summary.show_counts()
    #stats = document_metrics.PopulationStatistics(models, text_io, sem=semantic_tools)
    #stats.get_documents()


get_profile()

