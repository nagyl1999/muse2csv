from muse2csv.converter import muse_to_csv

muse_export = "examples/anonim_pac_xml_export.txt"
wfdb_filename = "patient001_ecg"

annotations = muse_to_csv(muse_export, wfdb_filename)
