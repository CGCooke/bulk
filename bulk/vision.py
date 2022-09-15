import base64
import numpy as np
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import Button, ColumnDataSource, TextInput, DataTable, TableColumn, ColorBar, HTMLTemplateFormatter
from bokeh.plotting import figure

from ._bokeh_utils import get_color_mapping


def encode_image(path):
    with open(path, "rb") as image_file:
        enc_str = base64.b64encode(image_file.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{enc_str}">'

def bulk_vision(path):
    def bkapp(doc):
        df = pd.read_csv(path).assign(image=lambda d: [encode_image(p) for p in d['path']])
        df['alpha'] = 0.5
        # df['alpha'] = [0.4 if c == 'none' else 1 for c in df['color']]
        
        highlighted_idx = []

        mapper, df = get_color_mapping(df)
        columns = [
            TableColumn(field="image", title="image", formatter=HTMLTemplateFormatter(template="<%=image%>")),
        ]

        def update(attr, old, new):
            """Callback used for plot update when lasso selecting"""
            global highlighted_idx
            subset = df.iloc[new]
            highlighted_idx = new
            subset = subset.iloc[np.random.permutation(len(subset))]
            source.data = subset

        def save():
            """Callback used to save highlighted data points"""
            global highlighted_idx
            df.iloc[highlighted_idx][['text']].to_csv(text_filename.value, index=False)

        source = ColumnDataSource(data=dict())
        source_orig = ColumnDataSource(data=df)

        data_table = DataTable(source=source, columns=columns, width=750 if "color" in df.columns else 800)
        source.data = df

        p = figure(title="", sizing_mode="scale_both", tools=["lasso_select", "box_select", "pan", "box_zoom", "wheel_zoom", "reset"])
        p.toolbar.active_drag = None
        p.toolbar.active_inspect = None

        circle_kwargs = {"x": "x", "y": "y", "size": 1, "source": source_orig, "alpha": "alpha"}
        if "color" in df.columns:
            circle_kwargs.update({"color": mapper})
            color_bar = ColorBar(color_mapper=mapper['transform'], width=8)
            p.add_layout(color_bar, 'right')

        scatter = p.circle(**circle_kwargs)
        p.plot_width = 300
        if "color" in df.columns:
            p.plot_width=350
        p.plot_height = 300

        scatter.data_source.selected.on_change('indices', update)

        text_filename = TextInput(value="out.csv", title="Filename:")
        save_btn = Button(label="SAVE")
        save_btn.on_click(save)

        controls = column(p, text_filename, save_btn)
        return doc.add_root(
            row(controls, data_table)
        )

    return bkapp
