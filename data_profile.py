from time import strftime
from utils.data_profiler import node_summary as nodes
from utils.data_profiler import document_summary
from utils.data_profiler import network_centrality
from utils.data_profiler import central_nodes


current_time = strftime("%Y-%m-%d %H:%M:%S")
print "\nData Profile"
print current_time
print "---"


def get_profile():
    node_count = nodes.NodeCount()
    node_count.show_counts()
    terms = term_summary.TermSummary(verbose=True)
    terms.get_term_stats()
    #names = np_summary.NounPhraseSummary(verbose=True)
    #names.get_np_stats()
    #documents = document_summary.DocumentsSummary(verbose=False)
    #documents.get_document_stats()
    structure = network_centrality.InOutDegree()
    structure.show_degrees()
    centre = central_nodes.CentralNodes()
    centre.show_nodes()
    #sentence_summary = sentence.SentenceNodes()
    #sentence_summary.show_counts()


get_profile()

