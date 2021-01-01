import os
import pathlib
import unittest
import io
import glob
import sys
os.chdir(pathlib.Path(__file__).parent)
sys.path.append("..")
import proximity_alarm


class Test(unittest.TestCase):
    def test_alarm_for_files(self):
        generate_reference_output = False
        display_format = "{gc_code}\nD{difficulty}/T{terrain}\n{hint}\n{name}"
        distance = 42.0
        encoding = "utf-8"

        for testcase_dir in glob.glob("testcases/*/"):
            with self.subTest(testcase_dir):
                gpx_filepaths = glob.glob(testcase_dir + "/in/*.gpx")
                outfile = io.BytesIO()
                proximity_alarm.alarm_for_files(gpx_filepaths, outfile, distance, display_format)
                reference_output_filepath = testcase_dir + "/out.gpx"
                if generate_reference_output:
                    with open(reference_output_filepath, "wb") as f:
                        f.write(outfile.getvalue())
                else:
                    with open(reference_output_filepath, encoding=encoding) as reference_file:
                        reference_output = reference_file.read()
                    self.assertEqual(outfile.getvalue().decode(encoding), reference_output)


if __name__ == "__main__":
    unittest.main()
