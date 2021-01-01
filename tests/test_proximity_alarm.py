from unittest import TestCase
import io
import glob
import proximity_alarm


class Test(TestCase):
    def test_alarm_for_files(self):
        def display_name(geocache):
            if geocache.hint is None:
                return "{gc_code}\nD{difficulty}/T{terrain}\n{name}".format(**vars(geocache))
            else:
                return "{gc_code}\nD{difficulty}/T{terrain}\n{hint}\n{name}".format(**vars(geocache))

        for testcase_dir in glob.glob("testcases/*/"):
            with self.subTest(testcase_dir):
                gpx_filepaths = glob.glob(testcase_dir + "/in/*.gpx")
                outfile = io.BytesIO()
                proximity_alarm.alarm_for_files(gpx_filepaths, outfile, display_name)
                reference_output_filepath = testcase_dir + "/out.gpx"
                generate_reference_output = False
                if generate_reference_output:
                    with open(reference_output_filepath, "wb") as f:
                        f.write(outfile.getvalue())
                    continue
                with open(reference_output_filepath) as reference_file:
                    reference_output = reference_file.read()
                self.assertEqual(outfile.getvalue().decode("utf-8"), reference_output)
