# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import print_function, unicode_literals

import pytest

from inspire_query_parser.parser import (And, BooleanQuery, ComplexValue,
                                         EmptyQuery, Expression,
                                         GreaterEqualOp, GreaterThanOp,
                                         InspireKeyword, InvenioKeywordQuery,
                                         LessEqualOp, LessThanOp,
                                         MalformedQueryWords,
                                         NestedKeywordQuery, NotQuery, Or,
                                         ParenthesizedQuery, Query, RangeOp,
                                         SimpleQuery, SimpleRangeValue,
                                         SimpleValue, SimpleValueBooleanQuery,
                                         SpiresKeywordQuery, Statement, Value)
from inspire_query_parser.stateful_pypeg_parser import StatefulParser

# TODO Reformat parentheses around parametrize entries


@pytest.mark.parametrize(
    ['query_str', 'expected_parse_tree'],
    {
        # Find keyword combined with other production rules
        ("FIN author:'ellis'",
         Query(Statement(Expression(SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'),
                                                                    Value(ComplexValue("'ellis'")))))))
         ),
        ('Find author "ellis"',
         Query([Statement(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(ComplexValue('"ellis"'))))))])
         ),
        ("f AU ellis",
         Query([Statement(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))))])
         ),

        # Invenio like search
        ("author:ellis and Ti:boson",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))),
             And(), Statement(Expression(
                 SimpleQuery(InvenioKeywordQuery(InspireKeyword('title'), Value(SimpleValue('boson'))))))))])
         ),
        ("unknown_keyword:'bar'",
         Query([Statement(
             Expression(SimpleQuery(InvenioKeywordQuery('unknown_keyword', Value(ComplexValue(u"'bar'"))))))])
         ),
        ("dotted.keyword:'bar'",
         Query([Statement(
             Expression(SimpleQuery(InvenioKeywordQuery('dotted.keyword', Value(ComplexValue(u"'bar'"))))))])
         ),

        # Boolean operator testing (And/Or)
        ("author ellis and title 'boson'",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))),
             And(), Statement(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(ComplexValue(u"'boson'"))))))))])
         ),
        ("f a appelquist and date 1983",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('appelquist'))))),
             And(), Statement(
                 Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(SimpleValue('1983'))))))))])
         ),
        ("fin a henneaux and citedby a nicolai",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('henneaux'))))),
             And(), Statement(Expression(NestedKeywordQuery('citedby', Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('nicolai'))))))))))])
         ),
        ("au ellis | title 'boson'",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))), Or(),
             Statement(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(ComplexValue(u"'boson'"))))))))])
         ),
        ("-author ellis OR title 'boson'",
         Query([Statement(BooleanQuery(Expression(NotQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))))),
             Or(), Statement(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(ComplexValue(u"'boson'"))))))))])
         ),
        ("author ellis & title 'boson'",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))),
             And(), Statement(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(ComplexValue(u"'boson'"))))))))])
         ),

        # Implicit And
        ("author ellis elastic.keyword:'boson'",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))),
             And(), Statement(
                 Expression(SimpleQuery(InvenioKeywordQuery('elastic.keyword', Value(ComplexValue(u"'boson'"))))))))])
         ),
        ("find cn atlas not tc c",
         Query([Statement(BooleanQuery(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('collaboration'), Value(SimpleValue('atlas'))))), And(),
             Statement(Expression(NotQuery(Expression(SimpleQuery(
                 SpiresKeywordQuery(InspireKeyword('type-code'),
                                    Value(SimpleValue('c'))))))))))])
         ),
        ("author:ellis j title:'boson' reference:M.N.1",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis j'))))),
             And(), Statement(BooleanQuery(Expression(
                 SimpleQuery(InvenioKeywordQuery(InspireKeyword('title'), Value(ComplexValue(u"'boson'"))))), And(),
                 Statement(Expression(SimpleQuery(
                     InvenioKeywordQuery(InspireKeyword('cite'),
                                         Value(SimpleValue('M.N.1'))))))))))])
         ),
        ("author ellis title boson not title higgs",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword(u'author'), Value(SimpleValue(u'ellis'))))),
             And(), Statement(BooleanQuery(
                 Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword(u'title'), Value(SimpleValue(u'boson'))))),
                 And(), Statement(Expression(NotQuery(Expression(
                     SimpleQuery(SpiresKeywordQuery(InspireKeyword(u'title'), Value(SimpleValue(u'higgs'))))))))))))])
         ),
        ("author ellis - title 'boson'",
         Query([Statement(BooleanQuery(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'),
                                                                                 Value(SimpleValue('ellis'))))),
                                       And(),
                                       Statement(Expression(
                                           NotQuery(Expression(SimpleQuery(
                                               SpiresKeywordQuery(InspireKeyword('title'),
                                                                  Value(ComplexValue(u"'boson'"))))))))))])
         ),

        # ##### Boolean operators at terminals level ####
        ('author ellis, j and smith',
         Query([Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(
             SimpleValueBooleanQuery(SimpleValue('ellis, j'), And(), SimpleValue('smith')))))))])
         ),
        ('f author ellis, j and patrignani and j Chin.Phys.',
         Query([Statement(
             BooleanQuery(
                 Expression(SimpleQuery(
                     SpiresKeywordQuery(InspireKeyword('author'), Value(
                         SimpleValueBooleanQuery(SimpleValue('ellis, j'),
                                                 And(),
                                                 SimpleValue('patrignani')))))),
                 And(),
                 Statement(Expression(SimpleQuery(
                     SpiresKeywordQuery(InspireKeyword('journal'), Value(SimpleValue('Chin.Phys.'))))))))])
         ),
        ('f author ellis, j and patrignani and j ellis',
         Query([Statement(BooleanQuery(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(
             SimpleValueBooleanQuery(SimpleValue('ellis, j'), And(), SimpleValue('patrignani')))))), And(), Statement(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('journal'), Value(SimpleValue('ellis'))))))))])
         ),
        ('f author ellis, j and patrignani and j, ellis',
         Query([Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(
             SimpleValueBooleanQuery(SimpleValue('ellis, j'), And(),
                                     SimpleValueBooleanQuery(SimpleValue('patrignani'), And(),
                                                             SimpleValue('j, ellis'))))))))])
         ),

        # Negation
        ("ellis and not title 'boson'",
         Query([Statement(BooleanQuery(Expression(SimpleQuery(Value(SimpleValue('ellis')))), And(), Statement(
             Expression(NotQuery(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(ComplexValue(u"'boson'"))))))))))])
         ),
        ("-title 'boson'",
         Query([Statement(Expression(NotQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(ComplexValue(u"'boson'"))))))))])
         ),

        # Nested expressions
        ('author ellis, j. and (title boson or (author /^xi$/ and title foo))',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis, j.'))))),
             And(), Statement(Expression(ParenthesizedQuery(Statement(BooleanQuery(
                 Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(SimpleValue('boson'))))),
                 Or(), Statement(Expression(ParenthesizedQuery(Statement(BooleanQuery(Expression(
                     SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(ComplexValue('/^xi$/'))))), And(),
                     Statement(Expression(SimpleQuery(
                         SpiresKeywordQuery(
                             InspireKeyword('title'),
                             Value(SimpleValue(
                                 'foo'))))))))))))))))))])
         ),
        ('author ellis, j. and not (title boson or not (author /^xi$/ and title foo))',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis, j.'))))),
             And(), Statement(Expression(NotQuery(Expression(ParenthesizedQuery(Statement(BooleanQuery(
                 Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(SimpleValue('boson'))))),
                 Or(), Statement(Expression(NotQuery(Expression(ParenthesizedQuery(Statement(BooleanQuery(Expression(
                     SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(ComplexValue('/^xi$/'))))), And(),
                     Statement(
                         Expression(
                             SimpleQuery(
                                 SpiresKeywordQuery(
                                     InspireKeyword(
                                         'title'),
                                     Value(
                                         SimpleValue(
                                             'foo'))))))))))))))))))))))])
         ),

        # Metadata search
        ('fulltext:boson and (reference:Ellis or reference "Ellis")',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(InvenioKeywordQuery(InspireKeyword('fulltext'), Value(SimpleValue('boson'))))),
             And(), Statement(Expression(ParenthesizedQuery(Statement(BooleanQuery(
                 Expression(SimpleQuery(InvenioKeywordQuery(InspireKeyword('cite'), Value(SimpleValue('Ellis'))))),
                 Or(), Statement(Expression(SimpleQuery(
                     SpiresKeywordQuery(InspireKeyword('cite'), Value(ComplexValue('"Ellis"')))))))))))))])
         ),
        ('exactauthor:M.Vanderhaeghen.1 and ac: 42',
         Query([Statement(BooleanQuery(Expression(SimpleQuery(
             InvenioKeywordQuery(InspireKeyword('exact-author'), Value(SimpleValue('M.Vanderhaeghen.1'))))), And(),
             Statement(Expression(SimpleQuery(
                 InvenioKeywordQuery(InspireKeyword('author-count'),
                                     Value(SimpleValue('42'))))))))])
         ),

        # Simple phrases
        ('ellis',
         Query([Statement(Expression(SimpleQuery(Value(SimpleValue('ellis')))))])
         ),
        ("'ellis'",
         Query([Statement(Expression(SimpleQuery(Value(ComplexValue(u"'ellis'")))))])
         ),
        (
            'foo and \'bar\'',
            Query([Statement(BooleanQuery(Expression(SimpleQuery(Value(SimpleValue('foo')))), And(),
                                          Statement(Expression(SimpleQuery(Value(ComplexValue("'bar'")))))))])
        ),
        (
            'ellis and smith and "boson"',
            Query([Statement(
                BooleanQuery(
                    Expression(SimpleQuery(Value(
                        SimpleValueBooleanQuery(SimpleValue('ellis'), And(), SimpleValue('smith'))))),
                    And(),
                    Statement(Expression(SimpleQuery(Value(ComplexValue('"boson"')))))))])
        ),
        (
            'ellis and smith "boson"',
            Query([Statement(
                BooleanQuery(
                    Expression(SimpleQuery(Value(
                        SimpleValueBooleanQuery(SimpleValue('ellis'), And(), SimpleValue('smith'))))),
                    And(),
                    Statement(Expression(SimpleQuery(Value(ComplexValue('"boson"')))))))])
        ),

        # Parenthesized keyword query values (working also with SPIRES operators - doesn't on legacy)
        ('author:(title ellis)',
         Query([Statement(Expression(
             SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'), Value(SimpleValue('title ellis'))))))])
         ),
        ('author (pardo, f AND slavich) OR (author:bernreuther and not date:2017)',
         Query([Statement(BooleanQuery(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(
             SimpleValueBooleanQuery(SimpleValue('pardo, f'), And(), SimpleValue('slavich')))))), Or(), Statement(
             Expression(ParenthesizedQuery(Statement(BooleanQuery(Expression(
                 SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'), Value(SimpleValue('bernreuther'))))),
                 And(), Statement(Expression(NotQuery(Expression(
                     SimpleQuery(InvenioKeywordQuery(InspireKeyword('date'), Value(SimpleValue('2017')))))))))))))))])
         ),

        # Non trivial terminals
        ('author smith and j., ellis',
         Query([Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(
             SimpleValueBooleanQuery(SimpleValue('smith'), And(), SimpleValue('j., ellis')))))))])
         ),
        ('find title Alternative the Phase-II upgrade of the ATLAS Inner Detector or na61/shine',
         Query([Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(
             SimpleValueBooleanQuery(SimpleValue('Alternative the Phase-II upgrade of the ATLAS Inner Detector'), Or(),
                                     SimpleValue('na61/shine')))))))])
         ),
        ('find (j phys.rev. and vol d85) or (j phys.rev.lett.,62,1825)',
         Query([Statement(BooleanQuery(Expression(ParenthesizedQuery(Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('journal'), Value(SimpleValue('phys.rev.'))))),
             And(), Statement(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('volume'), Value(SimpleValue('d85')))))))))), Or(),
             Statement(Expression(ParenthesizedQuery(Statement(Expression(SimpleQuery(
                 SpiresKeywordQuery(InspireKeyword('journal'),
                                    Value(SimpleValue('phys.rev.lett.,62,1825')))))))))))])
         ),
        ("title e-10 and -author d'hoker",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(SimpleValue('e-10'))))), And(),
             Statement(Expression(NotQuery(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue("d'hoker"))))))))))])
         ),
        ('a pang，yi and t SU(2)',
         Query([Statement(BooleanQuery(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('pang，yi'))))), And(),
             Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'),
                                                                 Value(SimpleValue(
                                                                     'SU(2)'))))))))])
         ),
        ('t e(+)e(-) or e+e- Colliders',
         Query([Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(
             SimpleValueBooleanQuery(SimpleValue('e(+)e(-)'), Or(), SimpleValue('e+e- Colliders')))))))])
         ),
        ('title: Si-28(p(pol.),n(pol.))',
         Query([Statement(Expression(SimpleQuery(
             InvenioKeywordQuery(InspireKeyword('title'), Value(SimpleValue('Si-28(p(pol.),n(pol.))'))))))])
         ),
        ('t Si28(p→,p→′)Si28(6−,T=1)',
         Query([Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(
             SimpleValue('Si28(p→,p→′)Si28(6−,T=1)'))))))])
         ),
        ('ti C-12(vec-p,vec-n)N-12 (g.s.,1+)',
         Query([Statement(Expression(SimpleQuery(
             SpiresKeywordQuery(InspireKeyword('title'), Value(SimpleValue('C-12(vec-p,vec-n)N-12 (g.s.,1+)'))))))])
         ),

        # Regex
        ('author:/^Ellis, (J|John)$/',
         Query([Statement(Expression(SimpleQuery(
             InvenioKeywordQuery(InspireKeyword('author'), Value(ComplexValue('/^Ellis, (J|John)$/'))))))])
         ),
        ('title:/dense ([^ $]* )?matter/',
         Query([Statement(Expression(SimpleQuery(
             InvenioKeywordQuery(InspireKeyword('title'), Value(ComplexValue('/dense ([^ $]* )?matter/'))))))])
         ),

        # Nestable keywords
        ('referstox:author:s.p.martin.1',
         Query([Statement(Expression(NestedKeywordQuery('referstox', Expression(
             SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'), Value(SimpleValue('s.p.martin.1'))))))))])
         ),
        ('find a parke, s j and refersto author witten',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('parke, s j'))))),
             And(), Statement(Expression(NestedKeywordQuery('refersto', Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('witten'))))))))))])
         ),
        ('citedbyx:author:s.p.martin.1',
         Query([Statement(Expression(NestedKeywordQuery('citedbyx', Expression(
             SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'), Value(SimpleValue('s.p.martin.1'))))))))])
         ),
        ('citedby:author:s.p.martin.1',
         Query([Statement(Expression(NestedKeywordQuery('citedby', Expression(
             SimpleQuery(InvenioKeywordQuery(InspireKeyword('author'), Value(SimpleValue('s.p.martin.1'))))))))])
         ),
        ('-refersto:recid:1374998 and citedby:(A.A.Aguilar.Arevalo.1)',
         Query([Statement(BooleanQuery(Expression(NotQuery(Expression(NestedKeywordQuery('refersto', Expression(
             SimpleQuery(InvenioKeywordQuery(InspireKeyword('recid'), Value(SimpleValue('1374998'))))))))), And(),
                                       Statement(Expression(NestedKeywordQuery('citedby', Expression(
                                           ParenthesizedQuery(Statement(Expression(
                                               SimpleQuery(Value(SimpleValue('A.A.Aguilar.Arevalo.1'))))))))))))])
         ),
        ('citedby:(author A.A.Aguilar.Arevalo.1 and not a ellis)',
         Query([Statement(Expression(NestedKeywordQuery('citedby', Expression(ParenthesizedQuery(Statement(
             BooleanQuery(Expression(SimpleQuery(
                 SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('A.A.Aguilar.Arevalo.1'))))), And(),
                 Statement(Expression(NotQuery(Expression(SimpleQuery(
                     SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis')))))))))))))))])
         ),
        ('citedby:refersto:recid:1432705',
         Query([
             Statement(Expression(
                 NestedKeywordQuery('citedby',
                                    Expression(
                                        NestedKeywordQuery('refersto',
                                                           Expression(
                                                               SimpleQuery(
                                                                   InvenioKeywordQuery(
                                                                       InspireKeyword('recid'),
                                                                       Value(
                                                                           SimpleValue('1432705'))))))))))])
         ),

        # Ranges
        ('d 2015->2017 and cited:1->9',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'),
                                                       Value(RangeOp(SimpleRangeValue('2015'), SimpleRangeValue('2017'))
                                                             )))
                        ), And(),
             Statement(Expression(SimpleQuery(InvenioKeywordQuery(InspireKeyword('topcite'),
                                                                  Value(RangeOp(SimpleRangeValue('1'),
                                                                                SimpleRangeValue('9')))))))))])
         ),

        # Empty query
        ("", Query([EmptyQuery()])),
        ("      ", Query([EmptyQuery()])),

        # G, GE, LT, LE, E queries
        ('date > 2000-10 and < 2000-12',
         Query([Statement(BooleanQuery(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(GreaterThanOp(SimpleValue('2000-10')))))),
             And(), Statement(
                 Expression(SimpleQuery(Value(LessThanOp(SimpleValue('2000-12'))))))))])
         ),
        ('date after 10/2000 and before 2000-12',
         Query([Statement(BooleanQuery(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(GreaterThanOp(SimpleValue('10/2000')))))),
             And(), Statement(
                 Expression(SimpleQuery(Value(LessThanOp(SimpleValue('2000-12'))))))))])
         ),
        ('date >= nov 2000 and d<=2005',
         Query([Statement(BooleanQuery(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(GreaterEqualOp(SimpleValue('nov 2000')))))),
             And(), Statement(Expression(SimpleQuery(
                 SpiresKeywordQuery(InspireKeyword('date'), Value(LessEqualOp(SimpleValue('2005')))))))))])
         ),
        ('date 1978+ + -ac 100+',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(GreaterEqualOp('1978'))))),
             And(), Statement(Expression(NotQuery(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('author-count'), Value(GreaterEqualOp('100'))))))))))])
         ),
        ('f a wimpenny and date = 1987',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('wimpenny'))))),
             And(), Statement(
                 Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(SimpleValue('1987'))))))))])
         ),

        # Date specifiers
        ('date today - 2 and title foo',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(SimpleValue('today - 2'))))),
             And(), Statement(
                 Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(SimpleValue('foo'))))))))])
         ),
        ('date this month author ellis',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(SimpleValue('this month'))))),
             And(), Statement(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('ellis'))))))))])
         ),
        ('date yesterday - 2 - ac 100',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(SimpleValue('yesterday - 2'))))),
             And(), Statement(Expression(NotQuery(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('author-count'), Value(SimpleValue('100'))))))))))])
         ),
        ('date last month - 2 + ac < 50',
         Query([Statement(BooleanQuery(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(SimpleValue('last month - 2'))))), And(),
             Statement(Expression(SimpleQuery(
                 SpiresKeywordQuery(InspireKeyword('author-count'),
                                    Value(LessThanOp(SimpleValue('50')))))))))])
         ),
        ('date this month - 2',
         Query([Statement(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'), Value(SimpleValue('this month - 2'))))))])
         ),
        ('du > yesterday - 2',
         Query([Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date-updated'), Value(
             GreaterThanOp(SimpleValue('yesterday - 2')))))))])
         ),

        # Star queries
        ("find a 'o*aigh' and t \"alge*\" and date >2013",
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(ComplexValue("'o*aigh'"))))),
             And(), Statement(BooleanQuery(Expression(
                 SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(ComplexValue(r'"alge*"'))))), And(),
                 Statement(Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('date'),
                                                                     Value(GreaterThanOp(
                                                                         SimpleValue(
                                                                             '2013')))))))))))])
         ),
        ('a *alge | a alge* | a o*aigh',
         Query([Statement(BooleanQuery(
             Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('*alge'))))), Or(),
             Statement(BooleanQuery(
                 Expression(SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('alge*'))))),
                 Or(), Statement(Expression(
                     SimpleQuery(SpiresKeywordQuery(InspireKeyword('author'), Value(SimpleValue('o*aigh'))))))))))])
         ),

        # Unrecognized queries
        ('title and foo',
         Query([MalformedQueryWords(['title', 'and', 'foo'])])
         ),
        ('title γ-radiation and and',
         Query([Statement(Expression(
             SimpleQuery(SpiresKeywordQuery(InspireKeyword('title'), Value(SimpleValue('\u03b3-radiation')))))),
             MalformedQueryWords(['and', 'and'])])
         )
    }
)
def test_parser_functionality(query_str, expected_parse_tree):
    print("Parsing: " + query_str)
    parser = StatefulParser()
    _, parse_tree = parser.parse(query_str, Query)
    assert parse_tree == expected_parse_tree
