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
    def test_create_alert(self) -> None:
        generate_reference_output = False
        encoding = "utf-8"
        self.maxDiff = None

        for testcase_dir in sorted(glob.glob("testcases/*/")):
            with self.subTest(testcase_dir):
                gpx_filepaths = sorted(glob.glob(testcase_dir + "/in/*.gpx"))
                outfile = io.BytesIO()
                proximity_alert.create_alert(
                    gpx_filepaths=gpx_filepaths,
                    out_file_or_path=outfile,
                    distance=42.0,
                    verbose=False)
                reference_output_filepath = testcase_dir + "/out.gpx"
                if generate_reference_output:
                    with open(reference_output_filepath, "wb") as f:
                        f.write(outfile.getvalue())
                else:
                    with open(reference_output_filepath, encoding=encoding) as reference_file:
                        reference_output = reference_file.read()
                    self.assertEqual(outfile.getvalue().decode(encoding), reference_output)

    def test_invalid_xml(self) -> None:
        self.assertRaises(
            proximity_alert.ProximityAlertError,
            proximity_alert.create_alert,
            gpx_filepaths=["test_proximity_alert.py"],
            out_file_or_path=io.BytesIO(),
            distance=0.0,
            verbose=False)

    def test_invalid_gpx(self) -> None:
        self.assertRaises(
            proximity_alert.ProximityAlertError,
            proximity_alert.create_alert,
            gpx_filepaths=["testcases/invalid_gpx.xml"],
            out_file_or_path=io.BytesIO(),
            distance=0.0,
            verbose=False)

    def test_no_caches_found(self) -> None:
        num_caches = proximity_alert.create_alert(
            gpx_filepaths=["testcases/no_caches.gpx"],
            out_file_or_path=io.BytesIO(),
            distance=0.0,
            verbose=False)
        self.assertEqual(num_caches, 0)

    def test_output_file_not_writable(self) -> None:
        self.assertRaises(
            proximity_alert.ProximityAlertError,
            proximity_alert.create_alert,
            gpx_filepaths=["testcases/single_gpx_download/in/GC1GTKQ.gpx"],
            out_file_or_path="foobar/",
            distance=0.0,
            verbose=False)


if __name__ == "__main__":
    unittest.main()
