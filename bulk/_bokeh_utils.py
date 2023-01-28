from pathlib import Path 
from typing import Tuple, Optional

from wasabi import msg
import bokeh.transform
import numpy as np
import pandas as pd
from bokeh.palettes import Category10, Cividis256
from bokeh.transform import linear_cmap, factor_cmap


def get_color_mapping(
    df: pd.DataFrame,
) -> Tuple[Optional[bokeh.transform.transform], pd.DataFrame]:
    """Creates a color mapping"""
    if "color" not in df.columns:
        return None, df

    color_datatype = str(df["color"].dtype)
    if color_datatype == "object":
        df["color"] = df["color"].apply(
            lambda x: str(x) if not (type(x) == float and np.isnan(x)) else x
        )
        all_values = list(df["color"].dropna().unique())
        if len(all_values) == 2:
            all_values.extend([""])
        elif len(all_values) > len(Category10) + 2:
            raise ValueError(
                f"Too many classes defined, the limit for visualisation is {len(Category10) + 2}. "
                f"Got {len(all_values)}."
            )
        mapper = factor_cmap(
            field_name="color",
            palette=Category10[len(all_values)],
            factors=all_values,
            nan_color="grey",
        )
    elif color_datatype.startswith("float") or color_datatype.startswith("int"):
        all_values = df["color"].dropna().values
        mapper = linear_cmap(
            field_name="color",
            palette=Cividis256,
            low=all_values.min(),
            high=all_values.max(),
            nan_color="grey",
        )
    else:
        raise TypeError(
            f"We currently only support the following type for 'color' column: 'int*', 'float*', 'object'. "
            f"Got {color_datatype}."
        )
    return mapper, df


def save_file(dataf: pd.DataFrame, highlighted_idx: pd.Series, filename: str) -> None:
    path = Path(filename)
    subset = dataf.iloc[highlighted_idx]
    if path.suffix == "jsonl":
        subset.to_json(path, orient="records", lines=True)
    else:
        subset.to_csv(path, index=False)
    msg.good(f"Saved {len(subset)} exampes over at {path}.", spaced=True)


def read_file(path: str):
    path = Path(path)
    if path.suffix == "jsonl":
        return pd.read_json(path, orient="records", lines=True)
    if path.suffix == "csv":
        return pd.read_csv(path)
    msg.fail(f"Bulk only supports .csv or .jsonl files, got {str(path)}.", exits=True, spaced=True)
