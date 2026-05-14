def calculate_fee(first_graduate: bool, hostel_required: bool) -> dict:
    """Calculate fee components for administration fee assignment."""
    semester_fee = 85000 if first_graduate else 110000
    book_fee = 3950
    exam_fee = 250
    hostel_fee = 60000 if hostel_required else 0
    misc_fee = 10000

    total = semester_fee + book_fee + exam_fee + hostel_fee + misc_fee

    return {
        "semester_fee": semester_fee,
        "book_fee": book_fee,
        "exam_fee": exam_fee,
        "hostel_fee": hostel_fee,
        "misc_fee": misc_fee,
        "total": total,
    }
