from data_interface import graph
from data_models import models, new_models
import json


graph = graph.Graph_Database()

node_name = 'Awesome Policy'
node_type = 'PolicyAgenda'

policy = 'Health'
category = 'Comprehensive Health Care Reform.'
code = '342'


def article_test():
    dude = models.Article(graph, "Guest blog: Fight the bedroom tax with anger and action")
    for m in dude.mentions():
        print m


def policy_test():
    # awesome = graph.vertices.create(node_type=node_type, node_name=node_name)
    print "* create the node"
    yo = models.PolicyAgenda(policy, category, code, db=graph)
    if yo.policy_exists:
        print yo.policy
        print yo.category
        edges = yo.related_to()
        for e in edges:
            print e, '\n'
            #if e['definition'] != 'None':
            #    decoded = json.loads(e['definition'])
            #    for k, v in decoded.iteritems():
            #        print k, v, '\n'


def new_policy_test():
    yo = new_models.Policy(policy, db=graph)
    if yo.exists:
        print yo.policy
        print ' ->related to:'
        for rel in yo.related_to():
            print rel
        print ' ->categories:'
        for rel in yo.categories():
            print rel


def new_category_test():
    yo = new_models.PolicyCategory(category, db=graph)
    if yo.exists:
        print yo.category
        print ' ->related to:'
        for rel in yo.related_to():
            print rel
        print ' ->policy:'
        for rel in yo.policy():
            print rel


def pos_test():
    yo = models.PolicyAgenda(policy, category, code, db=graph)
    yo.get_pos('Gypsies')
    yo.get_pos('place')


def named_test():
    cam = models.NamedEntity("David Cameron", db=graph)
    print 'associates'
    for ass in cam.is_associated_with():
        print ass
    print 'edges'
    for e in cam.edges:
        print e


def new_named_test():
    cam = new_models.NamedEntity("David Cameron", db=graph)
    print 'represents'
    for rep in cam.represents():
        print rep
    print 'is_member_of'
    for rep in cam.is_member_of():
        print rep
    print 'is_associated_with'
    for rep in cam.is_associated_with():
        print rep
    print 'is_mentioned_in'
    for rep in cam.is_mentioned_in():
        print rep


def term_test():
    tweet = new_models.UniqueTerm("immigration", db=graph)
    print tweet
    print 'associates'
    for ass in tweet.is_associated_with():
        print ass
    print 'mentions'
    for men in tweet.is_mentioned_in():
        print men

# pos_test()
# policy_test()
# new_named_test()
# term_test()
# new_policy_test()
new_named_test()
