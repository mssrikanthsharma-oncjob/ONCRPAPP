"""PDF generation service for customer reports."""
import json
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.models import CustomerEnquiry


class PDFReportService:
    """Service for generating PDF reports."""
    
    @staticmethod
    def generate_customer_report(customer_id, enquiry_ids=None, report_type='comprehensive'):
        """Generate PDF report for customer enquiries."""
        if not REPORTLAB_AVAILABLE:
            return None, "PDF generation not available in this environment. Please contact support."
        
        try:
            # Get customer enquiries
            query = CustomerEnquiry.query.filter_by(customer_id=customer_id)
            
            if enquiry_ids:
                query = query.filter(CustomerEnquiry.id.in_(enquiry_ids))
            
            if report_type == 'search-only':
                query = query.filter_by(enquiry_type='search')
            elif report_type == 'advice-only':
                query = query.filter_by(enquiry_type='advice')
            
            enquiries = query.order_by(CustomerEnquiry.created_at.desc()).all()
            
            if not enquiries:
                return None, "No enquiries found for report generation."
            
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#667eea')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.HexColor('#333333')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                alignment=TA_JUSTIFY
            )
            
            # Build PDF content
            story = []
            
            # Title
            story.append(Paragraph("ONC REALTY PARTNERS", title_style))
            story.append(Paragraph("Property Search & Advisory Report", heading_style))
            story.append(Spacer(1, 20))
            
            # Report metadata
            customer = enquiries[0].customer if enquiries else None
            story.append(Paragraph(f"<b>Generated for:</b> {customer.username if customer else 'Customer'}", normal_style))
            story.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
            story.append(Paragraph(f"<b>Report Type:</b> {report_type.replace('-', ' ').title()}", normal_style))
            story.append(Spacer(1, 20))
            
            # Summary statistics
            search_count = len([e for e in enquiries if e.enquiry_type == 'search'])
            advice_count = len([e for e in enquiries if e.enquiry_type == 'advice'])
            
            story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
            summary_data = [
                ['Total Enquiries', str(len(enquiries))],
                ['Property Searches', str(search_count)],
                ['Advisory Sessions', str(advice_count)],
                ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 30))
            
            # Detailed enquiries
            story.append(Paragraph("DETAILED ENQUIRY REPORT", heading_style))
            story.append(Spacer(1, 12))
            
            for i, enquiry in enumerate(enquiries, 1):
                # Enquiry header
                story.append(Paragraph(f"{i}. ENQUIRY #{enquiry.id} - {enquiry.enquiry_type.upper()}", 
                                     ParagraphStyle('EnquiryHeader', parent=styles['Heading3'], 
                                                  fontSize=14, textColor=colors.HexColor('#667eea'))))
                
                story.append(Paragraph(f"<b>Date:</b> {enquiry.created_at.strftime('%B %d, %Y at %I:%M %p')}", normal_style))
                story.append(Paragraph(f"<b>Type:</b> {enquiry.enquiry_type.title()}", normal_style))
                
                if enquiry.enquiry_type == 'search':
                    # Property search details
                    if enquiry.search_criteria:
                        try:
                            criteria = json.loads(enquiry.search_criteria)
                            story.append(Paragraph("<b>Search Criteria:</b>", normal_style))
                            
                            criteria_data = []
                            if criteria.get('location'):
                                criteria_data.append(['Location', criteria['location']])
                            if criteria.get('property_type'):
                                criteria_data.append(['Property Type', criteria['property_type']])
                            if criteria.get('budget_min'):
                                criteria_data.append(['Min Budget', f"₹{criteria['budget_min']:,}"])
                            if criteria.get('budget_max'):
                                criteria_data.append(['Max Budget', f"₹{criteria['budget_max']:,}"])
                            
                            if criteria_data:
                                criteria_table = Table(criteria_data, colWidths=[1.5*inch, 3*inch])
                                criteria_table.setStyle(TableStyle([
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                                ]))
                                story.append(criteria_table)
                        except:
                            story.append(Paragraph("Search criteria data not available", normal_style))
                
                elif enquiry.enquiry_type == 'advice':
                    # Advisory details
                    if enquiry.advice_request:
                        story.append(Paragraph("<b>Customer Request:</b>", normal_style))
                        story.append(Paragraph(enquiry.advice_request, normal_style))
                    
                    if enquiry.llm_response:
                        story.append(Paragraph("<b>Our Advisory:</b>", normal_style))
                        # Clean up the LLM response for PDF
                        clean_response = enquiry.llm_response.replace('\n\n', '<br/><br/>')
                        story.append(Paragraph(clean_response, normal_style))
                
                story.append(Spacer(1, 20))
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph("RECOMMENDATIONS", heading_style))
            recommendations = """
            Based on your enquiries, here are our key recommendations:
            
            1. <b>Continue Research:</b> Keep exploring properties in your preferred locations and stay updated with market trends.
            
            2. <b>Professional Consultation:</b> Consider scheduling a detailed consultation with our real estate experts for personalized guidance.
            
            3. <b>Financial Planning:</b> Ensure you have adequate funds not just for the property cost but also for registration, taxes, and maintenance.
            
            4. <b>Legal Verification:</b> Always verify all legal documents, RERA registration, and clear title before making any purchase decisions.
            
            5. <b>Market Timing:</b> Stay informed about market conditions and interest rates to make well-timed investment decisions.
            """
            story.append(Paragraph(recommendations, normal_style))
            
            story.append(Spacer(1, 30))
            story.append(Paragraph("Thank you for choosing ONC REALTY PARTNERS for your property needs.", 
                                 ParagraphStyle('Footer', parent=styles['Normal'], 
                                              fontSize=10, alignment=TA_CENTER, 
                                              textColor=colors.HexColor('#666666'))))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data, None
            
        except Exception as e:
            return None, f"Error generating PDF report: {str(e)}"
    
    @staticmethod
    def get_report_filename(customer_username, report_type='comprehensive'):
        """Generate appropriate filename for the report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"ONC_Property_Report_{customer_username}_{report_type}_{timestamp}.pdf"