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

import cgi
import logging
import re
import os

import config_rpm_maker.magic

from config_rpm_maker import config
from config_rpm_maker.token.cycle import TokenCycleChecking
from config_rpm_maker.exceptions import BaseConfigRpmMakerException


class MissingOrRedundantTokenException(BaseConfigRpmMakerException):
    error_info = """Could not replace some token(s)"
Perhaps you have forgotten a variable,
or you have declared variable that requires itself?\n"""


class CouldNotEscapeHtmlException (BaseConfigRpmMakerException):
    error_info = "Could not escape html :\n"


class CannotFilterFileException (BaseConfigRpmMakerException):
    error_info = "Could not filter file :\n"


class MissingTokenException (BaseConfigRpmMakerException):
    error_info = "Could not replace variable in file :\n"
    """
    Exception stating that a value for a given token
    has not been found in the token definition.
    """

    def __init__(self, token, file=None, *args, **kwargs):
        super(MissingTokenException, self).__init__(*args, **kwargs)
        self.token = token
        self.file = file

    def __str__(self):
        msg = "Missing token '%s'" % self.token
        if self.file:
            msg += " in file '%s'" % self.file
        return msg


class FileLimitExceededException(BaseConfigRpmMakerException):
    error_info = "File limit exceeded! :\n"
    """
    Exception stating the file exceeded the given file size limit
    """
    def __init__(self, path, size_limit=-1, *args, **kwargs):
        super(FileLimitExceededException, self).__init__(*args, **kwargs)
        self.path = path
        self.size_limit = size_limit

    def __str__(self):
        return "The file '%s' (%d bytes) is bigger than the allowed file size %d bytes." % (self.path, os.path.getsize(self.path), self.size_limit)


class TokenReplacer(object):
    """
    Class that replaces tokens in strings.

    The general syntax is
        @@@TOKEN@@@
    """

    TOKEN_PATTERN = re.compile(r"@@@([A-Za-z0-9_-]*)@@@")

    @classmethod
    def filter_directory(cls,
                         directory,
                         variables_definition_directory,
                         replacer_function=None, html_escape=False, html_escape_function=None):
        logging.info("Filtering files in %s", directory)

        token_replacer = cls.from_directory(os.path.abspath(variables_definition_directory),
                                            replacer_function=replacer_function, html_escape_function=html_escape_function)

        for root, _, filenames in os.walk(directory):
            if variables_definition_directory in root:
                continue
            for filename in filenames:
                absolute_filename = os.path.join(root, filename)
                logging.debug("Filtering file %s", absolute_filename)
                token_replacer.filter_file(absolute_filename, html_escape=html_escape)

        return token_replacer

    @classmethod
    def from_directory(cls, directory, replacer_function=None, html_escape_function=None):
        logging.debug("Initializing token replacer of class %s from directory %s",
                      cls.__name__, directory)

        token_values = {}
        absolute_path = os.path.abspath(directory)

        for name in os.listdir(absolute_path):
            candidate = os.path.join(absolute_path, name)
            if os.path.isfile(candidate):
                with open(candidate) as property_file:
                    token_values[name] = property_file.read().strip()

        return cls(token_values=token_values, replacer_function=replacer_function, html_escape_function=html_escape_function)

    def __init__(self, token_values={}, replacer_function=None, html_escape_function=None):
        self.token_values = {}
        self.token_used = set()
        for token in token_values:
            self.token_values[token] = token_values[token].decode('UTF-8').strip()

        if not replacer_function:
            def replacer_function(token, replacement):
                return replacement
        else:
            logging.debug("Using custom replacer_function %s",
                          replacer_function.__name__)

        if not html_escape_function:
            def html_escape_function(filename, content):
                try:
                    content = cgi.escape(content, quote=True)
                    return u"<!DOCTYPE html><html><head><title>%s</title></head><body><pre>%s</pre></body></html>" % (filename, content)
                except Exception as e:
                    raise CouldNotEscapeHtmlException("Could not html escape file: " + filename + '\n\n' + str(e))

        self.replacer_function = replacer_function
        self.html_escape_function = html_escape_function

        self.token_values = self._replace_tokens_in_token_values(self.token_values)
        self.magic_mime_encoding = None

    def filter(self, content):
        while True:
            match = TokenReplacer.TOKEN_PATTERN.search(content)
            if not match:
                return content
            token_name = match.group(1)
            if not token_name in self.token_values:
                raise MissingTokenException(token_name)
            replacement = self.replacer_function(token_name,
                                                 self.token_values[token_name])

            content = content.replace("@@@%s@@@" % token_name, replacement)
            self.token_used.add(token_name)

    def filter_file(self, filename, html_escape=False):
        try:
            self.file_size_limit = config.get('max_file_size', 100 * 1024)
            if os.path.getsize(filename) > self.file_size_limit:
                raise Exception("FileTooFatException : %s\n\t(size is %s bytes, limit is %s bytes)" % (os.path.basename(filename), os.path.getsize(filename), self.file_size_limit))

            with open(filename, "r") as input_file:
                file_content = input_file.read()

            file_encoding = self._get_file_encoding(file_content)
            if file_encoding and file_encoding != 'binary':
                file_content = file_content.decode(file_encoding)
                if html_escape:
                    file_content = self.html_escape_function(os.path.basename(filename), file_content)

                file_content_filtered = self.filter(file_content)
                with open(filename, "w") as output_file:
                    output_file.write(file_content_filtered.encode(file_encoding))
        except MissingTokenException as exception:
            raise MissingTokenException(exception.token, filename)
        except Exception as e:
            raise CannotFilterFileException('Cannot filter file %s.\n%s' % (os.path.basename(filename), str(e)))

    def _replace_tokens_in_token_values(self, token_values):
        tokens_without_sub_tokens = dict((key, value) for (key, value) in token_values.iteritems() if not TokenReplacer.TOKEN_PATTERN.search(value))
        tokens_with_sub_tokens = dict((key, value) for (key, value) in token_values.iteritems() if TokenReplacer.TOKEN_PATTERN.search(value))

        while tokens_with_sub_tokens:
            tokens_with_sub_tokens_after_replace = {}
            replace_count = 0
            for (key, value) in tokens_with_sub_tokens.iteritems():
                token_names = TokenReplacer.TOKEN_PATTERN.findall(value)
                for token_name in token_names:
                    if token_name in tokens_without_sub_tokens:
                        value = value.replace("@@@%s@@@" % token_name, tokens_without_sub_tokens[token_name])
                        replace_count += 1

                if TokenReplacer.TOKEN_PATTERN.search(value):
                    tokens_with_sub_tokens_after_replace[key] = value
                else:
                    tokens_without_sub_tokens[key] = value

            # there are still invalid tokens and we could not replace any of them in the last loop cycle, so let's throw an error
            if tokens_with_sub_tokens_after_replace and not replace_count:
                #maybe there is a cycle?
                dependency_digraph = {}
                for (variable, variable_contents) in tokens_with_sub_tokens_after_replace.iteritems():
                    edge_source = variable
                    edge_target = TokenReplacer.TOKEN_PATTERN.findall(variable_contents)
                    dependency_digraph[edge_source] = edge_target
                token_graph = TokenCycleChecking(dependency_digraph)
                token_graph.assert_no_cycles_present()
                #no cycle => variable undefined
                unreplaced_variables = []
                for(variable, variable_contents) in tokens_with_sub_tokens_after_replace.iteritems():
                    unreplaced = TokenReplacer.TOKEN_PATTERN.findall(variable_contents)
                    unreplaced_variables.append(unreplaced)
                raise MissingOrRedundantTokenException("Unresolved variables :\n" + str(unreplaced_variables))

            tokens_with_sub_tokens = tokens_with_sub_tokens_after_replace

        return tokens_without_sub_tokens

    def _get_file_encoding(self, content):
        if not self.magic_mime_encoding:
            self.magic_mime_encoding = config_rpm_maker.magic.Magic(mime_encoding=True)
        return self.magic_mime_encoding.from_buffer(content)
