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

import os
import shutil
import struct
import tempfile
import unittest

from config_rpm_maker.token.tokenreplacer import (CannotFilterFileException,
                                                  MissingTokenException,
                                                  MissingOrRedundantTokenException,
                                                  TokenReplacer)


def file_mode(mode, binary):
    result = mode
    if binary:
        result += "b"
    return result


def normalize_pathname(string_or_tuple):
    if isinstance(string_or_tuple, tuple):
        return os.path.join(*string_or_tuple)
    else:
        return string_or_tuple


class IntegrationTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp_directory = tempfile.mkdtemp(prefix=self.__class__.__name__ + "_")

    def tearDown(self):
        if self.tmp_directory is not None:
            shutil.rmtree(self.tmp_directory)

    def create_tmp_dir(self, name):
        os.mkdir(os.path.join(self.tmp_directory, normalize_pathname(name)))

    def create_tmp_file(self, filename, content, binary=False):
        with open(os.path.join(self.tmp_directory, normalize_pathname(filename)), file_mode("w", binary)) as file:
            file.write(content)

    def tmp_file_name(self, filename):
        return os.path.join(self.tmp_directory, filename)

    def abspath(self, pathname):
        return os.path.abspath(os.path.join(self.tmp_directory,
                                            normalize_pathname(pathname)))

    def ensure_file_contents(self, filename, contents, binary=False):
        with open(os.path.join(self.tmp_directory, normalize_pathname(filename)),
                  file_mode("r", binary)) as file:
            actual = file.read()
            if not binary:
                failure_message = "Contents of file %s does not match: Expected '%s' but got '%s'." % (filename, contents, actual)
            else:
                failure_message = "Contents of binary file %s does not match: Expected %d bytes but got %d bytes." % (filename, len(contents), len(actual))

            self.assertEquals(contents, actual, failure_message)


class TokenReplacerFromDirectoryTest(IntegrationTestBase):
    def test_should_return_token_replacer_for_existing_directory(self):
        self.create_tmp_file("SPAM", "spam")
        self.create_tmp_file("EGGS", "eggs")

        token_replacer = TokenReplacer.from_directory(self.tmp_directory)

        self.assertEquals({'SPAM': 'spam', 'EGGS': 'eggs'},
                          token_replacer.token_values)

    def test_should_strip_whitespaces_and_newlines_from_token_files(self):
        self.create_tmp_file("SPAM", " spam")
        self.create_tmp_file("EGGS", "eggs\n")

        token_replacer = TokenReplacer.from_directory(self.tmp_directory)

        self.assertEquals({'SPAM': 'spam', 'EGGS': 'eggs'}, token_replacer.token_values)


class TokenReplacerFilterFileTest(IntegrationTestBase):
    def test_ensure_that_file_without_tokens_is_not_modified_when_filter_is_called(self):
        self.create_tmp_file("spam", "eggs")

        TokenReplacer().filter_file(self.tmp_file_name("spam"))

        self.ensure_file_contents("spam", "eggs")

    def test_ensure_that_file_with_single_token_is_modified_when_filter_is_called(self):
        self.create_tmp_file("spam", "@@@spam@@@")

        TokenReplacer({"spam": "eggs"}).filter_file(self.tmp_file_name("spam"))

        self.ensure_file_contents("spam", "eggs")

    def test_should_raise_exception_containing_file_name_when_encountering_missing_token(self):
        self.create_tmp_file("spam", "@@@spam@@@")

        try:
            TokenReplacer().filter_file(self.tmp_file_name("spam"))
            self.fail("Expected MissingTokenException")
        except MissingTokenException as e:
            self.assertEquals("spam", e.token)
            self.assertTrue(e.file.endswith("spam"))

    def test_ensure_that_binary_file_is_not_modified(self):
        binary_data = ""
        for num in range(50):
            binary_data += struct.pack("i", num)

        self.create_tmp_file("bin", binary_data, True)

        TokenReplacer().filter_file(self.tmp_file_name("bin"))

        self.ensure_file_contents("bin", binary_data, True)

    def test_filter_throw_exception_for_files_bigger_than_file_size_limit(self):
        big_content = "x" * (200 * 1024)
        self.create_tmp_file("big_content", big_content)
        self.assertRaises(Exception, TokenReplacer().filter_file, self.tmp_file_name("big_content"))

    def test_html_escaping(self):
        def html_token_replacer(token, replacement):
            filtered_replacement = replacement.rstrip()
            return '<strong title="%s">%s</strong>' % (token, filtered_replacement)

        self.create_tmp_file("spam", '<a href="link?param1=1&param2=2">@@@spam@@@</a>')
        TokenReplacer(token_values={'spam': 'spam'}, replacer_function=html_token_replacer).filter_file(self.tmp_file_name("spam"), html_escape=True)
        self.ensure_file_contents("spam", '<!DOCTYPE html><html><head><title>spam</title></head><body><pre>&lt;a href=&quot;link?param1=1&amp;param2=2&quot;&gt;<strong title="spam">spam</strong>&lt;/a&gt;</pre></body></html>')

    def test_should_html_escape_file_with_special_characters(self):
        path = os.path.join(self.tmp_directory, 'file-with-special-character')
        shutil.copyfile('testdata/svn_repo/config/typ/web/data/file-with-special-character', path)
        TokenReplacer(token_values={'RPM_REQUIRES': 'äöß234'}).filter_file(path, html_escape=True)

    def test_should_raise_CannotFilterFileException(self):
        self.assertRaises(CannotFilterFileException, TokenReplacer().filter_file, "this-file-does-not-exist.txt")

    def test_should_raise_MissingOrRedundantTokenException(self):
        self.assertRaises(MissingOrRedundantTokenException, TokenReplacer, token_values={'RPM_REQUIRES': '@@@RPM_REQUIRES@@@'})


class TokenReplacerFilterDirectory(IntegrationTestBase):
    def test_should_filter_directory(self):
        self.create_tmp_dir("VARIABLES.localhost")
        self.create_tmp_file(("VARIABLES.localhost", "SPAM"), "spam")
        self.create_tmp_file(("VARIABLES.localhost", "EGGS"), "eggs")
        self.create_tmp_file(("VARIABLES.localhost", "HAM"), "ham")

        self.create_tmp_dir("yadt-config-localhost")

        self.create_tmp_file(("yadt-config-localhost", "motd"),
                             "Today we serve @@@SPAM@@@ and @@@EGGS@@@.")

        self.create_tmp_dir(("yadt-config-localhost", "tomorrow"))
        self.create_tmp_file(("yadt-config-localhost", "tomorrow", "motd"),
                             "Tomorrow we serve @@@HAM@@@ and @@@EGGS@@@.")

        TokenReplacer.filter_directory(self.tmp_directory,
                                       self.abspath("VARIABLES.localhost"))

        self.ensure_file_contents(("yadt-config-localhost", "motd"),
                                  "Today we serve spam and eggs.")
        self.ensure_file_contents(("yadt-config-localhost", "tomorrow", "motd"),
                                  "Tomorrow we serve ham and eggs.")

    def test_should_filter_directory_with_custom_replacer(self):
        def replacer(token, replacement):
            return replacement.upper()

        self.create_tmp_dir("VARIABLES.localhost")
        self.create_tmp_file(("VARIABLES.localhost", "SPAM"), "spam")
        self.create_tmp_file(("VARIABLES.localhost", "EGGS"), "eggs")
        self.create_tmp_file(("VARIABLES.localhost", "HAM"), "ham")

        self.create_tmp_dir("yadt-config-localhost")

        self.create_tmp_file(("yadt-config-localhost", "motd"),
                             "Today we serve @@@SPAM@@@ and @@@EGGS@@@.")

        self.create_tmp_dir(("yadt-config-localhost", "tomorrow"))
        self.create_tmp_file(("yadt-config-localhost", "tomorrow", "motd"),
                             "Tomorrow we serve @@@HAM@@@ and @@@EGGS@@@.")

        TokenReplacer.filter_directory(self.tmp_directory,
                                       self.abspath("VARIABLES.localhost"),
                                       replacer_function=replacer)

        self.ensure_file_contents(("yadt-config-localhost", "motd"),
                                  "Today we serve SPAM and EGGS.")
        self.ensure_file_contents(("yadt-config-localhost", "tomorrow", "motd"),
                                  "Tomorrow we serve HAM and EGGS.")

    def test_should_filter_directory_with_var_in_var(self):
        self.create_tmp_dir("VARIABLES.localhost")
        self.create_tmp_file(("VARIABLES.localhost", "FOO"), "@@@BAR@@@")
        self.create_tmp_file(("VARIABLES.localhost", "BAR"), "bar")
        self.create_tmp_dir("yadt-config-localhost")
        self.create_tmp_file(("yadt-config-localhost", "text"),
                             "Hello @@@FOO@@@ and @@@BAR@@@.")

        TokenReplacer.filter_directory(self.tmp_directory,
                                       self.abspath("VARIABLES.localhost"))

        self.ensure_file_contents(("yadt-config-localhost", "text"),
                                  "Hello bar and bar.")

    def test_should_filter_directory_with_unused_variables(self):
            self.create_tmp_dir("VARIABLES.localhost")
            self.create_tmp_file(("VARIABLES.localhost", "SPAM"), "spam")
            self.create_tmp_file(("VARIABLES.localhost", "EGGS"), "eggs")
            self.create_tmp_file(("VARIABLES.localhost", "UNUSED"), "unused variable")

            self.create_tmp_dir("yadt-config-localhost")

            self.create_tmp_file(("yadt-config-localhost", "motd"),
                                 "Today we serve @@@SPAM@@@ and @@@EGGS@@@.")

            replacer = TokenReplacer.filter_directory(self.tmp_directory,
                                                      self.abspath("VARIABLES.localhost"))

            self.assertEqual(replacer.token_used, set(["SPAM", "EGGS"]))
