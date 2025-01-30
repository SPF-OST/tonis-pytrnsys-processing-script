import collections.abc as _cabc
import dataclasses as dc
import datetime as dt
import pathlib as pl
import sys
import typing as tp

import matplotlib.pyplot as plt
import pandas as pd

YEAR = 2024
BEGIN_DATETIME = dt.datetime(YEAR + 1, month=2, day=7)
END_DATETIME = dt.datetime(YEAR + 1, month=2, day=14)


def main() -> None:
    n_args = len(sys.argv)
    if n_args not in (2, 3):
        _print_usage_and_exit()

    input_file_path = pl.Path(sys.argv[1])

    if n_args == 3:
        output_file_path = pl.Path(sys.argv[2])
    else:
        output_file_path = input_file_path.with_suffix(".pdf")

    process(input_file_path, output_file_path)


def _print_usage_and_exit() -> tp.NoReturn:
    print(
        f"ERROR: Usage: {sys.argv[0]} <path-to-input-.prt-file> [path-to-output-file]"
    )
    sys.exit(-1)


def process(input_file_path: pl.Path, output_file_path: pl.Path) -> None:
    df = read_data_frame(input_file_path, YEAR)

    selected_time_range = (BEGIN_DATETIME <= df.index) & (
        df.index <= END_DATETIME
    )

    df = df.loc[selected_time_range]

    fig: plt.Figure
    all_axes: _cabc.Sequence[tp.Tuple[plt.Axes, plt.Axes]]
    fig, all_axes = plt.subplots(
        nrows=5, ncols=2, gridspec_kw=dict(width_ratios=[5, 1])
    )

    # set to A4
    fig.set_size_inches(8.27, 11.69)

    _create_sub_plot(
        df,
        _Axis(
            "Ambient temperature [°C]",
            "Tamb24".split(),
        ),
        all_axes[0][0],
        all_axes[0][1],
        _Axis(
            "Inside temperatures [°C]",
            "Top_EG_Ost Top_EG_West Top_1OG_Ost Top_1OG_West Top_2OG_Ost Top_2OG_West".split(),
        ),
    )

    _create_sub_plot(
        df,
        _Axis(
            "Power [kW]",
            "PelPVAC_kW myPelBui_kW PelAuxComp_kW PVToBui_kW PVToHP_kW PvToGrid_kW PelFromGrid_kW".split(),
        ),
        all_axes[1][0],
        all_axes[1][1],
        None,
    )

    _create_sub_plot(
        df,
        _Axis(
            "Temperatures [°C]",
            "TTesDhwAuxOn TTesDhwAuxOff Tdhw".split(),
        ),
        all_axes[2][0],
        all_axes[2][1],
        _Axis(
            "Power [kW]",
            "Pdhw_kW".split(),
        ),
    )

    _create_sub_plot(
        df,
        _Axis(
            "Temperatures [°C]",
            "TsensorTesSh TRdSet tSet_MixSh tRoomSet Tin_BuiRd".split(),
        ),
        all_axes[3][0],
        all_axes[3][1],
        _Axis(
            "Power [kW]",
            "qSysOut_BuiDemand".split(),
        ),
    )

    _create_sub_plot(
        df,
        _Axis(
            "Statuses [-]",
            "BoHS HpForDHWIsNeeded HpForSHIsNeeded".split(),
        ),
        all_axes[4][0],
        all_axes[4][1],
        _Axis(
            "Rate [%]",
            "pwrRate".split(),
        ),
    )

    fig.tight_layout()
    fig.savefig(output_file_path)


@dc.dataclass
class _Axis:
    label: str
    variables: _cabc.Sequence[str]

    def __post_init__(self) -> None:
        if not self.label or not self.variables:
            raise ValueError("Label and variables cannot be empty.")


def _create_sub_plot(
    df: pd.DataFrame,
    left_axis: _Axis,
    plot_axes: plt.Axes,
    legend_axes: plt.Axes,
    right_axis: _Axis | None,
) -> None:
    plot_axes_left = plot_axes

    plot_axes_left.set_ylabel(left_axis.label)
    df[left_axis.variables].plot(ax=plot_axes_left, legend=False)

    plot_axes_right = plot_axes_left.twinx() if right_axis else None

    if plot_axes_right:
        # Hack to not start with the first color again on second axis
        # See: https://github.com/matplotlib/matplotlib/issues/19479
        plot_axes_right._get_lines = plot_axes_left._get_lines

        plot_axes_right.set_ylabel(right_axis.label)
        df[right_axis.variables].plot(ax=plot_axes_right, legend=False)

    _create_legend(legend_axes, plot_axes_left, plot_axes_right)


def _create_legend(
    legend_axes: plt.Axes,
    plot_axes_left: plt.Axes,
    plot_axes_right: plt.Axes | None,
) -> None:
    left_handles, left_labels = plot_axes_left.get_legend_handles_labels()
    right_handles, right_labels = (
        plot_axes_right.get_legend_handles_labels()
        if plot_axes_right
        else ([], [])
    )
    handles = [*left_handles, *right_handles]
    labels = [*left_labels, *right_labels]
    legend_axes.legend(handles, labels, borderaxespad=0)
    legend_axes.axis("off")


def read_data_frame(
    input_file_path: pl.Path, starting_year: int
) -> pd.DataFrame:
    df = pd.read_csv(input_file_path, sep=r"\s+")

    df = _set_index(df, starting_year)

    return df


def _set_index(df: pd.DataFrame, starting_year: int) -> pd.DataFrame:
    hours = pd.to_timedelta(df["TIME"], "hours")
    start_of_year = dt.datetime(day=1, month=1, year=starting_year)
    index = start_of_year + hours
    index = index.rename("datetime")

    df = df.drop("TIME", axis="columns")

    df = pd.concat([df, index], axis="columns")

    df = df.set_index("datetime")

    return df


if __name__ == "__main__":
    main()
