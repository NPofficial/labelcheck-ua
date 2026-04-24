"""Service for generating PDF validation reports."""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)


# Кандидати шрифтів у порядку пріоритету: (regular, bold, name, bold_name).
# Liberation Sans стоїть першим — він Arial-подібний і сприймається як
# офіційний документальний шрифт. DejaVu — запасний варіант з повною
# кирилицею. Якщо жоден не знайдено — fallback на Helvetica (без кирилиці).
_FONT_CANDIDATES: List[Tuple[str, str, str, str]] = [
    (
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "LiberationSans",
        "LiberationSans-Bold",
    ),
    (
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "LiberationSans",
        "LiberationSans-Bold",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "DejaVuSans",
        "DejaVuSans-Bold",
    ),
]


def _register_fonts() -> Tuple[str, str]:
    """Registers first available font pair, returns (regular_name, bold_name)."""
    for regular_path, bold_path, name, bold_name in _FONT_CANDIDATES:
        if not os.path.exists(regular_path):
            continue
        try:
            pdfmetrics.registerFont(TTFont(name, regular_path))
            if os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                logger.info("PDF fonts registered: %s + %s", name, bold_name)
                return name, bold_name
            logger.warning("Bold missing for %s, using regular for both", name)
            return name, name
        except Exception as exc:  # noqa: BLE001 — fallback chain
            logger.debug("Failed to register %s from %s: %s", name, regular_path, exc)
            continue

    logger.warning(
        "No Cyrillic-capable fonts found on system; falling back to Helvetica "
        "(Ukrainian may render as squares)."
    )
    return "Helvetica", "Helvetica-Bold"


# Кольори — відповідають палітрі UI фронтенду.
_COLOR_TEXT = colors.Color(30 / 255, 41 / 255, 59 / 255)       # foreground
_COLOR_MUTED = colors.Color(100 / 255, 116 / 255, 139 / 255)   # muted
_COLOR_BG = colors.Color(248 / 255, 250 / 255, 252 / 255)      # light grey bg
_COLOR_SUCCESS = colors.Color(16 / 255, 185 / 255, 129 / 255)
_COLOR_ERROR = colors.Color(220 / 255, 38 / 255, 38 / 255)
_COLOR_WARNING = colors.Color(217 / 255, 119 / 255, 6 / 255)


class ReportService:
    """Service for generating PDF validation reports."""

    def __init__(self) -> None:
        self.font_name, self.bold_font_name = _register_fonts()
        self.styles = getSampleStyleSheet()
        self._styles = self._build_styles()

    def _build_styles(self) -> Dict[str, ParagraphStyle]:
        base = self.styles["Normal"]
        return {
            "title": ParagraphStyle(
                "ReportTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                leading=22,
                textColor=_COLOR_TEXT,
                alignment=1,
                fontName=self.bold_font_name,
                spaceAfter=2,
            ),
            "subtitle": ParagraphStyle(
                "ReportSubtitle",
                parent=base,
                fontSize=10,
                textColor=_COLOR_MUTED,
                alignment=1,
                fontName=self.font_name,
                spaceAfter=10,
            ),
            "section": ParagraphStyle(
                "ReportSection",
                parent=self.styles["Heading2"],
                fontSize=13,
                leading=16,
                textColor=_COLOR_TEXT,
                fontName=self.bold_font_name,
                spaceBefore=8,
                spaceAfter=4,
            ),
            "item_title": ParagraphStyle(
                "ReportItemTitle",
                parent=base,
                fontSize=10.5,
                leading=14,
                fontName=self.bold_font_name,
                textColor=_COLOR_TEXT,
                spaceAfter=2,
            ),
            "body": ParagraphStyle(
                "ReportBody",
                parent=base,
                fontSize=9.5,
                leading=13,
                fontName=self.font_name,
                textColor=_COLOR_TEXT,
            ),
            "body_muted": ParagraphStyle(
                "ReportBodyMuted",
                parent=base,
                fontSize=9,
                leading=12,
                fontName=self.font_name,
                textColor=_COLOR_MUTED,
            ),
            "status": ParagraphStyle(
                "ReportStatus",
                parent=base,
                fontSize=12,
                fontName=self.bold_font_name,
                spaceAfter=6,
            ),
            "disclaimer": ParagraphStyle(
                "ReportDisclaimer",
                parent=base,
                fontSize=8,
                leading=11,
                textColor=_COLOR_MUTED,
                fontName=self.font_name,
            ),
        }

    async def generate_pdf_report(
        self,
        check_id: str,
        report_data: Dict,
        output_path: str,
    ) -> str:
        """Generates PDF report. Returns output_path."""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=18 * mm,
                rightMargin=18 * mm,
                topMargin=15 * mm,
                bottomMargin=15 * mm,
                title="LabelCheck UA — Звіт",
            )
            story = []

            story.extend(self._build_header(check_id, report_data))
            story.extend(self._build_summary(report_data))
            story.extend(self._build_stats_table(report_data))

            errors = report_data.get("errors") or []
            if errors:
                story.extend(self._build_errors(errors))

            compliance_errors = report_data.get("compliance_errors") or []
            forbidden = [e for e in compliance_errors if e.get("type") == "forbidden_phrase"]
            if forbidden:
                story.extend(self._build_forbidden(forbidden))

            missing = [e for e in compliance_errors if e.get("type") == "mandatory_field"]
            if missing:
                story.extend(self._build_missing_fields(missing))

            warnings = report_data.get("warnings") or []
            if warnings:
                story.extend(self._build_warnings(warnings))

            story.extend(self._build_regulatory())
            story.extend(self._build_disclaimer())

            doc.build(story)
            logger.info("PDF report generated: %s", output_path)
            return output_path
        except Exception as exc:
            logger.error("Error generating PDF report: %s", exc, exc_info=True)
            raise

    # ---------------------------------------------------------------
    # SECTIONS
    # ---------------------------------------------------------------

    def _build_header(self, check_id: str, data: Dict) -> List:
        product_name = (data.get("product_info") or {}).get("name") or "—"
        checked_at = data.get("checked_at")
        try:
            check_date = datetime.fromisoformat(checked_at)
            date_str = check_date.strftime("%d.%m.%Y %H:%M")
        except (TypeError, ValueError):
            date_str = "—"

        elements = [
            Paragraph("Звіт про перевірку етикетки", self._styles["title"]),
            Paragraph(
                "Автоматизована перевірка відповідності законодавству України",
                self._styles["subtitle"],
            ),
            Paragraph(f"<b>Продукт:</b> {product_name}", self._styles["body"]),
            Paragraph(f"<b>Дата перевірки:</b> {date_str}", self._styles["body"]),
            Paragraph(f"<b>Номер звіту:</b> #{check_id[:8]}", self._styles["body"]),
            Spacer(1, 8),
        ]
        return elements

    def _build_summary(self, data: Dict) -> List:
        is_valid = bool(data.get("is_valid"))
        stats = data.get("stats") or {}
        errors_count = int(stats.get("total_dosage_errors") or 0)
        missing_count = int(stats.get("total_missing_fields") or 0)
        forbidden_count = int(stats.get("total_forbidden_phrases") or 0)
        total_critical = errors_count + missing_count + forbidden_count

        if is_valid and total_critical == 0:
            status_text = "ВІДПОВІДАЄ ВИМОГАМ"
            color_hex = "#10B981"
        elif total_critical == 0:
            status_text = "Є ПОПЕРЕДЖЕННЯ"
            color_hex = "#D97706"
        else:
            status_text = "ВИЯВЛЕНО ПОРУШЕННЯ"
            color_hex = "#DC2626"

        return [
            Paragraph("Резюме", self._styles["section"]),
            Paragraph(
                f'<font color="{color_hex}"><b>{status_text}</b></font>',
                self._styles["status"],
            ),
        ]

    def _build_stats_table(self, data: Dict) -> List:
        stats = data.get("stats") or {}
        penalties = data.get("penalties") or {}
        total_penalty = int(penalties.get("total_amount") or 0)

        rows = [
            ["Критичні помилки дозування:", str(stats.get("total_dosage_errors", 0))],
            ["Попередження дозування:", str(stats.get("total_dosage_warnings", 0))],
            ["Заборонені фрази:", str(stats.get("total_forbidden_phrases", 0))],
            ["Відсутні обов'язкові поля:", str(stats.get("total_missing_fields", 0))],
            ["Перевірено інгредієнтів:", str(stats.get("total_ingredients", 0))],
        ]
        if total_penalty > 0:
            rows.append([
                "Потенційний штраф:",
                f"{total_penalty:,} {penalties.get('currency', 'UAH')}".replace(",", " "),
            ])

        table = Table(rows, colWidths=[110 * mm, 60 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _COLOR_BG),
            ("TEXTCOLOR", (0, 0), (-1, -1), _COLOR_TEXT),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.lightgrey),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        return [table, Spacer(1, 10)]

    def _build_errors(self, errors: List[Dict]) -> List:
        out: List = [
            Paragraph(
                f'<font color="#DC2626">Критичні помилки ({len(errors)})</font>',
                self._styles["section"],
            )
        ]
        for idx, error in enumerate(errors, 1):
            out.append(Paragraph(
                f"{idx}. {error.get('ingredient', '—')} — {error.get('message', '—')}",
                self._styles["item_title"],
            ))
            detail_lines = []
            if error.get("current_dose"):
                detail_lines.append(f"Поточна доза: {error['current_dose']}")
            if error.get("max_allowed"):
                detail_lines.append(f"Максимально допустимо: {error['max_allowed']}")
            if error.get("current_form"):
                detail_lines.append(f"Форма: {error['current_form']}")
            if error.get("regulatory_source"):
                detail_lines.append(f"Джерело: {error['regulatory_source']}")
            if detail_lines:
                out.append(Paragraph(" · ".join(detail_lines), self._styles["body_muted"]))
            if error.get("recommendation"):
                out.append(Paragraph(
                    f"<b>Рекомендація:</b> {error['recommendation']}",
                    self._styles["body"],
                ))
            if error.get("penalty_amount"):
                amount = int(error["penalty_amount"])
                out.append(Paragraph(
                    f"<b>Штраф:</b> {amount:,} грн".replace(",", " "),
                    self._styles["body"],
                ))
            out.append(Spacer(1, 6))
        return out

    def _build_forbidden(self, errors: List[Dict]) -> List:
        out: List = [
            Paragraph(
                f'<font color="#DC2626">Заборонені формулювання ({len(errors)})</font>',
                self._styles["section"],
            )
        ]
        for idx, error in enumerate(errors, 1):
            phrase = error.get("phrase") or "—"
            out.append(Paragraph(f'{idx}. «{phrase}»', self._styles["item_title"]))
            meta = []
            if error.get("category"):
                meta.append(f"Категорія: {error['category']}")
            if error.get("regulatory_source"):
                meta.append(f"Джерело: {error['regulatory_source']}")
            if meta:
                out.append(Paragraph(" · ".join(meta), self._styles["body_muted"]))
            if error.get("explanation"):
                out.append(Paragraph(error["explanation"], self._styles["body"]))
            if error.get("recommendation"):
                out.append(Paragraph(
                    f"<b>Рекомендація:</b> {error['recommendation']}",
                    self._styles["body"],
                ))
            if error.get("penalty_amount"):
                amount = int(error["penalty_amount"])
                out.append(Paragraph(
                    f"<b>Штраф:</b> {amount:,} грн".replace(",", " "),
                    self._styles["body"],
                ))
            out.append(Spacer(1, 6))
        return out

    def _build_missing_fields(self, errors: List[Dict]) -> List:
        out: List = [
            Paragraph(
                f'<font color="#DC2626">Відсутні обов\'язкові поля ({len(errors)})</font>',
                self._styles["section"],
            )
        ]
        for idx, error in enumerate(errors, 1):
            field_name = error.get("field_name") or "—"
            out.append(Paragraph(f"{idx}. {field_name}", self._styles["item_title"]))
            if error.get("error_message"):
                out.append(Paragraph(error["error_message"], self._styles["body"]))
            meta_parts: List[str] = []
            if error.get("regulatory_source"):
                meta_parts.append(f"Джерело: {error['regulatory_source']}")
            article = error.get("article_number")
            if article and (
                not error.get("regulatory_source")
                or article not in error["regulatory_source"]
            ):
                meta_parts.append(f"Стаття: {article}")
            if meta_parts:
                out.append(Paragraph(" · ".join(meta_parts), self._styles["body_muted"]))
            if error.get("recommendation"):
                out.append(Paragraph(
                    f"<b>Рекомендація:</b> {error['recommendation']}",
                    self._styles["body"],
                ))
            if error.get("penalty_amount"):
                amount = int(error["penalty_amount"])
                out.append(Paragraph(
                    f"<b>Штраф:</b> {amount:,} грн".replace(",", " "),
                    self._styles["body"],
                ))
            out.append(Spacer(1, 6))
        return out

    def _build_warnings(self, warnings: List[Dict]) -> List:
        out: List = [
            Paragraph(
                f'<font color="#D97706">Попередження ({len(warnings)})</font>',
                self._styles["section"],
            )
        ]
        for idx, warning in enumerate(warnings, 1):
            ingredient = warning.get("ingredient") or "—"
            message = warning.get("message") or "—"
            out.append(Paragraph(
                f"{idx}. {ingredient} — {message}",
                self._styles["item_title"],
            ))
            if warning.get("recommendation"):
                out.append(Paragraph(
                    f"<b>Рекомендація:</b> {warning['recommendation']}",
                    self._styles["body"],
                ))
            out.append(Spacer(1, 4))
        return out

    def _build_regulatory(self) -> List:
        acts = [
            "Закон України №4122-IX від 05.12.2024",
            "Закон України №2639-VIII від 06.12.2018",
            "Закон України №771/97-ВР від 23.12.1997",
            "Наказ МОЗ України №1114 від 19.12.2013",
        ]
        out: List = [Paragraph("Нормативна база", self._styles["section"])]
        for act in acts:
            out.append(Paragraph(f"• {act}", self._styles["body_muted"]))
        out.append(Spacer(1, 6))
        return out

    def _build_disclaimer(self) -> List:
        text = (
            "Цей звіт сформовано автоматизованою системою LabelCheck UA на основі "
            "чинного законодавства України у сфері обігу дієтичних добавок. Документ "
            "має довідково-рекомендаційний характер і призначений для внутрішнього "
            "контролю. Перед остаточним затвердженням етикетки радимо додатково "
            "перевірити її кваліфікованим фахівцем."
        )
        return [
            Paragraph("Дисклеймер", self._styles["section"]),
            Paragraph(text, self._styles["disclaimer"]),
        ]
