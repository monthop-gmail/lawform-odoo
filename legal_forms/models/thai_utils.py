"""Thai language utilities for court forms."""

from datetime import date, datetime

THAI_DIGITS = str.maketrans('0123456789', '๐๑๒๓๔๕๖๗๘๙')
ARABIC_DIGITS = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')

THAI_MONTHS = [
    '', 'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน',
    'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม',
    'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม',
]

THAI_MONTHS_SHORT = [
    '', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.',
    'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.',
    'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.',
]

THAI_DAYS = [
    'จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี',
    'ศุกร์', 'เสาร์', 'อาทิตย์',
]


def to_thai_digits(text):
    """Convert Arabic digits to Thai digits.

    >>> to_thai_digits('123')
    '๑๒๓'
    >>> to_thai_digits('คดีหมายเลข 1234/2569')
    'คดีหมายเลข ๑๒๓๔/๒๕๖๙'
    """
    if not text:
        return text
    return str(text).translate(THAI_DIGITS)


def to_arabic_digits(text):
    """Convert Thai digits to Arabic digits.

    >>> to_arabic_digits('๑๒๓')
    '123'
    """
    if not text:
        return text
    return str(text).translate(ARABIC_DIGITS)


def to_thai_date(d, fmt='long'):
    """Convert date to Thai Buddhist era format.

    Args:
        d: date or datetime object
        fmt: 'long'  = 'วันที่ ๑๕ เดือน มีนาคม พุทธศักราช ๒๕๖๙'
             'short' = '๑๕ มี.ค. ๒๕๖๙'
             'full'  = 'วันจันทร์ที่ ๑๕ เดือน มีนาคม พุทธศักราช ๒๕๖๙'

    >>> to_thai_date(date(2026, 3, 15), 'long')
    'วันที่ ๑๕ เดือน มีนาคม พุทธศักราช ๒๕๖๙'
    >>> to_thai_date(date(2026, 3, 15), 'short')
    '๑๕ มี.ค. ๒๕๖๙'
    """
    if not d:
        return ''
    if isinstance(d, datetime):
        d = d.date()

    day = to_thai_digits(str(d.day))
    be_year = d.year + 543
    year = to_thai_digits(str(be_year))

    if fmt == 'short':
        month = THAI_MONTHS_SHORT[d.month]
        return f'{day} {month} {year}'
    elif fmt == 'full':
        weekday = THAI_DAYS[d.weekday()]
        month = THAI_MONTHS[d.month]
        return f'วัน{weekday}ที่ {day} เดือน {month} พุทธศักราช {year}'
    else:  # long
        month = THAI_MONTHS[d.month]
        return f'วันที่ {day} เดือน {month} พุทธศักราช {year}'


def to_thai_year(d):
    """Get Buddhist era year as Thai digits.

    >>> to_thai_year(date(2026, 1, 1))
    '๒๕๖๙'
    """
    if not d:
        return ''
    if isinstance(d, datetime):
        d = d.date()
    return to_thai_digits(str(d.year + 543))
