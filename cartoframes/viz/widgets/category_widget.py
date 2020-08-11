from ..widget import Widget


def category_widget(value, title=None, description=None, footer=None, format=None, read_only=False, weight=1,
                    is_global=False):
    """Helper function for quickly creating a category widget.

    Args:
        value (str): Column name of the category value.
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.
        format (str, optional): Format to apply to number values in the widget, based on d3-format
            specifier (https://github.com/d3/d3-format#locale_format).
        read_only (boolean, optional): Interactively filter a category by selecting it in the widget.
          Set to "False" by default.
        is_global (boolean, optional): Account for calculations based on the entire dataset ('global') vs.
            the default of 'viewport' features.

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> category_widget(
        ...     'column_name',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

    """
    return Widget('category', value, title, description, footer, format=format, read_only=read_only, weight=weight,
                  is_global=is_global)
