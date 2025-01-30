# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2024 RADAR-API developers
#
# This file is part of RADAR-API.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------.
"""This module test the list utilities."""
from radar_api.utils.timing import print_elapsed_time


def test_print_elapsed_time(capsys):
    """Test for print_elapsed_time."""

    @print_elapsed_time
    def add_decorated(a, b, verbose=True):
        return a + b

    # Check when verbose = True
    result = add_decorated(2, 3)
    captured = capsys.readouterr()  # Capture the print output

    assert result == 5, "Function result incorrect"
    assert "Elapsed time: " in captured.out

    # Check when verbose = False
    result = add_decorated(2, 3, verbose=False)
    captured = capsys.readouterr()  # Capture the print output

    assert result == 5, "Function result incorrect"
    assert captured.out == ""
