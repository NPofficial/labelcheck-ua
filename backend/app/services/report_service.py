"""Service for generating PDF validation reports"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating PDF validation reports"""
    
    def __init__(self):
        """Initialize ReportService with Ukrainian font support"""
        # Register Ukrainian fonts for proper Cyrillic support
        try:
            # Try to find DejaVu fonts in common locations
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
                os.path.join(os.path.dirname(__file__), "../../../fonts/DejaVuSans.ttf"),
            ]
            
            font_found = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(
                            TTFont('DejaVuSans', font_path)
                        )
                        # Try to register bold version
                        bold_path = font_path.replace('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf')
                        if os.path.exists(bold_path):
                            pdfmetrics.registerFont(
                                TTFont('DejaVuSans-Bold', bold_path)
                            )
                        self.font_name = 'DejaVuSans'
                        self.bold_font_name = 'DejaVuSans-Bold'
                        font_found = True
                        logger.info(f"Ukrainian fonts (DejaVu) registered from {font_path}")
                        break
                    except Exception as e:
                        logger.debug(f"Could not load font from {font_path}: {e}")
                        continue
            
            if not font_found:
                # Fallback to built-in fonts (may show squares for Ukrainian text)
                logger.warning("Could not load DejaVu fonts. Using default fonts (may not display Ukrainian properly)")
                self.font_name = 'Helvetica'
                self.bold_font_name = 'Helvetica-Bold'
        except Exception as e:
            logger.warning(f"Font registration error: {e}. Using default fonts.")
            self.font_name = 'Helvetica'
            self.bold_font_name = 'Helvetica-Bold'
        
        self.styles = getSampleStyleSheet()
    
    async def generate_pdf_report(
        self, 
        check_id: str,
        report_data: Dict,
        output_path: str
    ) -> str:
        """
        Generate PDF validation report
        
        Args:
            check_id: Check session ID
            report_data: Validation report data
            output_path: Path to save PDF
            
        Returns:
            Path to generated PDF
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'Title',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.Color(30/255, 41/255, 59/255),
                alignment=1,  # Center
                fontName=self.bold_font_name
            )
            story.append(Paragraph("ЗВІТ ПРО ПЕРЕВІРКУ ЕТИКЕТКИ", title_style))
            story.append(Spacer(1, 12))
            
            # Subtitle
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.Color(100/255, 116/255, 139/255),
                alignment=1,
                fontName=self.font_name
            )
            story.append(Paragraph("LabelCheck UA (AI Analysis)", subtitle_style))
            story.append(Spacer(1, 24))
            
            # Product info
            product_name = report_data.get("product_info", {}).get("name", "N/A")
            normal_style = ParagraphStyle(
                'Normal',
                parent=self.styles['Normal'],
                fontName=self.font_name
            )
            story.append(Paragraph(f"<b>Продукт:</b> {product_name}", normal_style))
            
            check_date = datetime.fromisoformat(report_data["checked_at"])
            story.append(Paragraph(
                f"<b>Дата перевірки:</b> {check_date.strftime('%d.%m.%Y %H:%M')}",
                normal_style
            ))
            story.append(Paragraph(f"<b>Номер звіту:</b> #{check_id[:8]}", normal_style))
            story.append(Spacer(1, 24))
            
            # Status summary
            status = "✅ ВІДПОВІДАЄ" if report_data["is_valid"] else "⚠️ ВИЯВЛЕНО ПОМИЛКИ"
            status_color_hex = '#10B981' if report_data["is_valid"] else '#EF4444'
            
            heading_style = ParagraphStyle(
                'Heading2',
                parent=self.styles['Heading2'],
                fontSize=16,
                fontName=self.bold_font_name
            )
            heading3_style = ParagraphStyle(
                'Heading3Custom',
                parent=self.styles['Heading3'],
                fontName=self.bold_font_name
            )
            story.append(Paragraph("РЕЗЮМЕ", heading_style))
            
            status_style = ParagraphStyle(
                'Status',
                parent=normal_style,
                fontSize=14,
                fontName=self.bold_font_name
            )
            story.append(Paragraph(
                f"<font color='{status_color_hex}'><b>{status}</b></font>",
                status_style
            ))
            story.append(Spacer(1, 12))
            
            # Stats table
            stats = report_data.get("stats", {})
            stats_data = [
                ["Критичні помилки дозування:", str(stats.get("total_dosage_errors", 0))],
                ["Попередження дозування:", str(stats.get("total_dosage_warnings", 0))],
                ["Заборонені фрази:", str(stats.get("total_forbidden_phrases", 0))],
                ["Відсутні обов'язкові поля:", str(stats.get("total_missing_fields", 0))],
                ["Перевірено інгредієнтів:", str(stats.get("total_ingredients", 0))],
            ]
            
            penalties = report_data.get("penalties", {})

            if stats.get("total_dosage_errors", 0) > 0 or stats.get("total_missing_fields", 0) > 0:
                stats_data.append([
                    "Потенційні штрафи:",
                    f"{penalties.get('total_amount', 0):,} {penalties.get('currency', 'UAH')}"
                ])
            
            stats_table = Table(stats_data, colWidths=[120*mm, 70*mm])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(248/255, 250/255, 252/255)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 24))
            
            # Errors section
            errors = report_data.get("errors", [])
            if errors:
                story.append(Paragraph("🔴 КРИТИЧНІ ПОМИЛКИ", heading_style))
                story.append(Spacer(1, 12))
                
                for i, error in enumerate(errors, 1):
                    error_style = ParagraphStyle(
                        'Error',
                        parent=normal_style,
                        fontSize=11,
                        fontName=self.bold_font_name,
                        textColor=colors.Color(220/255, 38/255, 38/255)
                    )
                    story.append(Paragraph(
                        f"<b>❌ ПОМИЛКА #{i}: {error.get('message', 'N/A')}</b>",
                        error_style
                    ))
                    story.append(Paragraph(
                        f"<b>Інгредієнт:</b> {error.get('ingredient', 'N/A')}",
                        normal_style
                    ))
                    
                    if error.get('current_dose'):
                        story.append(Paragraph(
                            f"<b>Поточна доза:</b> {error['current_dose']}",
                            normal_style
                        ))
                    
                    if error.get('max_allowed'):
                        story.append(Paragraph(
                            f"<b>Максимально допустимо:</b> {error['max_allowed']}",
                            normal_style
                        ))
                    
                    story.append(Paragraph(
                        f"<b>Джерело:</b> {error.get('regulatory_source', 'N/A')} (Level {error.get('level', 'N/A')})",
                        normal_style
                    ))
                    
                    story.append(Paragraph(
                        f"<b>✅ Рекомендація:</b> {error.get('recommendation', 'N/A')}",
                        normal_style
                    ))
                    
                    if error.get('penalty_amount'):
                        story.append(Paragraph(
                            f"<b>💰 Штраф:</b> {error['penalty_amount']:,} грн",
                            normal_style
                        ))
                    
                    story.append(Spacer(1, 16))
            
            # Warnings section
            warnings = report_data.get("warnings", [])
            if warnings:
                story.append(PageBreak())
                story.append(Paragraph("🟡 ПОПЕРЕДЖЕННЯ", heading_style))
                story.append(Spacer(1, 12))
                
                for i, warning in enumerate(warnings, 1):
                    warning_style = ParagraphStyle(
                        'Warning',
                        parent=normal_style,
                        fontSize=11,
                        fontName=self.bold_font_name,
                        textColor=colors.Color(245/255, 158/255, 11/255)
                    )
                    story.append(Paragraph(
                        f"<b>⚠️ ПОПЕРЕДЖЕННЯ #{i}: {warning.get('message', 'N/A')}</b>",
                        warning_style
                    ))
                    story.append(Paragraph(
                        f"<b>Інгредієнт:</b> {warning.get('ingredient', 'N/A')}",
                        normal_style
                    ))
                    story.append(Paragraph(
                        f"<b>✅ Рекомендація:</b> {warning.get('recommendation', 'N/A')}",
                        normal_style
                    ))
                    story.append(Spacer(1, 12))

            # Forbidden phrases section
            compliance_errors = report_data.get("compliance_errors", []) or []
            forbidden_errors = [
                error for error in compliance_errors if error.get("type") == "forbidden_phrase"
            ]

            if forbidden_errors:
                story.append(Spacer(1, 12))
                story.append(Paragraph("🚫 ЗАБОРОНЕНІ ФОРМУЛЮВАННЯ", heading_style))
                story.append(Spacer(1, 12))

                for idx, error in enumerate(forbidden_errors, 1):
                    story.append(
                        Paragraph(
                            f"❌ ЗАБОРОНЕНА ФРАЗА #{idx}: {error.get('phrase', 'N/A')}",
                            heading3_style
                        )
                    )
                    story.append(Paragraph(f"Категорія: {error.get('category', 'N/A')}", normal_style))
                    story.append(
                        Paragraph(
                            f"Джерело: {error.get('regulatory_source', 'N/A')}",
                            normal_style
                        )
                    )
                    if error.get('explanation'):
                        story.append(
                            Paragraph(
                                f"📋 Пояснення: {error.get('explanation')}",
                                normal_style
                            )
                        )
                    story.append(
                        Paragraph(
                            f"✅ Рекомендація: {error.get('recommendation', 'N/A')}",
                            normal_style
                        )
                    )
                    story.append(
                        Paragraph(
                            f"💰 Штраф: {int(error.get('penalty_amount') or 0):,} грн",
                            normal_style
                        )
                    )
                    story.append(Spacer(1, 12))

            # Missing mandatory fields section
            missing_fields = [
                error for error in compliance_errors if error.get("type") == "mandatory_field"
            ]

            if missing_fields:
                story.append(Spacer(1, 12))
                story.append(Paragraph("📋 ВІДСУТНІ ОБОВ'ЯЗКОВІ ПОЛЯ", heading_style))
                story.append(Spacer(1, 12))

                for idx, error in enumerate(missing_fields, 1):
                    story.append(
                        Paragraph(
                            f"❌ ПОЛЕ #{idx}: {error.get('field_name', 'N/A')}",
                            heading3_style
                        )
                    )
                    story.append(
                        Paragraph(
                            f"Джерело: {error.get('regulatory_source', 'N/A')}",
                            normal_style
                        )
                    )
                    if error.get('article_number'):
                        story.append(
                            Paragraph(
                                f"Стаття: {error.get('article_number')}",
                                normal_style
                            )
                        )
                    story.append(
                        Paragraph(
                            f"📋 Помилка: {error.get('error_message', 'N/A')}",
                            normal_style
                        )
                    )
                    story.append(
                        Paragraph(
                            f"✅ Рекомендація: {error.get('recommendation', 'N/A')}",
                            normal_style
                        )
                    )
                    story.append(
                        Paragraph(
                            f"💰 Штраф: {int(error.get('penalty_amount') or 0):,} грн",
                            normal_style
                        )
                    )
                    story.append(Spacer(1, 12))

            # Summary section
            story.append(Spacer(1, 24))
            story.append(Paragraph("📊 ПІДСУМОК", heading_style))
            story.append(
                Paragraph(
                    f"Помилки дозування: {stats.get('total_dosage_errors', 0)}",
                    normal_style
                )
            )
            story.append(
                Paragraph(
                    f"Заборонені фрази: {stats.get('total_forbidden_phrases', 0)}",
                    normal_style
                )
            )
            story.append(
                Paragraph(
                    f"Відсутні поля: {stats.get('total_missing_fields', 0)}",
                    normal_style
                )
            )
            story.append(
                Paragraph(
                    f"💰 Загальні штрафи: {int(penalties.get('total_amount') or 0):,} {penalties.get('currency', 'UAH')}",
                    heading3_style
                )
            )
            
            # Regulatory acts
            story.append(Spacer(1, 24))
            story.append(Paragraph("📋 НОРМАТИВНА БАЗА", heading_style))
            story.append(Paragraph(
                "Під час перевірки використані такі нормативні акти:",
                normal_style
            ))
            story.append(Spacer(1, 12))
            
            acts = [
                "📜 Закон України №4122-IX від 05.12.2024",
                "📜 Закон України №2639-VIII від 06.12.2018",
                "📜 Закон України №771/97-ВР від 23.12.1997",
                "📜 Наказ МОЗ України №1114 від 19.12.2013",
            ]
            
            for act in acts:
                story.append(Paragraph(act, normal_style))
            
            # Disclaimer
            story.append(Spacer(1, 24))
            story.append(Paragraph("ДИСКЛЕЙМЕР", heading_style))
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=normal_style,
                fontSize=9,
                textColor=colors.Color(100/255, 116/255, 139/255)
            )
            story.append(Paragraph(
                "Цей звіт створено автоматично системою LabelCheck UA з використанням "
                "штучного інтелекту Claude на основі аналізу поточного законодавства України. "
                "Звіт є помічником та рекомендаційним інструментом. Перед остаточним використанням "
                "етикетки рекомендуємо додаткову перевірку кваліфікованим експертом.",
                disclaimer_style
            ))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}", exc_info=True)
            raise

