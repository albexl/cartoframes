from ..widget import Widget


def histogram_widget(value, title=None, description=None, footer=None, format=None, read_only=False, buckets=20,
                     weight=1, is_global=False):
    """Helper function for quickly creating a histogram widget.

    Histogram widgets display the distribution of a numeric attribute, in buckets, to group
    ranges of values in your data.

    By default, you can hover over each bar to see each bucket's values and count, and also
    filter your map's data within a given range

    Args:
        value (str): Column name of the numeric or date value.
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.
        format (str, optional): Format to apply to number values in the widget, based on d3-format
            specifier (https://github.com/d3/d3-format#locale_format).
        read_only (boolean, optional): Interactively filter a range of numeric values by
            selecting them in the widget. Set to "False" by default.
        buckets (number, optional): Number of histogram buckets. Set to 20 by default.
        is_global (boolean, optional): Account for calculations based on the entire dataset ('global') vs.
            the default of 'viewport' features.

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> histogram_widget(
        ...     'column_name',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer',
        ...     buckets=9)

    """
    return Widget('histogram', value, title, description, footer, format=format, read_only=read_only, buckets=buckets,
                  weight=weight, is_global=is_global)
