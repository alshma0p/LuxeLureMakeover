from typing import List

from app.schemas.common import disclaimer_ar


SKIN_TYPE_MAP = {
    "dry": "جافة",
    "normal": "عادية",
    "oily": "دهنية"
}


def map_label(label: str) -> str:
    label_lower = label.lower()
    for key, value in SKIN_TYPE_MAP.items():
        if key in label_lower:
            return value
    return "غير واضح"


def derive_attributes(confidence: float, tzone_shiny: bool, irritates_easily: bool, predicted_label: str) -> List[str]:
    attributes = []
    if confidence < 0.55:
        attributes.append("مختلطة")
    if tzone_shiny and "جافة" in predicted_label:
        attributes.append("مختلطة")
    if irritates_easily:
        attributes.append("حساسة")
    return list(dict.fromkeys(attributes))


def preview_template(skin_type: str) -> dict:
    return {
        "summary": [
            f"التقدير الأولي يشير إلى أن بشرتك {skin_type}.",
            "قد تختلف النتيجة مع اختلاف الإضاءة أو زاوية الصورة.",
            "استخدمي النصائح العامة كمرشد أولي فقط."
        ],
        "top_tips": [
            "التزم بغسول لطيف صباحا ومساء.",
            "رطبي البشرة بمرطب خفيف ومتوازن.",
            "استخدمي واقي شمس مناسب يوميا."
        ]
    }


def full_report_template(skin_type: str, attributes: List[str]) -> dict:
    attribute_text = "، ".join(attributes) if attributes else "بدون سمات إضافية"
    return {
        "what_it_means": [
            f"نوع البشرة المقدر هو {skin_type} مع سمات {attribute_text}.",
            "هذا التقدير أولي وغير طبي.",
            "اختاري المنتجات بناء على شعور بشرتك اليومي."
        ],
        "fits_you": [
            "منظف لطيف غير معطر.",
            "مرطب خفيف مع مكونات مهدئة.",
            "واقي شمس واسع الطيف.",
            "ترطيب إضافي بعد الاستحمام.",
            "مستحضرات غير كوميدوغينيك."
        ],
        "avoid": [
            "المقشرات القوية جدا بشكل متكرر.",
            "المنتجات عالية العطور.",
            "الغسل المفرط بالماء الساخن.",
            "تجارب منتجات متعددة في نفس اليوم.",
            "فرك البشرة بقوة."
        ],
        "simple_routine_am": [
            "غسول لطيف.",
            "مرطب خفيف.",
            "واقي شمس مناسب."
        ],
        "simple_routine_pm": [
            "غسول لطيف.",
            "مرطب داعم للحاجز.",
            "نوم كاف وترطيب داخلي."
        ],
        "see_specialist_if": [
            "ألم أو التهاب شديد.",
            "طفح جلدي متكرر.",
            "تحسس شديد مستمر."
        ],
        "disclaimer_ar": disclaimer_ar
    }
