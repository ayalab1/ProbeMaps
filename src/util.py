def offset_shank_channels(channel_string: str, offset: int) -> str:
    """
    Offsets a space-separated string of channel numbers by a specified amount.
    
    This is particularly useful for quickly adjusting neurophysiology channel 
    maps (e.g., copied from NDManager) when shifting shanks to a new probe 
    configuration or adjusting between 0-based and 1-based indexing.

    Parameters
    ----------
    channel_string : str
        A space-separated string of channel numbers (e.g., "239 224 238").
    offset : int
        The integer value to add to each channel number. Pass a negative 
        number to subtract.

    Returns
    -------
    str
        A space-separated string of the newly offset channel numbers.

    Examples
    --------
    >>> channels = "239 224 238 225"
    >>> offset_shank_channels(channels, -128)
    '111 96 110 97'
    """
    # Split the string, cast to int, apply the offset, cast back to str, and join.
    return ' '.join(str(int(ch) + offset) for ch in channel_string.split())
