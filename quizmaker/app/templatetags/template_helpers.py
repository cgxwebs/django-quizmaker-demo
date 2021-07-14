from random import sample

from django import template


def get_item(dictionary, key):
    return dictionary.get(str(key))


def reshuffle(seq):
    return sample(seq, len(seq))


register = template.Library()
register.filter('get_item', get_item)
register.filter('reshuffle', reshuffle)
