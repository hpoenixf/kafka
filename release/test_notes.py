#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest
from types import SimpleNamespace

import notes


def _issue(issue_id, summary, type_name="Bug", type_id="1"):
    return SimpleNamespace(
        id=str(issue_id),
        key=f"KAFKA-{issue_id}",
        fields=SimpleNamespace(
            summary=summary,
            issuetype=SimpleNamespace(name=type_name, id=type_id),
        ),
    )


class TestRender(unittest.TestCase):
    def test_render_wraps_each_issue_type_in_a_list(self):
        issues = [
            _issue(3, "Fix a bug"),
            _issue(2, "Improve a feature", "Improvement", "4"),
            _issue(1, "Add a feature", "New Feature", "2"),
        ]

        rendered = notes.render("4.4.0", issues)

        expected = '''<h2>New Feature</h2>
<ul>
<li>[<a href="https://issues.apache.org/jira/browse/KAFKA-1">KAFKA-1</a>] - Add a feature</li>
</ul>
<h2>Improvement</h2>
<ul>
<li>[<a href="https://issues.apache.org/jira/browse/KAFKA-2">KAFKA-2</a>] - Improve a feature</li>
</ul>
<h2>Bug</h2>
<ul>
<li>[<a href="https://issues.apache.org/jira/browse/KAFKA-3">KAFKA-3</a>] - Fix a bug</li>
</ul>'''
        self.assertEqual(expected, rendered[rendered.index("<h2>"):])

    def test_render_escapes_issue_summary(self):
        cases = [
            ("Preserve <String> & fields", "Preserve &lt;String&gt; &amp; fields"),
            ('Preserve "double" and \'single\' quotes',
             "Preserve &quot;double&quot; and &#x27;single&#x27; quotes"),
            ("Preserve &lt;literal&gt;", "Preserve &amp;lt;literal&amp;gt;"),
            ("Preserve Unicode: café", "Preserve Unicode: café"),
        ]
        for summary, escaped in cases:
            with self.subTest(summary=summary):
                rendered = notes.render("4.4.0", [_issue(1, summary)])
                self.assertIn(
                    f'<li>[<a href="https://issues.apache.org/jira/browse/KAFKA-1">KAFKA-1</a>] - {escaped}</li>',
                    rendered,
                )

    def test_render_empty_issues_has_no_lists(self):
        rendered = notes.render("4.4.0", [])

        self.assertIn("Release Notes - Kafka - Version 4.4.0", rendered)
        self.assertNotIn("<ul>", rendered)
        self.assertNotIn("</ul>", rendered)
        self.assertNotIn("<li>", rendered)


if __name__ == "__main__":
    unittest.main()
