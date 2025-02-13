#
# Copyright 2023 Picovoice Inc.
#
# You may not use this file except in compliance with the license. A copy of the license is located in the "LICENSE"
# file accompanying this source.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#

import os.path
import subprocess
import sys
import unittest

from parameterized import parameterized

from test_util import *

test_parameters = load_test_data()


class PicovoiceCTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._access_key = sys.argv[1]
        cls._platform = sys.argv[2]
        cls._arch = "" if len(sys.argv) != 4 else sys.argv[3]
        cls._root_dir = os.path.join(os.path.dirname(__file__), "../../../")

    def _get_library_file(self):
        return os.path.join(
            self._root_dir,
            "sdk",
            "c",
            "lib",
            self._platform,
            self._arch,
            "libpicovoice." + get_lib_ext(self._platform)
        )

    def _get_porcupine_model_path_by_language(self, language):
        model_path_subdir = append_language('lib/common/porcupine_params', language)
        return os.path.join(
            self._root_dir,
            "resources",
            "porcupine",
            '%s.pv' % model_path_subdir)

    def _get_rhino_model_path_by_language(self, language):
        model_path_subdir = append_language('lib/common/rhino_params', language)
        return os.path.join(
            self._root_dir,
            "resources",
            "rhino",
            '%s.pv' % model_path_subdir)

    def _get_keyword_path_by_language(self, language, keyword):
        keyword_files_root = append_language('resources/keyword_files', language)
        keyword_files_dir = os.path.join(
            self._root_dir,
            "resources",
            "porcupine",
            keyword_files_root,
            self._platform)

        return os.path.join(keyword_files_dir, "%s_%s.ppn" % (keyword, self._platform))

    def _get_context_path_by_language(self, language, context):
        context_files_root = append_language('resources/contexts', language)
        context_files_dir = os.path.join(
            self._root_dir,
            "resources",
            "rhino",
            context_files_root,
            self._platform)

        return os.path.join(context_files_dir, "%s_%s.rhn" % (context, self._platform))

    def _get_audio_file(self, audio_file_name):
        return os.path.join(
            self._root_dir,
            'resources/audio_samples',
            audio_file_name)

    def run_picovoice(self, language, keyword, context, audio_file_name, is_understood=False, intent=None, slots=None):
        args = [
            os.path.join(os.path.dirname(__file__), "../build/picovoice_demo_file"),
            "-a", self._access_key,
            "-l", self._get_library_file(),
            "-p", self._get_porcupine_model_path_by_language(language),
            "-r", self._get_rhino_model_path_by_language(language),
            "-k", self._get_keyword_path_by_language(language, keyword),
            "-c", self._get_context_path_by_language(language, context),
            "-t", "0.5",
            "-s", "0.5",
            "-w", self._get_audio_file(audio_file_name)
        ]
        process = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertEqual(process.poll(), 0)
        self.assertEqual(stderr.decode('utf-8'), '')

        self.assertTrue("[wake word]" in stdout.decode('utf-8'))

        understood_str = "is_understood : '%s'" % str(is_understood).lower()
        self.assertTrue(understood_str in stdout.decode('utf-8'))

        if intent is not None:
            intent_str = "intent : '%s'" % intent
            self.assertTrue(intent_str in stdout.decode('utf-8'))

        if slots is not None:
            for key, value in slots.items():
                slot_str = "'%s' : '%s'" % (key, value)
                self.assertTrue(slot_str in stdout.decode('utf-8'))

    @parameterized.expand(test_parameters)
    def test_picovoice(self, language, keyword, context, audio_file_name, intent, slots):
        self.run_picovoice(
            language=language,
            keyword=keyword,
            context=context,
            audio_file_name=audio_file_name,
            is_understood=True,
            intent=intent,
            slots=slots)

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("usage: test_picovoice_c.py ${AccessKey} ${Platform} [${Arch}]")
        exit(1)
    unittest.main(argv=sys.argv[:1])
