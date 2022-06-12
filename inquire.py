#!/usr/bin/python3
"""
list prompt example
"""
from __future__ import print_function, unicode_literals
from PyInquirer import prompt, Separator
from examples import custom_style_2
questions = [
    {
        'type': 'list',
        'name': 'clips',
        'message': 'Select next clip!',
        'choices': [
            'Creator1: Clip1',
            Separator(),
            'Creator1: Clip1',
            'Creator1: Clip1',
            'Creator1: Clip1',
            'Creator1: Clip1',
        ]
    },
]
for i in range(2):
    answers = prompt(questions, style=custom_style_2)
print(answers)