import sublime


def find_in_range(view, term, start, end, flags=sublime.LITERAL):
    found = view.find(term, start, flags)
    if found and found.b <= end:
        return found


def find_wrapping(view, term, start, end, flags=sublime.LITERAL, times=1):
    current_sel = view.sel()[0]
    # Search wrapping around the end of the buffer.
    for x in range(times):
        match = find_in_range(view, term, start, end)
        # Start searching in the upper half of the buffer if we aren't doing it yet.
        if not match and start > current_sel.b:
            start = 0
            end = current_sel.a
            match = find_in_range(view, term, start, end)
            if not match:
                return
        # No luck in the whole buffer.
        elif not match:
            return
        start = match.b

    return match


def reverse_find_wrapping(view, term, start, end, flags=sublime.LITERAL, times=1):
    current_sel = view.sel()[0]
    # Search wrapping around the end of the buffer.
    for x in range(times):
        match = reverse_search(view, term, start, end)
        # Start searching in the lower half of the buffer if we aren't doing it yet.
        if not match and start < current_sel.b:
            start = current_sel.b
            end = view.size()
            match = reverse_search(view, term, start, end)
            if not match:
                return
        # No luck in the whole buffer.
        elif not match:
            return
        end = match.a

    return match


def find_last_in_range(view, term, start, end, flags=sublime.LITERAL):
    found = find_in_range(view, term, start, end, flags)
    last_found = found
    while found:
        found = find_in_range(view, term, found.b, end, flags)
        if not found or found.b > end:
            break
        last_found = found if found else last_found

    return last_found


# reverse search
def reverse_search(view, term, start, end, flags=sublime.LITERAL):
    assert isinstance(start, int) or start is None
    assert isinstance(end, int) or end is None

    start = start if (start is not None) else 0
    end = end if (end is not None) else view.size()

    if start < 0 or end > view.size():
        return None

    lo_line = view.full_line(start)
    hi_line = view.full_line(end)

    while True:
        low_row, hi_row = view.rowcol(lo_line.a)[0], view.rowcol(hi_line.a)[0]
        middle_row = (low_row + hi_row) // 2

        middle_line = view.full_line(view.text_point(middle_row, 0))

        lo_region = sublime.Region(lo_line.a, middle_line.b)
        hi_region = sublime.Region(middle_line.b, min(hi_line.b, end))

        if find_in_range(view, term, hi_region.a, hi_region.b, flags):
            lo_line = view.full_line(middle_line.b)
        elif find_in_range(view, term, lo_region.a, lo_region.b, flags):
            hi_line = view.full_line(middle_line.a)
        else:
            return None

        if lo_line == hi_line:
            # we found the line we were looking for, now extract the match.
            return find_last_in_range(view, term, hi_line.a, min(hi_line.b, end), flags)


def reverse_search_by_pt(view, term, start, end, flags=sublime.LITERAL):
    assert isinstance(start, int) or start is None
    assert isinstance(end, int) or end is None

    start = start if (start is not None) else 0
    end = end if (end is not None) else view.size()

    if start < 0 or end > view.size():
        return None

    lo_line = view.full_line(start)
    hi_line = view.full_line(end)

    while True:
        low_row, hi_row = view.rowcol(lo_line.a)[0], view.rowcol(hi_line.a)[0]
        middle_row = (low_row + hi_row) // 2

        middle_line = view.full_line(view.text_point(middle_row, 0))

        lo_region = sublime.Region(lo_line.a, middle_line.b)
        hi_region = sublime.Region(middle_line.b, min(hi_line.b, end))

        if find_in_range(view, term, hi_region.a, hi_region.b, flags):
            lo_line = view.full_line(middle_line.b)
        elif find_in_range(view, term, lo_region.a, lo_region.b, flags):
            hi_line = view.full_line(middle_line.a)
        else:
            return None

        if lo_line == hi_line:
            # we found the line we were looking for, now extract the match.
            return find_last_in_range(view, term, max(hi_line.a, start), min(hi_line.b, end), flags)