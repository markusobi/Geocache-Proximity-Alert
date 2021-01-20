import os
import pathlib
import unittest
import io
import glob
import sys
os.chdir(pathlib.Path(__file__).parent)
sys.path.append("..")
import proximity_alert


class Test(unittest.TestCase):
    def test_create_alert(self):
        generate_reference_output = False
        display_format = \
            "{gc_code}\n" \
            "D{difficulty}/T{terrain}\n" \
            "{hint}\n" \
            "{name}\n" \
            "{type}"
        encoding = "utf-8"
        self.maxDiff = None

        for testcase_dir in sorted(glob.glob("testcases/*/")):
            with self.subTest(testcase_dir):
                gpx_filepaths = sorted(glob.glob(testcase_dir + "/in/*.gpx"))
                outfile = io.BytesIO()
                proximity_alert.create_alert(
                    gpx_filepaths=gpx_filepaths,
                    out_file_or_filename=outfile,
                    distance=42.0,
                    display_format=display_format,
                    verbose=False)
                reference_output_filepath = testcase_dir + "/out.gpx"
                if generate_reference_output:
                    with open(reference_output_filepath, "wb") as f:
                        f.write(outfile.getvalue())
                else:
                    with open(reference_output_filepath, encoding=encoding) as reference_file:
                        reference_output = reference_file.read()
                    self.assertEqual(outfile.getvalue().decode(encoding), reference_output)

    def test_invalid_xml(self):
        self.assertRaises(
            proximity_alert.ProximityAlertError,
            proximity_alert.create_alert,
            gpx_filepaths=["test_proximity_alert.py"],
            out_file_or_filename=io.BytesIO(),
            distance=0.0,
            display_format="",
            verbose=False)

    def test_invalid_gpx(self):
        self.assertRaises(
            proximity_alert.ProximityAlertError,
            proximity_alert.create_alert,
            gpx_filepaths=["testcases/invalid_gpx.xml"],
            out_file_or_filename=io.BytesIO(),
            distance=0.0,
            display_format="",
            verbose=False)

    def test_no_caches_found(self):
        num_caches = proximity_alert.create_alert(
            gpx_filepaths=["testcases/no_caches.gpx"],
            out_file_or_filename=io.BytesIO(),
            distance=0.0,
            display_format="",
            verbose=False)
        self.assertEqual(num_caches, 0)

    def test_output_file_not_writable(self):
        self.assertRaises(
            proximity_alert.ProximityAlertError,
            proximity_alert.create_alert,
            gpx_filepaths=["testcases/single_gpx_download/in/GC1GTKQ.gpx"],
            out_file_or_filename="foobar/",
            distance=0.0,
            display_format="",
            verbose=False)

    def test_invalid_displayformat(self):
        self.assertRaises(
            proximity_alert.ProximityAlertError,
            proximity_alert.create_alert,
            gpx_filepaths=["testcases/single_gpx_download/in/GC1GTKQ.gpx"],
            out_file_or_filename=io.BytesIO(),
            distance=0.0,
            display_format="{",
            verbose=False)


if __name__ == "__main__":
    unittest.main()
