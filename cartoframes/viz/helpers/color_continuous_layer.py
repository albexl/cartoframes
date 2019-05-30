from __future__ import absolute_import

from ..layer import Layer


def color_continuous_layer(source, value, palette='sunset', title=''):
    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(linear(${0}), reverse({1}))'.format(value, palette)
            },
            'line': {
                'color': 'ramp(linear(${0}), reverse({1}))'.format(value, palette)
            },
            'polygon': {
                'color': 'opacity(ramp(linear(${0}), reverse({1})), 0.9)'.format(value, palette)
            }
        },
        popup={
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend={
            'type': {
                'point': 'color-category',
                'line': 'color-category',
                'polygon': 'color-continuous'
            },
            'prop': 'color',
            'title': title or value,
            'description': ''
        }
    )