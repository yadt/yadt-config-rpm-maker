# coding=utf-8
#
#   yadt-config-rpm-maker
#   Copyright (C) 2011-2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from mock import Mock, patch

from config_rpm_maker.token.cycle import ContainsCyclesException
from config_rpm_maker.token.tokenreplacer import CannotFilterFileException, MissingTokenException, TokenReplacer


class TokenReplacerTest(unittest.TestCase):

    def test_should_return_unmodified_content_when_content_does_not_contain_token(self):
        self.assertEquals("spam", TokenReplacer().filter("spam"))

    def test_should_raise_exception_when_token_to_filter_is_missing(self):
        self.assertRaises(MissingTokenException, TokenReplacer().filter, "@@@NOT_FOUND@@@")

    def _test_should_return_value_of_replaced_token_when_content_is_token_reference_and_token_contains_special_characters(self):
        self.assertEquals("#\\/@$%&", TokenReplacer({"SPAM": "#\\/@$%&"}).filter("@@@SPAM@@@"))

    def test_should_return_value_of_token_when_content_is_single_token(self):
        self.assertEquals("spam", TokenReplacer({"SPAM": "spam"}).filter("@@@SPAM@@@"))

    def test_should_not_replace_token_if_content_contains_invalid_token_reference(self):
        self.assertEquals("@@@SPAM@@", TokenReplacer({"SPAM": "spam"}).filter("@@@SPAM@@"))

    def test_should_return_value_of_token_when_content_has_surrounding_white_spaces(self):
        self.assertEquals("spam", TokenReplacer({"SPAM": " spam\n"}).filter("@@@SPAM@@@"))

    def test_should_return_value_of_two_tokens_when_content_is_double_token(self):
        self.assertEquals("spameggs", TokenReplacer({"SPAM": "spam",
                                                     "EGGS": "eggs"}).filter("@@@SPAM@@@@@@EGGS@@@"))

    def test_should_return_value_of_content_with_replaced_tokens_when_content_is_a_mixture_of_static_text_and_tokens(self):
        self.assertEquals("You should eat more spam and eggs.",
                          TokenReplacer({"SPAM": "spam",
                                         "EGGS": "eggs"}).filter("You should eat more @@@SPAM@@@ and @@@EGGS@@@."))

    def test_should_use_custom_replacer_function(self):
        def custom_replacer_function(token, value):
            return "<%s:%s>" % (token, value)
        self.assertEquals("<spam:eggs>",
                          TokenReplacer({"spam": "eggs"},
                                        custom_replacer_function).filter("@@@spam@@@"))

    def test_should_replace_token_in_token(self):
        self.assertEquals("foo", TokenReplacer({"FOO": "foo", "BAR": "@@@FOO@@@"}).filter("@@@BAR@@@"))

    def test_should_replace_multiple_token_in_token(self):
        self.assertEquals("fooIGNOREfoo", TokenReplacer({"FOO": "foo", "BAR": "@@@FOO@@@", "BAT": "@@@FOO@@@IGNORE@@@BAR@@@"}).filter("@@@BAT@@@"))

    def test_should_determine_token_recursion(self):
        self.assertRaises(ContainsCyclesException, TokenReplacer, {"FOO": "@@@BAR@@@", "BAR": "@@@FOO@@@"})
        self.assertRaises(ContainsCyclesException, TokenReplacer, {"FOO": "@@@BAR@@@", "BAR": "@@@BLO@@@", "BLO": "@@@FOO@@@"})

    @patch('config_rpm_maker.token.tokenreplacer.KEY_MAX_FILE_SIZE')
    @patch('config_rpm_maker.token.tokenreplacer.getsize')
    def test_should_not_filter_file_with_encoding_unknown_8bit(self, mock_get_size, mock_config):

        mock_get_size.return_value = 10
        mock_config.return_value = 20

        mock_token_replacer = Mock(TokenReplacer)
        mock_token_replacer._read_content_from_file.return_value = 'fake binary file content'
        mock_token_replacer._get_file_encoding.return_value = 'unknown-8bit'

        TokenReplacer.filter_file(mock_token_replacer, "binary.file")

        self.assertEqual(0, mock_token_replacer._perform_filtering_on_file.call_count)

    @patch('config_rpm_maker.token.tokenreplacer.KEY_MAX_FILE_SIZE')
    @patch('config_rpm_maker.token.tokenreplacer.getsize')
    def test_raise_exeception_when_file_limit_exceeded(self, mock_get_size, mock_config):

        mock_get_size.return_value = 4000
        mock_config.return_value = 2000

        mock_token_replacer = Mock(TokenReplacer)

        self.assertRaises(CannotFilterFileException, TokenReplacer.filter_file, mock_token_replacer, "binary.file")
