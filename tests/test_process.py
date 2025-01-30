import pathlib as pl

import process as proc

DATA_DIR_PATH = pl.Path(__file__).parent / "data"
INPUT_FILE_PATH = DATA_DIR_PATH / "input" / "Outputs.zip"


def test_read_data_frame() -> None:
    df = proc.read_data_frame(INPUT_FILE_PATH, proc.YEAR)
    print(df)


def test_process() -> None:
    output_file_path = (
        DATA_DIR_PATH / "output" / INPUT_FILE_PATH.with_suffix(".pdf").name
    )
    proc.process(INPUT_FILE_PATH, output_file_path)
